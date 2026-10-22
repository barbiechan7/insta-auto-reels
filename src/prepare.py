"""今回の投稿の台本を用意する(1日2本: 昼 12:00-13:00 / 夜 20:00-21:00)。
queue/日付-noon.json・日付-eve.json があればそれを使い、なければClaude APIで生成。
投稿時刻は、枠の中から1分単位でランダムに決める(日付と枠から決まるので、同じ回で再実行しても同じ時刻)。"""
import datetime, json, os, random, shutil, sys
from zoneinfo import ZoneInfo
import generate

HOURS = {"noon": 12, "eve": 20}

def due_slot(now, today, hist):
    """15分ごとの確認で呼ばれる。時刻が来ていて、まだ投稿していない枠のうち、古いものを返す。"""
    for slot in ("noon", "eve"):
        if any(h.get("date") == today.isoformat() and h.get("slot") == slot for h in hist): continue
        h, m = map(int, random_time(today, slot).split(":"))
        if now >= now.replace(hour=h, minute=m, second=0, microsecond=0): return slot
    return None

def current_slot(now, today=None, hist=None):
    if os.environ.get("SLOT") in HOURS: return os.environ["SLOT"]            # 手動実行で枠を指定
    if os.environ.get("EVENT_NAME") == "schedule": return due_slot(now, today, hist or [])
    return "noon" if now.hour < 16 else "eve"

def random_time(date, slot):
    minute = random.Random(f"{date.isoformat()}-{slot}").randrange(0, 60)
    return f"{HOURS[slot]}:{minute:02d}"

def set_output(key, value):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        open(path, "a").write(f"{key}={value}\n")

def main(out):
    now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
    today = now.date()
    hist = json.load(open(generate.HIST, encoding="utf-8")) if os.path.exists(generate.HIST) else []
    slot = current_slot(now, today, hist)
    if slot is None:
        print("skip: いま投稿する枠はありません"); set_output("skip", "true"); return
    # 二重投稿の防止: 同じ日・同じ枠がすでに投稿済みなら何もしない
    if any(h.get("date") == today.isoformat() and h.get("slot") == slot for h in hist):
        print("skip: already posted", today, slot); set_output("skip", "true"); return
    q = f"queue/{today.isoformat()}-{slot}.json"
    if os.path.exists(q):
        shutil.copy(q, out)
    else:
        generate.main(out)
    s = json.load(open(out, encoding="utf-8"))
    s["post_time"] = random_time(today, slot)
    # 自動実行が大幅に遅れて、枠の終わりを過ぎてしまった場合は投稿しない(手動実行は常に投稿)
    h, m = map(int, s["post_time"].split(":"))
    late = (now - now.replace(hour=h, minute=m, second=0, microsecond=0)).total_seconds() / 60
    if os.environ.get("EVENT_NAME") == "schedule" and late > 300:   # 5時間以上遅れたら、次の枠と重なるのでスキップ
        print(f"skip: {late:.0f} min after post time"); set_output("skip", "true"); return
    s["slot"] = slot
    json.dump(s, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 投稿の記録(history.json)は、投稿が成功したあとにワークフローで書く(失敗した枠を再試行できるようにする)
    print("slot:", slot, "post_time:", s["post_time"])

if __name__ == "__main__":
    main(sys.argv[1])
