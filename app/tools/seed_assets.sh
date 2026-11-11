#!/usr/bin/env bash
# Put the kinds of asset the app serves (`art`, `journal`, `audio`: the subtrees under /assets that the client and
# contracts name; previews and research stay home) onto every site's `assets-rwx` volume and prove each arrived: per
# kind, the file count and total bytes on the target volume must equal the source's, or this exits non-zero. Other
# top-level entries on the volume are logged as a warning, not a failure.
#
#     SITES="site-a site-b" app/tools/seed_assets.sh   # every site in SITES, from $ASHFALL_ASSETS
#
# The first site is seeded from the local tree; each later site is seeded from the first site's live `web` pod, so the
# sites cannot drift. This streams `tar` out of the running pod's /assets into the seed Job's pod and checks the target
# against the counts measured in that same source pod. The run stops at the first failed site, so a later site is never
# seeded from a half-seeded first. A later site whose namespace does not exist yet is skipped with a warning.
#
# One site only: `KUBE_CONTEXT=site-b` seeds just that site from the local tree, and with FROM_CONTEXT the source is
# another site's live pod instead:
#
#     FROM_CONTEXT=site-a KUBE_CONTEXT=site-b app/tools/seed_assets.sh
#
# A local seed refuses to run when any kind already holds more files on the target than locally, since the volume
# would be overwritten by an older tree. `--dry-run` runs the preflight and `kubectl apply --dry-run=client`, and
# sends nothing (so it cannot make that comparison).
#
# The Job is the cluster repo's one manifest (JOB_MANIFEST); it is applied by hand because Flux must not run it, and its
# pod is the volume's only writer (the app mounts it read-only). Reseeding overwrites and never deletes, so a file left
# on the target that the source lacks makes the check fail. The Job is deleted on the way out.
# Env, required: SITES (kubeconfig context names, space-separated) or KUBE_CONTEXT (one site); ASHFALL_ASSETS (the
# local tree, as tools/scene/output.py) unless FROM_CONTEXT is set; JOB_MANIFEST (the cluster repo's seed Job).
# Optional: NAMESPACE (ashfall), FROM_CONTEXT (unset: local), FROM_NAMESPACE (NAMESPACE).
set -euo pipefail

ns=${NAMESPACE:-ashfall}
from=${FROM_CONTEXT:-}
from_ns=${FROM_NAMESPACE:-$ns}
assets=${ASHFALL_ASSETS:-}
manifest=${JOB_MANIFEST:?JOB_MANIFEST must name the seed-assets Job manifest in the cluster repo}
job=seed-assets
kinds=(art journal audio)
skipped_rc=3
dry=0
case "${1:-}" in
  "") ;;
  --dry-run) dry=1 ;;
  *) echo "usage: seed_assets.sh [--dry-run]" >&2; exit 2 ;;
esac

# One site only when KUBE_CONTEXT or FROM_CONTEXT names it; otherwise every site in SITES.
if [ -n "${KUBE_CONTEXT:-}" ] || [ -n "$from" ]; then
  sites=("${KUBE_CONTEXT:?KUBE_CONTEXT must name the site to seed}")
else
  read -r -a sites <<<"${SITES:?SITES (or KUBE_CONTEXT) must name the sites to seed}"
fi
ctx=${sites[0]}

kube() { kubectl --context "$ctx" -n "$ns" "$@"; }
kube_from() { kubectl --context "$from" -n "$from_ns" "$@"; }
log() { echo "ts=$(date -u +%Y-%m-%dT%H:%M:%SZ) tool=seed_assets context=$ctx namespace=$ns ${from:+from=$from }$*"; }
die() { log "event=failed reason=\"$*\" duration_s=$SECONDS"; exit 1; }

# Run in a pod's shell as `sh -c "$probe" _ <volume root> <kinds...>`: "tree <kind> <files> <bytes>" or "absent <kind>"
# per kind, then "top <name>" per top-level entry.
# shellcheck disable=SC2016  # the program is for the pod's shell
probe='
  root=$1; shift
  for d in "$@"; do
    if [ -d "$root/$d" ]; then
      echo "tree $d $(find "$root/$d" -type f | wc -l) $(find "$root/$d" -type f -exec wc -c {} + | awk "\$2 != \"total\" {s+=\$1} END{print s+0}")"
    else
      echo "absent $d"
    fi
  done
  for e in $(ls -A "$root"); do echo "top $e"; done'

