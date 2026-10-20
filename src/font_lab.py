"""フォント比較: 同じ背景・同じ色(白+影)で、書体だけを変えた案を作る。"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1920
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
ROW_Y = [565, 765, 965, 1160, 1360]
FONTS = {   # 名前: (見出し/順位/日付, 説明文, 見出しの大きさ補正, 見出しの縁取り太さ)
 "A_明朝_Black(太い)":     ("ZenOldMincho-Black.ttf", "ZenOldMincho-Black.ttf", 1.0, 1),
 "B_明朝_Bold":           ("ZenOldMincho-Bold.ttf", "ZenOldMincho-Bold.ttf", 1.0, 0),
 "C_明朝_SemiBold":       ("ZenOldMincho-SemiBold.ttf", "ZenOldMincho-SemiBold.ttf", 1.0, 0),
 "D_明朝_Medium(細い)":    ("ZenOldMincho-Medium.ttf", "ZenOldMincho-Medium.ttf", 1.0, 0),
}
def font(name, size): return ImageFont.truetype(os.path.join(FD, name), int(size))
def fit(d, s, name, size, maxw):
    while d.textlength(s, font=font(name, size)) > maxw and size > 20: size -= 2
    return font(name, size)

def render(bg, script, head, body, k, sw=1):
    im = bg.convert("RGBA"); L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); S = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(S)
    white, shad = (255, 255, 255, 255), (0, 10, 50, 210)
    def put(xy, s, f, anchor="lm", sw=0):
        sd.text((xy[0] + 3, xy[1] + 5), s, font=f, fill=shad, anchor=anchor, stroke_width=sw, stroke_fill=shad)
        d.text(xy, s, font=f, fill=white, anchor=anchor, stroke_width=sw, stroke_fill=white)
    put((W // 2, 365), script["theme"], fit(d, script["theme"], head, 92 * k, 960), "mm", sw)
    for i, r in enumerate(script["ranks"]):
        y = ROW_Y[i]; ds = f"{r['days']}日生まれ"
        put((110, y), f"{i+1}位", font(head, 78 * k), "lm", sw)
        put((285, y), ds, fit(d, ds, head, 84 * k, 700), "lm", sw)
        for j, l in enumerate(r["lines"]): put((281, y + 76 + j * 50), l, fit(d, l, body, 40, 780), "lm")
    for y, s in zip((1578, 1665), ["長押しで止められるわ", "フォローで運気UP"]): put((W // 2, y), s, fit(d, s, head, 66 * k, 960), "mm", sw)
    im = Image.alpha_composite(im, S.filter(ImageFilter.GaussianBlur(5)))
    return Image.alpha_composite(im, L).convert("RGB")

if __name__ == "__main__":
    script = json.load(open(sys.argv[1], encoding="utf-8")); bg = Image.open(sys.argv[2]); out = sys.argv[3]; os.makedirs(out, exist_ok=True)
    for name, (h, b, k, sw) in FONTS.items(): render(bg, script, h, b, k, sw).save(f"{out}/font_{name}.jpg", quality=92)
    print("done")
