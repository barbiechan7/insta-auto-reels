"""週次レポート: 直近7日の投稿の再生数(ビュー)・リーチ、アーカイブ候補(投稿から5日以上で1万ビュー未満)をSlackに送る。"""
import csv, datetime, os, sys, requests
from zoneinfo import ZoneInfo
import notify

G = os.environ.get("IG_API_BASE", "https://graph.instagram.com/v21.0")
TOK = os.environ["IG_ACCESS_TOKEN"]
JST = ZoneInfo("Asia/Tokyo")

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

def fmt(n): return "-" if n is None else (f"{n/10000:.1f}万" if n >= 10000 else str(n))

def main():
    now = datetime.datetime.now(JST)
    media, url = [], f"me/media"
    d = get(url, fields="id,caption,timestamp,media_product_type,permalink", limit=100)
    if "error" in d: notify.send(f":warning: 週次レポートを作れませんでした(Instagram APIエラー): {d['error']}"); sys.exit(1)
    media = [m for m in d.get("data", []) if m.get("media_product_type") == "REELS"]
    names = titles()
    rows = []
    for m in media:
        ts = datetime.datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")).astimezone(JST)
        rows.append({"ts": ts, "views": metric(m["id"], "views"), "reach": metric(m["id"], "reach"),
                     "title": names.get(m["id"]) or (m.get("caption") or "").split("\n")[0][:20] or m["permalink"], "link": m["permalink"]})
    week = [r for r in rows if (now - r["ts"]).days < 7]
    lines = [f":bar_chart: *週次レポート* ({now:%m/%d})  直近7日の投稿 {len(week)}本"]
    tv = sum(r["views"] or 0 for r in week)
    lines.append(f"合計ビュー *{fmt(tv)}* / 1本あたり平均 {fmt(tv // len(week)) if week else '-'}")
    for r in sorted(week, key=lambda r: -(r["views"] or 0)):
        lines.append(f"• {r['ts']:%m/%d %H:%M} 「{r['title']}」 ビュー {fmt(r['views'])} / リーチ {fmt(r['reach'])}")
    cand = [r for r in rows if (now - r["ts"]).days >= 5 and (r["views"] or 0) < 10000 and r["views"] is not None]
    lines.append(f"\n:file_cabinet: *アーカイブ候補*(投稿から5日以上で1万ビュー未満) {len(cand)}本")
    for r in sorted(cand, key=lambda r: r["views"])[:15]:
        lines.append(f"• {r['ts']:%m/%d} 「{r['title']}」 {fmt(r['views'])}  {r['link']}")
    if len(cand) > 15: lines.append(f"…ほか{len(cand) - 15}本")
    notify.send("\n".join(lines))

if __name__ == "__main__":
    main()
