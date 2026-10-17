"""Instagram Graph APIでリール投稿。使い方: post.py <video_url> <script.json> [cover_url]"""
import json, os, sys, time, requests
G = os.environ.get("IG_API_BASE", "https://graph.instagram.com/v21.0")   # Instagramログイン方式のトークン用。Facebookログイン方式なら IG_API_BASE=https://graph.facebook.com/v21.0

def main(video_url, script_path, cover_url=None):
    s = json.load(open(script_path, encoding="utf-8"))
    caption = s["caption"] + "\n\n" + " ".join(s["hashtags"])
    uid, tok = os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]
    data = {"media_type": "REELS", "video_url": video_url, "caption": caption, "access_token": tok}
    if cover_url: data["cover_url"] = cover_url   # サムネイル(カバー画像)
    r = requests.post(f"{G}/{uid}/media", data=data, timeout=60)
    r.raise_for_status(); cid = r.json()["id"]
    for _ in range(40):
        st = requests.get(f"{G}/{cid}", params={"fields": "status_code", "access_token": tok}, timeout=30).json()
        if st.get("status_code") == "FINISHED": break
        if st.get("status_code") == "ERROR": sys.exit(f"処理失敗: {st}")
        time.sleep(10)
    r = requests.post(f"{G}/{uid}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=60)
    r.raise_for_status(); print("posted", r.json())

if __name__ == "__main__":
    main(*sys.argv[1:4])
