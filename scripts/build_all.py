# scripts/build_all.py
import json, pathlib, re
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_TXT = ROOT / "scripts" / "sources" / "codes_all.txt"
OUT_ALL = ROOT / "api" / "rankings" / "all.json"
OUT_ISL = ROOT / "api" / "islands"
OUT_ALL.parent.mkdir(parents=True, exist_ok=True)
OUT_ISL.mkdir(parents=True, exist_ok=True)

CODE_RE = re.compile(r"\b\d{4}-\d{4}-\d{4}\b")

def now_utc():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def read_codes(path: pathlib.Path, limit: int = 200):
    seen, ordered = set(), []
    if not path.exists():
        raise FileNotFoundError(f"codes file not found: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = CODE_RE.search(raw)
        if not m:
            continue
        code = m.group(0)
        if code in seen:
            continue
        seen.add(code)
        ordered.append(code)
        if len(ordered) >= limit:
            break
    return ordered

def load_all():
    if OUT_ALL.exists():
        try:
            return json.loads(OUT_ALL.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"category": "all", "source": "fortnitegg(seed-list)", "updated_at": now_utc(), "items": []}

def save_json(path: pathlib.Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def ensure_island_json(code: str, title=None, author=None, thumb_url=None):
    p = OUT_ISL / f"{code}.json"
    if p.exists():
        # 最低限 updated_at のみ更新
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            data = {}
    else:
        data = {"code": code}
    data.setdefault("title", title)
    data.setdefault("author", author)
    data.setdefault("thumb_url", thumb_url)
    data.setdefault("source", "fortnitegg(seed-list)")
    data["updated_at"] = now_utc()
    save_json(p, data)

def merge_codes_into_all(existing_items: list, codes: list):
    # 既存itemsをcodeで辞書化（既存情報は保持）
    by_code = {it.get("code"): dict(it) for it in existing_items if it.get("code")}
    # 新リスト順 = rank の基準
    for pos, code in enumerate(codes, start=1):
        cur = by_code.get(code, {})
        if not cur:
            cur = {"code": code, "discovered_at": now_utc()}
        # title/author/thumb_url は後で enrich 予定なので既存があれば温存
        cur.setdefault("title", None)
        cur.setdefault("author", None)
        cur.setdefault("thumb_url", None)
        cur["rank"] = pos
        by_code[code] = cur
        # 各島の最小JSONも用意（初回生成）
        ensure_island_json(code, cur.get("title"), cur.get("author"), cur.get("thumb_url"))
    # ランク順の配列に戻す（codes の順序を厳守）
    merged = [by_code[c] for c in codes]
    return merged

def main():
    codes = read_codes(SRC_TXT, limit=200)
    data = load_all()
    prev_items = data.get("items") or []
    merged = merge_codes_into_all(prev_items, codes)
    out = {
        "category": "all",
        "source": "fortnitegg(seed-list)",
        "updated_at": now_utc(),
        "items": merged,
    }
    before = json.dumps(data, ensure_ascii=False, sort_keys=True)
    after  = json.dumps(out,  ensure_ascii=False, sort_keys=True)
    if before == after:
        print(f"no changes | codes={len(codes)} items={len(merged)}")
        return
    save_json(OUT_ALL, out)
    print(f"updated all.json | codes={len(codes)} items={len(merged)}")

if __name__ == "__main__":
    main()
