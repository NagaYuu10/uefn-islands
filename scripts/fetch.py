# scripts/fetch.py
import json, pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "api" / "rankings" / "zonewars.json"
OUT.parent.mkdir(parents=True, exist_ok=True)


def now_utc():
  return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def seed_items():
  # 必ず最低限存在してほしいダミー3件
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


def load_existing():
  if OUT.exists():
    try:
      return json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
      pass
  return {"category": "zonewars", "updated_at": now_utc(), "items": []}


def merge_items(existing_items, seed):
  # 既存itemsを優先しつつ、seedの3件を必ず含める（codeキーでマージ）
  by_code = {it.get("code"): dict(it) for it in existing_items if it.get("code")}
  for s in seed:
    c = s.get("code")
    if not c:
      continue
    prev = by_code.get(c, {})
    merged = {**prev, **s}  # 既存があれば上書き
    by_code[c] = merged

  merged_list = list(by_code.values())

  # まず rank で並べ替え（不正 or 欠損は末尾）
  def _rank_key(it):
    r = it.get("rank")
    try:
      return int(r)
    except Exception:
      return 10**9

  merged_list.sort(key=_rank_key)

  # rank を 1..N で振り直して安定化
  for i, it in enumerate(merged_list, start=1):
    it["rank"] = i

  return merged_list


def main():
  data = load_existing()
  existing = data.get("items") or []
  seed = seed_items()
  merged = merge_items(existing, seed)

  out_data = {
    "category": "zonewars",
    "updated_at": now_utc(),
    "items": merged,
  }

  OUT.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")
  print(f"OK: zonewars.json updated | existing={len(existing)} seed={len(seed)} merged={len(merged)}")


if __name__ == "__main__":
  main()
