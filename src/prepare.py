"""今回の投稿の台本を用意する(1日2本: 昼 12:00-13:00 / 夜 20:00-21:00)。
queue/日付-noon.json・日付-eve.json があればそれを使い、なければClaude APIで生成。
投稿時刻は、枠の中から1分単位でランダムに決める(日付と枠から決まるので、同じ回で再実行しても同じ時刻)。"""
import datetime, json, os, random, shutil, sys
from zoneinfo import ZoneInfo
import generate

HOURS = {"noon": 12, "eve": 20}

def current_slot(now):
    return os.environ.get("SLOT") or ("noon" if now.hour < 16 else "eve")

def random_time(date, slot):
    minute = random.Random(f"{date.isoformat()}-{slot}").randrange(0, 60)
    return f"{HOURS[slot]}:{minute:02d}"

def main(out):
    now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
    today, slot = now.date(), current_slot(now)
    q = f"queue/{today.isoformat()}-{slot}.json"
    if os.path.exists(q):
        shutil.copy(q, out)
        hist = json.load(open(generate.HIST, encoding="utf-8")) if os.path.exists(generate.HIST) else []
        hist.append({"date": today.isoformat(), "slot": slot, "theme": json.load(open(q, encoding="utf-8"))["theme"]})
        json.dump(hist[-100:], open(generate.HIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        generate.main(out)
    s = json.load(open(out, encoding="utf-8"))
    s["post_time"] = random_time(today, slot)
    s["slot"] = slot
    json.dump(s, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("slot:", slot, "post_time:", s["post_time"])

if __name__ == "__main__":
    main(sys.argv[1])
