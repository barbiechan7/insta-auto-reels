"""Slackに通知する。SLACK_WEBHOOK_URL が未設定なら画面に表示するだけ。使い方: notify.py "本文" """
import os, sys, requests

def send(text):
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        print("[Slack未設定] " + text); return False
    r = requests.post(url, json={"text": text}, timeout=20)
    print("slack:", r.status_code)
    return r.ok

if __name__ == "__main__":
    send(sys.argv[1])
