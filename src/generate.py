"""Claude APIで台本を生成。過去30日のテーマは避ける。"""
import json, os, random, sys, datetime
import anthropic

HIST = "history.json"
THEMES = ["努力が実る人","運気が急上昇する人","愛される才能がある人","お金に愛される人","直感が冴えている人",
          "人生が豊かな人","周りに恵まれる人","突然チャンスが来る人","強運を持っている人","夢を叶える人"]

def main(out):
    hist = json.load(open(HIST, encoding="utf-8")) if os.path.exists(HIST) else []
    recent = [h["theme"] for h in hist[-30:]]
    days = random.sample(range(1, 32), 15)
    groups = ["・".join(map(str, sorted(days[i*3:i*3+3]))) for i in range(5)]
    prompt = f"""占い系ショート動画の台本をJSONのみで出力してください。
- theme: 「〇〇な人」形式の8文字以内のタイトル。次は使用禁止: {recent}。参考例: {THEMES}
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
