#!/usr/bin/env python3
"""Export the FastAPI OpenAPI schema to webapp/openapi.json.

Run this whenever the API request/response models change. The frontend's
TypeScript types are generated from the emitted file (see the webapp's
``gen:api`` npm script). No running server is required.

Usage (from the project root, with the backend deps importable):
    python3 scripts/export_openapi.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.main import app  # noqa: E402  (import after sys.path tweak)


def main() -> None:
    out_path = ROOT / "webapp" / "openapi.json"
    schema = app.openapi()
    out_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)} ({len(schema.get('paths', {}))} paths)")


if __name__ == "__main__":
    main()
