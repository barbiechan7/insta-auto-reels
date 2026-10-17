"""今日の台本を用意する。queue/今日の日付.json があればそれを使い、なければClaude APIで生成。
投稿時刻(post_time)が未設定なら、20:05〜20:55の5分刻みから日ごとにずらして決める(連日で同じ時刻にならない)。"""
import datetime, json, os, shutil, sys
from zoneinfo import ZoneInfo
import generate

def slot_for(date):
    return f"20:{5 + 5 * ((date.toordinal() * 7) % 11):02d}"   # 7と11は互いに素 → 連日で必ず別の時刻

def main(out):
    today = datetime.datetime.now(ZoneInfo("Asia/Tokyo")).date()
    q = f"queue/{today.isoformat()}.json"
    if os.path.exists(q):
        shutil.copy(q, out)
        hist = json.load(open(generate.HIST, encoding="utf-8")) if os.path.exists(generate.HIST) else []
        hist.append({"date": today.isoformat(), "theme": json.load(open(q, encoding="utf-8"))["theme"]})
        json.dump(hist[-100:], open(generate.HIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        generate.main(out)
    s = json.load(open(out, encoding="utf-8"))
    s.setdefault("post_time", slot_for(today))
    json.dump(s, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("post_time:", s["post_time"])

if __name__ == "__main__":
    main(sys.argv[1])
