"""全リールの指標(閲覧・リーチ・いいね・コメント・シェア・保存・平均視聴時間)を取得してログに出す。"""
import os, json, requests
G = os.environ.get("IG_API_BASE", "https://graph.instagram.com/v21.0"); TOK = os.environ["IG_ACCESS_TOKEN"]
def get(path, **p):
    r = requests.get(f"{G}/{path}", params={**p, "access_token": TOK}, timeout=30); return r.json() if r.ok else {"error": r.text[:150]}
media, url = [], None
d = get("me/media", fields="id,timestamp,media_product_type,caption", limit=100)
media += d.get("data", [])
rows = []
for m in media:
    if m.get("media_product_type") != "REELS": continue
    ins = get(f"{m['id']}/insights", metric="views,reach,likes,comments,shares,saved,ig_reels_avg_watch_time,ig_reels_video_view_total_time")
    vals = {x["name"]: x["values"][0]["value"] for x in ins.get("data", [])} if "data" in ins else {"err": ins.get("error")}
    rows.append({"id": m["id"], "t": m["timestamp"], "cap": (m.get("caption") or "")[:12], **vals})
print("ROWS_BEGIN"); [print(json.dumps(r, ensure_ascii=False)) for r in rows]; print("ROWS_END")
