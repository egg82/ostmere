#!/usr/bin/env bash
# render.sh script [round]  ->  <out>.png (600px, on parchment), <out>_ink.png (1200px, ink on transparent)
# <out> is $OUT if set (a script may save under another name, e.g. OUT=wolf for wolf3.py), else the script name.
set -euo pipefail
cd "$(dirname "$0")"
python3 "$1.py"
out="${OUT:-$1}"
rsvg-convert -w 1200 "$out.svg" -o "${out}_ink.png"
rsvg-convert -w 600 "$out.svg" -o "${out}_tmp600.png"
size=$(identify -format '%wx%h' "${out}_tmp600.png")   # any page height
convert -size "$size" xc:'#e6dcc6' "${out}_tmp600.png" -composite "$out.png"
rm -f "${out}_tmp600.png"
if [ -n "${2:-}" ]; then mkdir -p rounds; cp "$out.png" "rounds/${out}_r$2.png"; fi
echo rendered "$out.png" "${out}_ink.png"
