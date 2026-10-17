"""script.json の post_time(日本時間)まで待つ。すでに過ぎていればすぐ終了。"""
import datetime, json, sys, time
from zoneinfo import ZoneInfo
s = json.load(open(sys.argv[1], encoding="utf-8"))
now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
h, m = map(int, s["post_time"].split(":"))
target = now.replace(hour=h, minute=m, second=0, microsecond=0)
wait = (target - now).total_seconds()
print(f"now {now:%H:%M} -> post at {s['post_time']} (wait {max(0, wait):.0f}s)")
if wait > 0:
    time.sleep(wait)
