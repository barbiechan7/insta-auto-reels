"""Facebookページに、同じ動画を投稿する。FB_PAGE_TOKEN / FB_PAGE_ID が未設定なら、何もせず終了する(Instagram投稿には影響しない)。
使い方: python post_fb.py <動画URL> <script.json>"""
import json, os, sys, requests

def main(video_url, script_path):
    token, page = os.environ.get("FB_PAGE_TOKEN"), os.environ.get("FB_PAGE_ID")
    if not token or not page:
        print("skip: FB_PAGE_TOKEN / FB_PAGE_ID が未設定"); return
    s = json.load(open(script_path, encoding="utf-8"))
    desc = s["caption"] + "\n\n" + " ".join(s["hashtags"])
    video = requests.get(video_url, timeout=300); video.raise_for_status()   # URL渡しは失敗することがあるので、ファイルを取ってきて直接アップロードする
    r = requests.post(f"https://graph.facebook.com/v21.0/{page}/videos",
                      data={"description": desc, "title": s["theme"], "access_token": token},
                      files={"source": ("reel.mp4", video.content, "video/mp4")}, timeout=600)
    print(r.status_code, r.text[:1500])
    r.raise_for_status()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
