"""`python -m ashfall_app.web`: the web pods' server on :8080 (web/app.py)."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("ashfall_app.web.app:create_app", factory=True, host="0.0.0.0", port=8080)
