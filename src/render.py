"""台本JSON + 背景動画 -> 1080x1920 5秒の無音リール。参考動画のレイアウトを再現。"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 5.0
FONT_CANDIDATES = [
    os.environ.get("FONT_PATH", ""),
    "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
]
FONT = next(p for p in FONT_CANDIDATES if p and os.path.exists(p))
def font(size): return ImageFont.truetype(FONT, size)

ROW_Y = [565, 765, 965, 1160, 1360]   # 各位の見出し中心y
TITLE_Y, FOOT_Y = 365, [1578, 1665]
CYAN, MAGENTA, WHITE = (0, 255, 255), (255, 0, 200), (255, 255, 255)

def text_c(d, xy, s, f, fill, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def glitch(layer, xy, s, f, anchor="mm", off=4):
    """シアン/マゼンタの色ずれ付き白文字"""
    d = ImageDraw.Draw(layer)
    text_c(d, (xy[0]-off, xy[1]), s, f, CYAN + (255,), anchor)
    text_c(d, (xy[0]+off, xy[1]), s, f, MAGENTA + (255,), anchor)
    text_c(d, xy, s, f, WHITE + (255,), anchor)

def squeezed(L, xy, s, size, fill, width):
    """細い書体風にするため、描画後に横幅をwidthへ圧縮して左寄せで貼る"""
    f = font(size); tw = int(ImageDraw.Draw(L).textlength(s, font=f)) + 8
    t = Image.new("RGBA", (tw, size*2), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((4, size), s, font=f, fill=fill, anchor="lm")
    t = t.resize((width, size*2))
    L.alpha_composite(t, (xy[0]-4, xy[1]-size))

def moon(d, cx, cy, r):
    m = Image.new("L", (r*4, r*4), 0); md = ImageDraw.Draw(m)
    md.ellipse((r, r, r*3, r*3), fill=255)
    md.ellipse((r+r//2, r-r//4, r*3+r//2, r*3-r//4), fill=0)
    return m

def static_layers(script):
    title = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glitch(title, (W//2, TITLE_Y), script["theme"], font(84))
    foot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lines = ["長押しで止められるわ", "誕生日をコメントで無料鑑定"]
    for y, s in zip(FOOT_Y, lines):
        f = font(66); w = ImageDraw.Draw(foot).textlength(s, font=f)
        x0 = (W - w - 70) / 2
        glitch(foot, (x0 + w/2, y), s, f, off=3)
        mm = moon(None, 0, 0, 30); col = Image.new("RGBA", mm.size, (255, 200, 40, 255))
        foot.paste(col.resize((76, 76)), (int(x0 + w + 8), y - 40), mm.resize((76, 76)))
    return title, foot

def row_layer(script, i, nchars):
    """i位の行。nchars=説明文の表示済み文字数(タイプライター)"""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    y = ROW_Y[i]; r = script["ranks"][i]
    DW = 600
    for off, col in ((3, (0, 0, 30, 150)), (0, WHITE + (255,))):
        text_c(d, (110+off, y+off), f"{i+1}位", font(78), col, "lm")
        squeezed(L, (285+off, y+off), f"{r['days']}日生まれ", 92, col, DW)
    left = nchars
    for k, line in enumerate(r["lines"]):
        shown = line[:max(0, left)]; left -= len(line)
        if shown:
            yy = y + 70 + k*50
            text_c(d, (281, yy+2), shown, font(37), (0, 0, 30, 150), "lm")
            text_c(d, (280, yy), shown, font(37), WHITE+(255,), "lm")
    return L

def render(script_path, bg_path, out_path):
    script = json.load(open(script_path, encoding="utf-8"))
    title, foot = static_layers(script)
    n = int(FPS*DUR)
    t_start = [0.15 + i*0.7 for i in range(5)]       # 各位の登場時刻
    type_dur, erase_at = 0.6, 4.35
    with tempfile.TemporaryDirectory() as tmp:
        cache = {}
        for fi in range(n):
            t = fi / FPS
            frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            frame.alpha_composite(title); frame.alpha_composite(foot)
            for i in range(5):
                if t < t_start[i] or t >= erase_at + i*0.1:   # 頭から順に消える
                    continue
                total = sum(len(l) for l in script["ranks"][i]["lines"])
                nc = min(total, int((t - t_start[i]) / type_dur * total))
                key = (i, nc)
                if key not in cache: cache[key] = row_layer(script, i, nc)
                frame.alpha_composite(cache[key])
            frame.save(f"{tmp}/o{fi:04d}.png")
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", bg_path,
            "-framerate", str(FPS), "-i", f"{tmp}/o%04d.png",
            "-filter_complex",
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
            f"eq=brightness=-0.05[bg];[bg][1:v]overlay=shortest=1,format=yuv420p[v]",
            "-map", "[v]", "-t", str(DUR), "-r", str(FPS), "-an",
            "-c:v", "libx264", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M", "-movflags", "+faststart", out_path], check=True)
    print("wrote", out_path)

if __name__ == "__main__":
    render(*sys.argv[1:4])
