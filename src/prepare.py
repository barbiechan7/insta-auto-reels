"""今回の投稿の台本を用意する(1日2本: 昼 12:00-13:00 / 夜 20:00-21:00)。
queue/日付-noon.json・日付-eve.json があればそれを使い、なければClaude APIで生成。
投稿時刻は、枠の中から1分単位でランダムに決める(日付と枠から決まるので、同じ回で再実行しても同じ時刻)。"""
import datetime, json, os, random, shutil, sys
from zoneinfo import ZoneInfo
import generate

HOURS = {"eve": 18}   # 1日1本。夜の18:00〜19:59のあいだの、1分単位のランダムな時刻に投稿する(以前は昼+夜の2本)

def due_slot(now, today, hist):
    """15分ごとの確認で呼ばれる。今日まだ1本も投稿していなくて、時刻が来ていれば、その枠を返す。"""
    if any(h.get("date") == today.isoformat() for h in hist): return None   # 1日1本: 今日すでに投稿済み
    h, m = map(int, random_time(today, "eve").split(":"))
    return "eve" if now >= now.replace(hour=h, minute=m, second=0, microsecond=0) else None

def current_slot(now, today=None, hist=None):
    if os.environ.get("SLOT") in HOURS: return os.environ["SLOT"]            # 手動実行で枠を指定
    if os.environ.get("EVENT_NAME") == "schedule" or os.environ.get("POLL") == "true": return due_slot(now, today, hist or [])
    return "eve"

def random_time(date, slot):
    total = random.Random(f"{date.isoformat()}-{slot}").randrange(0, 120)   # 18:00〜19:59
    return f"{HOURS[slot] + total // 60}:{total % 60:02d}"

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
    # 二重投稿の防止: 今日すでに投稿済みなら何もしない(手動実行で枠を指定したときは、同じ枠だけを防ぐ)
    if any(h.get("date") == today.isoformat() and (h.get("slot") == slot or os.environ.get("EVENT_NAME") == "schedule" or os.environ.get("POLL") == "true") for h in hist):
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
    if (os.environ.get("EVENT_NAME") == "schedule" or os.environ.get("POLL") == "true") and late > 300:   # 5時間以上遅れたら、次の枠と重なるのでスキップ
        print(f"skip: {late:.0f} min after post time"); set_output("skip", "true"); return
    s["slot"] = slot
    json.dump(s, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 投稿の記録(history.json)は、投稿が成功したあとにワークフローで書く(失敗した枠を再試行できるようにする)
    print("slot:", slot, "post_time:", s["post_time"])

if __name__ == "__main__":
    main(sys.argv[1])
