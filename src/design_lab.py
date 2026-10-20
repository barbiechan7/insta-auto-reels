"""デザイン案づくり: 占い風の背景(5種)と、テロップの見せ方(4種)を静止画で比較する。"""
import json, math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "..", "assets", "fonts")
HEAD, BODY, MINCHO = (os.path.join(FD, f) for f in ("ZenKakuGothicNew-Black.ttf", "BIZUDPGothic-Bold.ttf", "ZenOldMincho-Black.ttf"))
F = lambda p, s: ImageFont.truetype(p, s)
ROW_Y = [565, 765, 965, 1160, 1360]

# ---------- 背景 ----------
def clouds(seed, scale_list=(4, 8, 16, 32), w=W, h=H):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for s in scale_list:
        n = rng.random((h // s + 2, w // s + 2)).astype(np.float32)
        im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(s / 3))
        acc += np.asarray(im, np.float32) / 255 * amp; tot += amp; amp *= 0.6
    acc /= tot; return (acc - acc.min()) / (acc.max() - acc.min())

def grad(top, bot):
    y = np.linspace(0, 1, H)[:, None, None]
    return np.array(top) * (1 - y) + np.array(bot) * y * np.ones((1, W, 1))

def stars(im, n, seed, color=(255, 255, 255), glow=True, maxr=3):
    rng = random.Random(seed); d = ImageDraw.Draw(im, "RGBA")
    for _ in range(n):
        x, y, r = rng.randrange(W), rng.randrange(H), rng.choice([1, 1, 1, 2, 2, maxr])
        a = rng.randrange(120, 255)
        d.ellipse((x - r, y - r, x + r, y + r), fill=color + (a,))
        if glow and r >= 2: d.ellipse((x - r * 4, y - r * 4, x + r * 4, y + r * 4), fill=color + (30,))
    return im

def sparkle(d, x, y, r, color):
    d.polygon([(x, y - r), (x + r * .18, y - r * .18), (x + r, y), (x + r * .18, y + r * .18), (x, y + r), (x - r * .18, y + r * .18), (x - r, y), (x - r * .18, y - r * .18)], fill=color)

def bg_nebula():   # 1. 紫ピンクの神秘宇宙(アカウントのサムネ色に合わせる)
    base = grad((70, 30, 125), (222, 122, 200)); c = clouds(1, (48, 96, 192))[:, :, None]
    c2 = clouds(2, (40, 80, 160))[:, :, None]
    img = base * (0.7 + 0.6 * c) + np.array([255, 160, 230]) * (c2 ** 3) * 0.6
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); im = stars(im, 650, 3, (255, 235, 250))
    return im

def bg_moon():     # 2. 深い藍に大きな三日月と金の星
    img = grad((8, 14, 48), (38, 28, 92)) + clouds(5)[:, :, None] * np.array([18, 10, 36])
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); im = stars(im, 420, 6, (255, 244, 214))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    cx, cy, r = 760, 300, 210
    g.ellipse((cx - r * 1.7, cy - r * 1.7, cx + r * 1.7, cy + r * 1.7), fill=(255, 220, 140, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(70)); im = Image.alpha_composite(im.convert("RGBA"), glow)
    m = Image.new("RGBA", (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(m)
    md.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 232, 170, 255)); md.ellipse((cx - r + 90, cy - r - 40, cx + r + 90, cy + r - 40), fill=(0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0); mm = ImageDraw.Draw(mask); mm.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255); mm.ellipse((cx - r + 90, cy - r - 40, cx + r + 90, cy + r - 40), fill=0)
    gold = Image.new("RGBA", (W, H), (255, 228, 160, 255)); im.paste(gold, (0, 0), mask)
    d = ImageDraw.Draw(im, "RGBA"); rng = random.Random(7)
    for _ in range(16): sparkle(d, rng.randrange(60, W - 60), rng.randrange(40, 900), rng.randrange(10, 26), (255, 226, 150, 230))
    return im.convert("RGB")

def bg_mandala():  # 3. 黒紫に金の曼荼羅(タロット・神秘)
    img = grad((18, 8, 40), (48, 14, 70)) + clouds(9)[:, :, None] * np.array([16, 6, 24])
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); cx, cy = W // 2, 210
    gold = (226, 182, 96)
    for r, w, a in ((440, 4, 200), (400, 2, 150), (320, 3, 190), (250, 2, 150), (175, 3, 200), (100, 2, 150)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=gold + (a,), width=w)
    for k in range(24):
        t = k * math.pi / 12
        d.line((cx + 100 * math.cos(t), cy + 100 * math.sin(t), cx + 440 * math.cos(t), cy + 440 * math.sin(t)), fill=gold + (90,), width=2)
    for k in range(12):
        t = k * math.pi / 6 + math.pi / 12
        pts = [(cx + 320 * math.cos(t + dt), cy + 320 * math.sin(t + dt)) for dt in (-0.12, 0, 0.12)] + [(cx + 440 * math.cos(t), cy + 440 * math.sin(t))]
        d.polygon(pts, outline=gold + (200,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((cx - 120, cy - 120, cx + 120, cy + 120), fill=(255, 210, 120, 120))
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(50))); im = Image.alpha_composite(im, ov)
    return stars(im.convert("RGB"), 260, 11, (255, 236, 190))

