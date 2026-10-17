"""固定背景(星空+星座ホイール)を生成して assets/bg.mp4 に保存。1回だけ実行すればOK。
自分の背景にしたい場合は assets/bg.mp4 を縦長動画(5秒以上)で置き換える。"""
import math, random, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, N = 1080, 1920, 30, 150
SYMF = ImageFont.truetype("/System/Library/Fonts/Apple Symbols.ttf", 64)
SIGNS = "♈♉♊♋♌♍♎♏♐♑♒♓"
random.seed(7); rng = np.random.default_rng(7)

# 縦グラデーション(上: 濃紺, 下: 明るめの青)
y = np.linspace(0, 1, H)[:, None, None]
top, bot = np.array([8, 24, 70]), np.array([30, 90, 170])
base = (top + (bot - top) * y ** 0.8) * np.ones((1, W, 1))
vig = 1 - 0.25 * ((np.arange(W)[None, :, None] - W / 2) / (W / 2)) ** 2
base = (base * vig).astype(np.float32)

stars = [(random.randrange(W), random.randrange(H), random.choice([1, 1, 2, 2, 3]), random.random() * 6.28)
         for _ in range(500)]

def wheel(angle):
    S = 1100; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S // 2
    for r, w, a in ((520, 5, 200), (440, 3, 150), (300, 3, 150), (200, 2, 120)):
        d.ellipse((c-r, c-r, c+r, c+r), outline=(150, 190, 255, a), width=w)
    for k in range(12):
        t = angle + k * math.pi / 6
        d.line((c+300*math.cos(t), c+300*math.sin(t), c+520*math.cos(t), c+520*math.sin(t)), fill=(150, 190, 255, 140), width=3)
        m = t + math.pi / 12; x, yy = c + 370 * math.cos(m), c + 370 * math.sin(m)
        g = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((55, 55), SIGNS[k], font=SYMF, fill=(170, 220, 230, 230), anchor="mm")
        g = g.rotate(-math.degrees(m) - 90, resample=Image.BICUBIC)
        im.alpha_composite(g, (int(x - 55), int(yy - 55)))
    # 中心の光
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((c-120, c-120, c+120, c+120), fill=(200, 225, 255, 150))
    return Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(50)))

def main(out):
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(N):
            t = i / FPS
            frame = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert("RGBA")
            d = ImageDraw.Draw(frame)
            for x, yy, s, ph in stars:
                a = int(130 + 125 * math.sin(t * 2.2 + ph))
                d.ellipse((x - s/2, yy - s/2, x + s/2, yy + s/2), fill=(225, 238, 255, max(40, a)))
            wh = wheel(t * 0.12)
            frame.alpha_composite(wh, (W // 2 - 550, 120 - 550 + 150))
            # 流れ星
            p = (t / 5.0) % 1.0
            sx, sy = 900 - 700 * p, 700 + 650 * p
            d.line((sx, sy, sx + 160, sy - 150), fill=(255, 255, 255, int(220 * math.sin(p * math.pi))), width=3)
            frame.convert("RGB").save(f"{tmp}/b{i:04d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/b%04d.png",
                        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", out], check=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "assets/bg.mp4")
