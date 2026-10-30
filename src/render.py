"""台本JSON + 背景動画 -> 1080x1920 5秒の無音リール。参考動画のレイアウトを再現。"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1080, 1920, 30, 5.0
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")   # リポジトリ同梱(OFL)。CI環境のフォントに依存しない
FONT_HEAD = os.path.join(FONT_DIR, "ZenOldMincho-Bold.ttf")   # 明朝(Bold)。環境変数 TELOP_FONT で太さを変えて試せる
FONT_BODY = FONT_HEAD   # 本文も同じ書体
if os.environ.get("TELOP_FONT"): FONT_HEAD = FONT_BODY = os.path.join(FONT_DIR, os.environ["TELOP_FONT"])
def font(size, body=False): return ImageFont.truetype(FONT_BODY if body else FONT_HEAD, size)

ROW_Y = [565, 765, 965, 1160, 1360]   # 各位の見出し中心y
TITLE_Y, FOOT_Y = 365, [1578, 1665]
CYAN, MAGENTA, WHITE = (0, 255, 255), (255, 0, 200), (255, 255, 255)

def text_c(d, xy, s, f, fill, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def glitch(layer, xy, s, f, anchor="mm", off=4):
    """白文字+やわらかい影(色ずれなし)。関数名は互換のため残している"""
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + 3, xy[1] + 5), s, font=f, fill=(0, 10, 50, 210), anchor=anchor)
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(layer).text(xy, s, font=f, fill=WHITE + (255,), anchor=anchor)

def moon(d, cx, cy, r):
    m = Image.new("L", (r*4, r*4), 0); md = ImageDraw.Draw(m)
    md.ellipse((r, r, r*3, r*3), fill=255)
    md.ellipse((r+r//2, r-r//4, r*3+r//2, r*3-r//4), fill=0)
    return m

def static_layers(script, off=4):
    title = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font(92)
    while ImageDraw.Draw(title).textlength(script["theme"], font=f) > 960: f = font(f.size - 4)
    glitch(title, (W // 2, TITLE_Y), script["theme"], f)
    foot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glitch(foot, (W // 2, 1620), "長押しで止められるわ", font(70))   # 最後の文は1行だけ
    return title, foot

def row_layer(script, i, nchars):
    """i位の行。nchars=説明文の表示済み文字数(タイプライター)"""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    y = ROW_Y[i]; r = script["ranks"][i]
    ds = f"{r['days']}日生まれ"; df = font(84)
    while d.textlength(ds, font=df) > 700: df = font(df.size - 2)   # 日付が長くても右にはみ出さない
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    text_c(sd, (113, y+4), f"{i+1}位", font(80), (0, 10, 50, 200), "lm")
    text_c(sd, (288, y+4), ds, df, (0, 10, 50, 200), "lm")
    L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    text_c(d, (110, y), f"{i+1}位", font(80), WHITE+(255,), "lm")
    text_c(d, (285, y), ds, df, WHITE+(255,), "lm")
    left = nchars
    for k, line in enumerate(r["lines"]):
        shown = line[:max(0, left)]; left -= len(line)
        if shown:
            yy = y + 74 + k*50
            text_c(d, (281, yy+2), shown, font(40, True), (0, 10, 50, 170), "lm")
            text_c(d, (280, yy), shown, font(40, True), WHITE+(255,), "lm")
    return L

def render(script_path, bg_path, out_path):
    """script に segments(5本の台本)があれば、5秒×5本をつないだ25秒版。なければ従来の5秒版"""
    script = json.load(open(script_path, encoding="utf-8"))
    if "segments" not in script:
        return render_one(script, bg_path, out_path)
    with tempfile.TemporaryDirectory() as tmp:
        lst = []
        for i, seg in enumerate(script["segments"]):
            p = f"{tmp}/seg{i}.mp4"
            render_one(seg, bg_path, p, with_bgm=False); lst.append(f"file '{p}'")
        open(f"{tmp}/list.txt", "w").write("\n".join(lst))
        total = DUR * len(lst)
        bgm = os.path.join(HERE, "..", "assets", "bgm.m4a")
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt"]
        if os.path.exists(bgm) and os.environ.get("NO_BGM") != "1":
            vol = os.environ.get("BGM_VOLUME", "0.5")
            cmd += ["-i", bgm, "-filter_complex",
                    f"[1:a]atrim=0:{total},volume={vol},afade=t=in:d=0.5,afade=t=out:st={total-1.5}:d=1.5,aformat=sample_rates=44100:channel_layouts=stereo[a]",
                    "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "160k"]
        else:
            cmd += ["-an"]
        cmd += ["-t", str(total), "-c:v", "copy", "-movflags", "+faststart", out_path]
        subprocess.run(cmd, check=True)
    print("wrote", out_path)

def render_one(script, bg_path, out_path, with_bgm=True):
    variants = [static_layers(script, o) for o in (3, 5, 4)]   # 色ずれの揺らぎ
    n = int(FPS*DUR)
    t_start = [0.15 + i*0.7 for i in range(5)]       # 各位の登場時刻
    type_dur, erase_at = 0.6, 4.35
    with tempfile.TemporaryDirectory() as tmp:
        cache = {}
        for fi in range(n):
            t = fi / FPS
            frame = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            title, foot = variants[(fi // 3) % 3]
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
        bgm = os.path.join(HERE, "..", "assets", "bgm.m4a")
        has_audio = with_bgm and os.path.exists(bgm) and os.environ.get("NO_BGM") != "1"
        vol = os.environ.get("BGM_VOLUME", "0.35")
        cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", bg_path,
               "-framerate", str(FPS), "-i", f"{tmp}/o%04d.png"]
        fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
              f"eq=brightness=-0.05[bg];[bg][1:v]overlay=shortest=1,format=yuv420p[v]")
        if has_audio:
            cmd += ["-i", bgm]
            fc += f";[2:a]atrim=0:{DUR},volume={vol},afade=t=in:d=0.1,afade=t=out:st={DUR-0.5}:d=0.5,aformat=sample_rates=44100:channel_layouts=stereo[a]"
        cmd += ["-filter_complex", fc, "-map", "[v]"]
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "160k"] if has_audio else ["-an"]
        cmd += ["-t", str(DUR), "-r", str(FPS), "-c:v", "libx264", "-crf", "20", "-maxrate", "8M", "-bufsize", "16M",
                "-movflags", "+faststart", out_path]
        subprocess.run(cmd, check=True)
    print("wrote", out_path)

if __name__ == "__main__":
    render(*sys.argv[1:4])
