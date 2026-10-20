"""通知を送る。設定されている宛先すべてに送る(未設定の宛先は無視)。
  Slack: SLACK_WEBHOOK_URL
  LINE : LINE_CHANNEL_TOKEN(Messaging APIのチャネルアクセストークン) と LINE_USER_ID(通知を受け取る人のユーザーID)
使い方: notify.py "本文" """
import os, sys, requests

def to_slack(text):
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url: return None
    r = requests.post(url, json={"text": text}, timeout=20)
    print("slack:", r.status_code); return r.ok

def to_line(text):
    tok, uid = os.environ.get("LINE_CHANNEL_TOKEN", "").strip(), os.environ.get("LINE_USER_ID", "").strip()
    if not tok or not uid: return None
    plain = text.replace("*", "").replace(":bar_chart:", "📊").replace(":file_cabinet:", "🗄").replace(":rotating_light:", "🚨").replace(":warning:", "⚠️")
    r = requests.post("https://api.line.me/v2/bot/message/push",
                      headers={"Authorization": f"Bearer {tok}"},
                      json={"to": uid, "messages": [{"type": "text", "text": plain[:4900]}]}, timeout=20)
    print("line:", r.status_code, "" if r.ok else r.text[:200]); return r.ok

def send(text):
    print(text)   # 実行ログにも残す(秘密情報は含まない)
    results = [to_slack(text), to_line(text)]
    if all(r is None for r in results): print("[通知先が未設定] " + text)
    return any(results)

if __name__ == "__main__":
    send(sys.argv[1])