def bg_rose():     # 4. ローズクォーツ(淡いピンクとラベンダー、きらきら)
    base = grad((250, 214, 230), (196, 176, 236)); c = clouds(13)[:, :, None]
    img = base * (0.88 + 0.22 * c) + np.array([255, 255, 255]) * (clouds(14, (8, 16, 40))[:, :, None] ** 4) * 0.5
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); rng = random.Random(15)
    for _ in range(34):
        x, y, r = rng.randrange(W), rng.randrange(H), rng.randrange(30, 120)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rng.randrange(18, 48)))
    for _ in range(40): sparkle(d, rng.randrange(W), rng.randrange(H), rng.randrange(8, 24), (255, 255, 255, 220))
    return Image.alpha_composite(im, ov.filter(ImageFilter.GaussianBlur(1))).convert("RGB")

def bg_aurora():   # 5. オーロラ(青緑〜紫の光の帯)
    base = grad((6, 12, 40), (22, 18, 70)); im = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i, (col, y0) in enumerate((((60, 255, 200), 380), ((120, 120, 255), 540), ((220, 90, 255), 700))):
        pts = []
        for x in range(0, W + 40, 40): pts.append((x, y0 + 90 * math.sin(x / 170 + i * 1.7) + 40 * math.sin(x / 60 + i)))
        d.polygon(pts + [(W, y0 + 420), (0, y0 + 420)], fill=col + (90,))
    ov = ov.filter(ImageFilter.GaussianBlur(55)); im = Image.alpha_composite(im, ov)
    return stars(im.convert("RGB"), 520, 17, (235, 245, 255))

BGS = {"1_紫の神秘宇宙": bg_nebula, "2_月と金の星": bg_moon, "3_金の曼荼羅": bg_mandala, "4_ローズクォーツ": bg_rose, "5_オーロラ": bg_aurora}

# ---------- テロップ ----------
def tx(d, xy, s, f, fill, anchor="lm", sw=0, sf=None): d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=sf)

