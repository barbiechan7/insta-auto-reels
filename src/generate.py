"""Claude APIで台本を生成。過去30日のテーマは避ける。"""
import json, os, random, sys, datetime
import anthropic

HIST = "history.json"
PAST = "data/past_posts_2026-10-17.csv"   # 過去投稿の タイトル/ビュー数(シリーズ,タイトル,ビュー数)

def past_summary():
    """過去実績から「当たり」と「外れ」のタイトルを渡す"""
    import csv
    rows = [(t, int(v)) for s, t, v in csv.reader(open(PAST, encoding="utf-8")) if s == "生まれた日"]
    rows.sort(key=lambda r: -r[1])
    return [t for t, _ in rows[:12]], [t for t, _ in rows[-8:]], {t for t, _ in rows}
THEMES = ["努力が実る人","運気が急上昇する人","愛される才能がある人","お金に愛される人","直感が冴えている人",
          "人生が豊かな人","周りに恵まれる人","突然チャンスが来る人","強運を持っている人","夢を叶える人"]

def main(out):
    hist = json.load(open(HIST, encoding="utf-8")) if os.path.exists(HIST) else []
    recent = [h["theme"] for h in hist[-30:]]
    hit, miss, used = past_summary()
    days = random.sample(range(1, 32), 15)
    groups = ["・".join(map(str, sorted(days[i*3:i*3+3]))) for i in range(5)]
    prompt = f"""占い系ショート動画の台本をJSONのみで出力してください。
- theme: 「〇〇な人」形式の10文字以内のタイトル。次は使用禁止: {recent} と過去に使った全タイトル {sorted(used)}。
  当たり(ビュー数が多い)タイトルの傾向: {hit}。共通点は「一生」「人生」「お金」「勝ち」など断定的で強い言葉。これに寄せつつ、新しい言い回しにする。
  外れの傾向(避ける): {miss}。復縁・才能・結ばれる系は弱い。
- ranks: 5件。各件 days は次をこの順で使う: {groups}
  lines は2要素、各16文字以内、前向きで具体的な文。1位ほど強い表現。
- caption: 140字以内。末尾に「※AI生成コンテンツ・娯楽としてお楽しみください」
- hashtags: 8個、配列、#付き
形式: {{"theme":"","ranks":[{{"days":"","lines":["",""]}}],"caption":"","hashtags":[]}}"""
    msg = anthropic.Anthropic().messages.create(
        model="claude-sonnet-5-5", max_tokens=1500, messages=[{"role": "user", "content": prompt}])
    txt = msg.content[0].text
    s = json.loads(txt[txt.index("{"):txt.rindex("}")+1])
    assert len(s["ranks"]) == 5 and all(len(r["lines"]) == 2 for r in s["ranks"])
    json.dump(s, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hist.append({"date": datetime.date.today().isoformat(), "theme": s["theme"]})
    json.dump(hist[-100:], open(HIST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main(sys.argv[1])
