"""サムネイル(カバー画像)を作る。台紙 assets/thumb_base.jpg の中央に、題名を金色の明朝体で重ねる。"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "assets", "thumb_base.jpg")
FONT = os.path.join(HERE, "..", "assets", "fonts", os.environ.get("THUMB_FONT", "ZenOldMincho-Black.ttf"))
GOLD, SHADOW = (144, 112, 24), (255, 232, 240)
CENTER_Y, MAX_W = 955, 880   # 枠の内側に収まる幅

def split_title(t):
    """7文字以内は1行。それ以上は助詞などの切れ目で2行に分ける"""
    if len(t) <= 7: return [t]
    best = None
    for i in range(3, len(t) - 2):
        left, right = t[:i], t[i:]
        score = abs(len(left) - len(right)) + (0 if left[-1] in "にがをはでとの" else 2)
        if best is None or score < best[0]: best = (score, [left, right])
    return best[1]

def make(title, out, lines=None):
    im = Image.open(BASE).convert("RGBA")
    lines = lines or split_title(title)
    size = 112 if len(lines) == 1 else 104
    f = ImageFont.truetype(FONT, size)
    while max(ImageDraw.Draw(im).textlength(l, font=f) for l in lines) > MAX_W:
        size -= 4; f = ImageFont.truetype(FONT, size)
    gap = int(size * 1.35)
    ys = [CENTER_Y + (i - (len(lines) - 1) / 2) * gap for i in range(len(lines))]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for l, y in zip(lines, ys):
        sd.text((540 + 5, y + 6), l, font=f, fill=SHADOW + (255,), anchor="mm", stroke_width=2, stroke_fill=SHADOW + (255,))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2)))
    d = ImageDraw.Draw(im)
    for l, y in zip(lines, ys):
        d.text((540, y), l, font=f, fill=GOLD + (255,), anchor="mm", stroke_width=1, stroke_fill=GOLD + (255,))
    im.convert("RGB").save(out, quality=95)

if __name__ == "__main__":
    s = json.load(open(sys.argv[1], encoding="utf-8"))
    make(s["theme"], sys.argv[2], s.get("thumb_lines"))
