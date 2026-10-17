"""定期レポートをSlack/LINEに送る。
  月曜: 1週間の振り返り(合計・前週比・ベスト/ワースト・アーカイブ候補)
  水・金: 前回のレポート以降の投稿と、直近の投稿がどのぐらい伸びたか
前回レポート時点のビュー数は data/views_snapshot.json に保存し、増加分を出す。MODE=monday|midweek で強制指定できる。"""
import csv, datetime, json, os, sys, requests
from zoneinfo import ZoneInfo
import notify

G = os.environ.get("IG_API_BASE", "https://graph.instagram.com/v21.0")
TOK = os.environ["IG_ACCESS_TOKEN"]
JST = ZoneInfo("Asia/Tokyo")
SNAP = "data/views_snapshot.json"
BASELINE = 54500   # 『生まれた日』シリーズの過去ビュー中央値(仮説ログの判定基準)

def get(path, **params):
    r = requests.get(f"{G}/{path}", params={**params, "access_token": TOK}, timeout=30)
    return r.json() if r.ok else {"error": r.text[:200]}

def titles():
    t = {}
    if os.path.exists("data/daily_log.csv"):
        for row in csv.reader(open("data/daily_log.csv", encoding="utf-8")):
            if len(row) >= 5 and row[4]: t[row[4]] = row[1]
    return t

def metric(mid, name):
    d = get(f"{mid}/insights", metric=name)
    try: return d["data"][0]["values"][0]["value"]
    except Exception: return None

def fmt(n): return "-" if n is None else (f"{n/10000:.1f}万" if n >= 10000 else f"{n:,}")

def main():
    now = datetime.datetime.now(JST)
    mode = os.environ.get("MODE") or ("monday" if now.weekday() == 0 else "midweek")
    d = get("me/media", fields="id,caption,timestamp,media_product_type,permalink", limit=100)
    if "error" in d:
        notify.send(f":warning: レポートを作れませんでした(Instagram APIエラー): {d['error']}"); sys.exit(1)
    names = titles()
    snap = json.load(open(SNAP, encoding="utf-8")) if os.path.exists(SNAP) else {}
    last_at = datetime.datetime.fromisoformat(snap["_at"]) if "_at" in snap else now - datetime.timedelta(days=7)
    rows = []
    for m in d.get("data", []):
        if m.get("media_product_type") != "REELS": continue
        ts = datetime.datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).astimezone(JST)
        v = metric(m["id"], "views")
        rows.append({"id": m["id"], "ts": ts, "views": v, "reach": metric(m["id"], "reach"), "link": m["permalink"],
                     "title": names.get(m["id"]) or (m.get("caption") or "").split("\n")[0][:18] or m["permalink"],
                     "delta": None if m["id"] not in snap or v is None else v - snap[m["id"]]})
    age = lambda r: (now - r["ts"]).total_seconds() / 86400
    line = lambda r: f"• {r['ts']:%m/%d %H:%M} 「{r['title']}」 {fmt(r['views'])}ビュー" + (f"(+{fmt(r['delta'])})" if r["delta"] else "") + f" / リーチ {fmt(r['reach'])}"
    out = []
    if mode == "monday":
        week = [r for r in rows if age(r) < 7]
        prev = [r for r in rows if 7 <= age(r) < 14]
        tv, pv = sum(r["views"] or 0 for r in week), sum(r["views"] or 0 for r in prev)
        diff = f"(前週 {fmt(pv)} → {'+' if tv >= pv else ''}{fmt(tv - pv)})" if prev else ""
        out.append(f":bar_chart: *1週間の振り返り* ({now:%m/%d})")
        out.append(f"直近7日の投稿 {len(week)}本 / 合計 *{fmt(tv)}ビュー* {diff} / 1本平均 {fmt(tv // len(week)) if week else '-'}")
        ranked = sorted([r for r in week if r["views"] is not None], key=lambda r: -r["views"])
        if ranked:
            hit = sum(1 for r in ranked if r["views"] >= BASELINE)
            out.append(f"過去の中央値({fmt(BASELINE)})を超えた投稿: {hit}/{len(ranked)}本")
            out.append("\n*ベスト3*"); out += [line(r) for r in ranked[:3]]
            out.append("*ワースト3*"); out += [line(r) for r in ranked[-3:][::-1]]
        cand = sorted([r for r in rows if age(r) >= 5 and r["views"] is not None and r["views"] < 10000], key=lambda r: r["views"])
        out.append(f"\n:file_cabinet: *アーカイブ候補*(5日以上で1万ビュー未満) {len(cand)}本")
        out += [f"• {r['ts']:%m/%d} 「{r['title']}」 {fmt(r['views'])}  {r['link']}" for r in cand[:10]]
        if len(cand) > 10: out.append(f"…ほか{len(cand) - 10}本")
    else:
        new = [r for r in rows if r["ts"] > last_at]
        recent = [r for r in rows if age(r) < 7 and r["ts"] <= last_at]
        out.append(f":bar_chart: *投稿状況* ({now:%m/%d %H:%M}時点)")
        out.append(f"前回のレポート以降の新しい投稿: {len(new)}本")
        out += [line(r) for r in sorted(new, key=lambda r: r["ts"])] or ["(なし)"]
        out.append("\n*直近7日の投稿の伸び*(カッコは前回からの増加)")
        out += [line(r) for r in sorted(recent, key=lambda r: r["ts"], reverse=True)] or ["(なし)"]
    notify.send("\n".join(out))
    snap = {r["id"]: r["views"] for r in rows if r["views"] is not None}
    snap["_at"] = now.isoformat()
    json.dump(snap, open(SNAP, "w", encoding="utf-8"))

if __name__ == "__main__":
    main()