def draw_text(im, script, style):
    im = im.convert("RGBA"); L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    foot = ["長押しで止められるわ", "誕生日をコメントで無料鑑定"]
    if style == "A_現行(色ずれ)":
        th, rk, ds, sh = F(HEAD, 92), F(HEAD, 78), F(BODY, 38), (0, 10, 50, 190)
        for o, c in ((-4, (0, 255, 255, 255)), (4, (255, 0, 200, 255)), (0, (255, 255, 255, 255))): tx(d, (W // 2 + o, 365), script["theme"], th, c, "mm")
        for i, r in enumerate(script["ranks"]):
            y = ROW_Y[i]; tx(d, (113, y + 4), f"{i+1}位", rk, sh); tx(d, (288, y + 4), f"{r['days']}日生まれ", rk, sh)
            tx(d, (110, y), f"{i+1}位", rk, (255,) * 4); tx(d, (285, y), f"{r['days']}日生まれ", rk, (255,) * 4)
            for k, l in enumerate(r["lines"]): tx(d, (280, y + 74 + k * 50), l, ds, (255,) * 4)
        for y, s in zip((1578, 1665), foot):
            for o, c in ((-3, (0, 255, 255, 255)), (3, (255, 0, 200, 255)), (0, (255, 255, 255, 255))): tx(d, (W // 2 + o, y), s, F(HEAD, 66), c, "mm")
    elif style == "B_金の明朝":
        th, rk, ds = F(MINCHO, 96), F(MINCHO, 74), F(BODY, 38)
        lum = np.asarray(im.convert("L").crop((200, 600, 900, 1500))).mean()
        dcol = (80, 40, 70, 255) if lum > 150 else (255, 238, 248, 255)
        gold, pink = (150, 112, 24, 255), (255, 232, 240, 255)
        tx(d, (W // 2 + 4, 369), script["theme"], th, pink, "mm", 2, pink); tx(d, (W // 2, 365), script["theme"], th, gold, "mm", 1, gold)
        for i, r in enumerate(script["ranks"]):
            y = ROW_Y[i]
            for xx, s in ((110, f"{i+1}位"), (285, f"{r['days']}日生まれ")):
                tx(d, (xx + 4, y + 5), s, rk, pink, "lm", 2, pink); tx(d, (xx, y), s, rk, gold, "lm", 1, gold)
            for k, l in enumerate(r["lines"]): tx(d, (281, y + 76 + k * 50), l, ds, dcol)
        for y, s in zip((1578, 1665), foot): tx(d, (W // 2 + 3, y + 4), s, F(MINCHO, 64), pink, "mm", 2, pink); tx(d, (W // 2, y), s, F(MINCHO, 64), gold, "mm", 1, gold)
    elif style == "C_白に紫ふち":
        th, rk, ds = F(HEAD, 96), F(HEAD, 78), F(HEAD, 40)
        pu = (120, 50, 190, 255)
        tx(d, (W // 2, 365), script["theme"], th, (255,) * 4, "mm", 8, pu)
        for i, r in enumerate(script["ranks"]):
            y = ROW_Y[i]; tx(d, (110, y), f"{i+1}位", rk, (255,) * 4, "lm", 7, pu); tx(d, (285, y), f"{r['days']}日生まれ", rk, (255,) * 4, "lm", 7, pu)
            for k, l in enumerate(r["lines"]): tx(d, (280, y + 76 + k * 50), l, ds, (255,) * 4, "lm", 5, pu)
        for y, s in zip((1578, 1665), foot): tx(d, (W // 2, y), s, F(HEAD, 66), (255, 246, 160, 255), "mm", 7, pu)
    elif style == "D_カード型":
        th, rk, ds = F(HEAD, 90), F(HEAD, 70), F(BODY, 36)
        pan = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pan)
        pd.rounded_rectangle((60, 290, W - 60, 440), 40, fill=(20, 10, 50, 150), outline=(255, 215, 130, 200), width=3)
        for i in range(5): y = ROW_Y[i]; pd.rounded_rectangle((60, y - 62, W - 60, y + 138), 34, fill=(20, 10, 50, 130), outline=(255, 215, 130, 120), width=2)
        pd.rounded_rectangle((60, 1520, W - 60, 1720), 40, fill=(20, 10, 50, 150), outline=(255, 215, 130, 200), width=3)
        L.alpha_composite(pan)
        tx(d, (W // 2, 365), script["theme"], th, (255, 226, 150, 255), "mm")
        for i, r in enumerate(script["ranks"]):
            y = ROW_Y[i]; tx(d, (110, y), f"{i+1}位", rk, (255, 205, 100, 255)); tx(d, (285, y), f"{r['days']}日生まれ", rk, (255,) * 4)
            for k, l in enumerate(r["lines"]): tx(d, (285, y + 70 + k * 46), l, ds, (236, 228, 255, 255))
        for y, s in zip((1578, 1665), foot): tx(d, (W // 2, y), s, F(HEAD, 62), (255, 226, 150, 255), "mm")
    sh = L.filter(ImageFilter.GaussianBlur(6)); a = sh.split()[3].point(lambda v: int(v * 0.35)); dark = Image.new("RGBA", (W, H), (0, 0, 40, 0)); dark.putalpha(a)
    return Image.alpha_composite(Image.alpha_composite(im, dark), L).convert("RGB")

STYLES = ["A_現行(色ずれ)", "B_金の明朝", "C_白に紫ふち", "D_カード型"]
PAIR = {"1_紫の神秘宇宙": "B_金の明朝", "2_月と金の星": "D_カード型", "3_金の曼荼羅": "B_金の明朝", "4_ローズクォーツ": "C_白に紫ふち", "5_オーロラ": "A_現行(色ずれ)"}

if __name__ == "__main__":
    script = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    bgs = {k: f() for k, f in BGS.items()}
    for k, im in bgs.items(): im.save(f"{out}/bg_{k}.jpg", quality=92)
    for k, im in bgs.items(): draw_text(im, script, PAIR[k]).save(f"{out}/final_{k}_{PAIR[k]}.jpg", quality=92)
    base = bgs["1_紫の神秘宇宙"]
    for s in STYLES: draw_text(base, script, s).save(f"{out}/text_{s}.jpg", quality=92)
    print("done")
