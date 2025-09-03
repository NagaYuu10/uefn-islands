# scripts/fetch.py
import json, pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "api" / "rankings" / "zonewars.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def seed_items():
    return [
        {
            "rank": 1,
            "code": "1234-5678-9012",
            "title": "Dummy Map 1",
            "author": "TestUser",
            "thumb_url": "https://dummyimage.com/640x360/ccc/000.jpg&text=Dummy1",
        },
        {
            "rank": 2,
            "code": "2345-6789-0123",
            "title": "Dummy Map 2",
            "author": "TestUser",
            "thumb_url": "https://dummyimage.com/640x360/ccc/000.jpg&text=Dummy2",
        },
        {
            "rank": 3,
            "code": "3456-7890-1234",
            "title": "Dummy Map 3",
            "author": "TestUser",
            "thumb_url": "https://dummyimage.com/640x360/ccc/000.jpg&text=Dummy3",
        },
    ]

if OUT.exists():
    data = json.loads(OUT.read_text(encoding="utf-8"))
    # 既存itemsがあれば維持
    items = data.get("items") or seed_items()
else:
    items = seed_items()

data = {
    "category": "zonewars",
    "updated_at": now_utc(),
    "items": items,
}

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("OK: zonewars.json updated with", len(items), "items")
