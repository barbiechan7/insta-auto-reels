"""投稿はせず、トークンとIDが有効かだけ確認する(トークンは表示しない)。"""
import os, sys, requests
G = os.environ.get("IG_API_BASE", "https://graph.instagram.com/v21.0")
uid, tok = os.environ.get("IG_USER_ID", ""), os.environ.get("IG_ACCESS_TOKEN", "")
if not uid or not tok: sys.exit("IG_USER_ID / IG_ACCESS_TOKEN が未登録です")
r = requests.get(f"{G}/me", params={"fields": "user_id,username,account_type", "access_token": tok}, timeout=30)
print("status", r.status_code, r.json() if r.status_code != 200 else {k: v for k, v in r.json().items()})
if r.status_code != 200: sys.exit("トークンが無効です")
me = r.json()
print("IG_USER_ID が一致:", str(me.get("user_id") or me.get("id")) == uid.strip())
