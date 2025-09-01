import json, pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"
(API_DIR / "rankings").mkdir(parents=True, exist_ok=True)

def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def build_dummy():
    out = {
        "category": "zonewars",
        "updated_at": now_utc(),
        "items": [
            {"rank": 1, "code": "1234-5678-9012", "title": "Dummy Map", "author": "TestUser",
             "thumb_url": "https://dummyimage.com/640x360/ccc/000.jpg&text=Dummy"}
        ]
    }
    (API_DIR/"rankings"/"zonewars.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

if __name__ == "__main__":
    build_dummy()
    print("OK: dummy JSON generated")
