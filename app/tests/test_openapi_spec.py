"""The checked-in spec the client's types are generated from (client/generated/openapi.json) is the one the app
serves. The other link, spec -> client/generated/schema.d.ts, is the client job in .github/workflows/ci.yml."""
import json
from pathlib import Path

from ashfall_app.main import create_app

SPEC = Path(__file__).resolve().parent.parent / "client" / "generated" / "openapi.json"
REGEN = ("regenerate (in app/): python -c 'import json, pathlib; from ashfall_app.main import create_app; "
         "pathlib.Path(\"client/generated/openapi.json\").write_text(json.dumps(create_app().openapi(), indent=2, "
         "ensure_ascii=False) + \"\\n\")', then in client/: npm run types (stdout carries the app's log lines)")


def test_checked_in_spec_matches_app() -> None:
    served = create_app().openapi()
    assert "/api/saves/{save_id}/decisions" in served["paths"]   # control: the game's routes are in what is compared
    assert SPEC.exists(), REGEN
    assert json.loads(SPEC.read_text()) == served, REGEN