# Seed the site in $ctx from $from (or the local tree when $from is empty). Runs in a subshell: exits 1 on failure,
# $skipped_rc when the namespace does not exist and $allow_skip is set.
seed_site() {
  local out c measured contexts src_pod source_desc have remote kind name f b rfiles rbytes bad files=0 bytes=0 t
  local -A want_files want_bytes seen
  local -a trees=()

  command -v kubectl >/dev/null || die "kubectl not on PATH"
  contexts=$(kubectl config get-contexts -o name)
  for c in $ctx $from; do grep -Fx -- "$c" <<<"$contexts" >/dev/null || die "no kubeconfig context $c"; done
  [ -f "$manifest" ] || die "job manifest missing: $manifest"
  if ! out=$(kube get namespace "$ns" 2>&1); then
    if [ -n "$allow_skip" ] && grep -F NotFound <<<"$out" >/dev/null; then
      log "event=warn skipped=namespace_missing duration_s=$SECONDS"
      exit "$skipped_rc"
    fi
    die "cluster unreachable or no namespace $ns"
  fi

  if [ -n "$from" ]; then
    src_pod=$(kube_from get pods -l app.kubernetes.io/component=web -o name | head -n 1)
    [ -n "$src_pod" ] || die "no running web pod in $from/$from_ns to read /assets from"
    source_desc="pod=$src_pod"
    measured=$(kube_from exec "$src_pod" -- sh -c "$probe" _ /assets "${kinds[@]}") || die "could not read the source volume"
    while read -r kind name f b; do
      [ "$kind" = tree ] || continue
      want_files[$name]=$f want_bytes[$name]=$b trees+=("$name")
    done <<<"$measured"
    [ "${#trees[@]}" -gt 0 ] || die "none of ${kinds[*]} on the source volume"
  else
    [ -n "$assets" ] || die "ASHFALL_ASSETS is not set"
    [ -d "$assets" ] || die "assets dir missing: $assets"
    source_desc="assets=$assets"
    for t in "${kinds[@]}"; do
      [ -d "$assets/$t" ] || continue
      want_files[$t]=$(find "$assets/$t" -type f | wc -l)
      want_bytes[$t]=$(find "$assets/$t" -type f -printf '%s\n' | awk '{s+=$1} END{print s+0}')
      trees+=("$t")
    done
    [ "${#trees[@]}" -gt 0 ] || die "none of ${kinds[*]} under $assets"
  fi
  for t in "${trees[@]}"; do
    [ "${want_files[$t]}" -gt 0 ] || die "$t/ has no files"
    files=$((files + want_files[$t])) bytes=$((bytes + want_bytes[$t]))
  done

  log "event=start $source_desc trees=${trees[*]} files=$files bytes=$bytes dry_run=$dry"
  if [ "$dry" = 1 ]; then
    kube apply --dry-run=client -f "$manifest" >/dev/null || die "manifest does not apply"
    log "event=finish dry_run=1 duration_s=$SECONDS"
    return 0
  fi

  trap 'kube delete job "$job" --ignore-not-found --wait=false >/dev/null 2>&1 || true' EXIT
  kube delete job "$job" --ignore-not-found --wait=true >/dev/null
  kube apply -f "$manifest" >/dev/null
  kube wait --for=condition=Ready pod -l "job-name=$job" --timeout=120s >/dev/null || die "pod never became ready"

  if [ -z "$from" ]; then
    have=$(kube exec "job/$job" -- sh -c "$probe" _ /to "${kinds[@]}") || die "could not read the target volume"
    while read -r kind name f _; do
      [ "$kind" = tree ] || continue
      log "event=preflight kind=$name volume_files=$f local_files=${want_files[$name]:-0}"
      [ "$f" -le "${want_files[$name]:-0}" ] || die "refusing to downgrade: $name/ holds $f files on the volume, the local tree has ${want_files[$name]:-0}; seed from the live site with FROM_CONTEXT"
    done <<<"$have"
    tar -C "$assets" -cf - "${trees[@]}" | kube exec -i "job/$job" -- tar -C /to -xf - || die "copy failed"
  else
    kube_from exec "$src_pod" -- tar -C /assets -cf - "${trees[@]}" | kube exec -i "job/$job" -- tar -C /to -xf - || die "copy failed"
  fi

  remote=$(kube exec "job/$job" -- sh -c "$probe" _ /to "${trees[@]}") || die "could not read the volume"
  bad=0
  while read -r kind name rfiles rbytes; do
    case "$kind" in
      top) [ -n "${want_files[$name]:-}" ] || log "event=warn extra_top_level_entry=$name" ;;
      tree)
        seen[$name]=1
        log "event=verify tree=$name source_files=${want_files[$name]} source_bytes=${want_bytes[$name]} volume_files=$rfiles volume_bytes=$rbytes"
        [ "$rfiles" = "${want_files[$name]}" ] && [ "$rbytes" = "${want_bytes[$name]}" ] || bad=$((bad + 1)) ;;
    esac
  done <<<"$remote"
  for t in "${trees[@]}"; do [ -n "${seen[$t]:-}" ] || bad=$((bad + 1)); done
  [ "$bad" = 0 ] || die "$bad subtree(s) do not match the source"

  kube exec "job/$job" -- touch /tmp/done
  kube wait --for=condition=Complete "job/$job" --timeout=120s >/dev/null || die "job did not complete"
  log "event=finish files=$files bytes=$bytes duration_s=$SECONDS"
}

first=$ctx
allow_skip=
for site in "${sites[@]}"; do
  ctx=$site
  if [ "${#sites[@]}" -gt 1 ] && [ "$site" != "$first" ]; then from=$first allow_skip=1; fi
  set +e
  ( seed_site )
  rc=$?
  set -e
  case "$rc" in
    0) log "event=site_result result=ok" ;;
    "$skipped_rc") log "event=site_result result=skipped" ;;
    *) log "event=site_result result=failed rc=$rc"; exit 1 ;;
  esac
done
