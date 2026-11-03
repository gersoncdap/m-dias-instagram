import os, json, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont
from conteudo import POSTS, HASHTAGS

OUT = "/home/claude/ig_agent/out"
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
F = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
BG, RED, YEL, WHITE, GREY = "#0B0B0B", "#E63946", "#FFD400", "#FFFFFF", "#9A9A9A"
ASSINATURA = "Gerson Santos  |  Executivo na Área da Saúde"
HANDLE = "@gersononovo"

def font(w, s): return ImageFont.truetype(F % w, s)

def wrap(d, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def fit(d, text, weight, maxw, maxh, start, minsize=40, lh=1.15):
    s = start
    while s > minsize:
        fnt = font(weight, s); lines = wrap(d, text, fnt, maxw)
        if len(lines) * s * lh <= maxh and all(d.textlength(l, font=fnt) <= maxw for l in lines): return fnt, lines, s
        s -= 4
    fnt = font(weight, s); return fnt, wrap(d, text, fnt, maxw), s

def block(d, text, weight, x, y, maxw, maxh, start, fill, lh=1.15, anchor_mid=False):
    fnt, lines, s = fit(d, text, weight, maxw, maxh, start, lh=lh)
    h = len(lines) * s * lh
    yy = y + (maxh - h) / 2 if anchor_mid else y
    for l in lines:
        d.text((x, yy), l, font=fnt, fill=fill); yy += s * lh
    return yy

def frame(W, H):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 18, H], fill=RED)  # barra lateral vermelha
    return im, d

def tag(d, x, y, text="PONTO DE VISTA"):
    fnt = font("ExtraBold", 34); w = d.textlength(text, font=fnt)
    d.rectangle([x, y, x + w + 40, y + 60], fill=YEL)
    d.text((x + 20, y + 10), text, font=fnt, fill=BG)

def footer(d, W, H, extra=None):
    d.line([(80, H - 150), (W - 80, H - 150)], fill="#2A2A2A", width=2)
    d.text((80, H - 120), ASSINATURA, font=font("Medium", 28), fill=GREY)
    d.text((80, H - 80), HANDLE, font=font("SemiBold", 28), fill=YEL)
    if extra:
        f2 = font("SemiBold", 28); d.text((W - 80 - d.textlength(extra, font=f2), H - 80), extra, font=f2, fill=GREY)

def save(im, path):
    im.convert("P", palette=Image.ADAPTIVE, colors=64).save(path, optimize=True)

def cover(p, W=1080, H=1350):
    im, d = frame(W, H); tag(d, 80, 110)
    block(d, p["titulo"], "Black", 80, 260, W - 160, 760, 120, WHITE, lh=1.08, anchor_mid=True)
    d.text((80, 1080), "Arraste para ler  →".replace("→", ">"), font=font("SemiBold", 32), fill=RED)
    footer(d, W, H); return im

def slide(p, i, text, n, W=1080, H=1350):
    im, d = frame(W, H); tag(d, 80, 110)
    d.text((W - 80 - d.textlength(f"{i}/{n}", font=font("ExtraBold", 40)), 118), f"{i}/{n}", font=font("ExtraBold", 40), fill=YEL)
    block(d, text, "ExtraBold", 80, 260, W - 160, 760, 76, WHITE, lh=1.2, anchor_mid=True)
    footer(d, W, H); return im

def cta(p, n, W=1080, H=1350):
    im, d = frame(W, H); tag(d, 80, 110)
    d.text((W - 80 - d.textlength(f"{n}/{n}", font=font("ExtraBold", 40)), 118), f"{n}/{n}", font=font("ExtraBold", 40), fill=YEL)
    block(d, "Concorda ou discorda?", "Black", 80, 330, W - 160, 300, 96, YEL, lh=1.1)
    block(d, "Deixa seu ponto de vista nos comentários e compartilha com quem precisa ler isso.", "SemiBold", 80, 640, W - 160, 300, 52, WHITE, lh=1.25)
    d.rectangle([80, 960, 540, 1040], fill=RED)
    d.text((110, 978), "Siga " + HANDLE, font=font("ExtraBold", 36), fill=WHITE)
    footer(d, W, H); return im

def single(p, W=1080, H=1350):
    im, d = frame(W, H); tag(d, 80, 110)
    y = block(d, p["titulo"], "Black", 80, 250, W - 160, 420, 92, YEL, lh=1.08)
    d.line([(80, y + 30), (300, y + 30)], fill=RED, width=8)
    block(d, p["texto"], "SemiBold", 80, y + 80, W - 160, 1150 - (y + 80), 52, WHITE, lh=1.25)
    footer(d, W, H); return im

def reel_card(text, i, n, titulo, W=1080, H=1920):
    im, d = frame(W, H); tag(d, 80, 260)
    d.text((80, 340), titulo.upper(), font=font("Bold", 30), fill=GREY)
    block(d, text, "Black", 80, 520, W - 160, 900, 96, WHITE if i % 2 else YEL, lh=1.12, anchor_mid=True)
    # barra de progresso
    seg = (W - 160 - (n - 1) * 12) / n
    for k in range(n):
        x0 = 80 + k * (seg + 12)
        d.rectangle([x0, 1500, x0 + seg, 1510], fill=RED if k <= i else "#333333")
    footer(d, W, H); return im

def make_reel(p, folder):
    cards = p["cards"]; n = len(cards) + 1
    paths = []
    for i, c in enumerate(cards):
        pt = f"{folder}/card{i}.png"; reel_card(c, i, n, p["titulo"]).save(pt); paths.append(pt)
    im, d = frame(1080, 1920); tag(d, 80, 260)
    block(d, "Concorda? Comenta aqui.", "Black", 80, 600, 920, 500, 100, YEL, lh=1.1, anchor_mid=True)
    d.rectangle([80, 1200, 560, 1290], fill=RED); d.text((110, 1220), "Siga " + HANDLE, font=font("ExtraBold", 40), fill=WHITE)
    footer(d, 1080, 1920); pt = f"{folder}/card{n-1}.png"; im.save(pt); paths.append(pt)
    # concat com fade: cada card 3,5s
    inputs = []; filt = ""
    dur = 3.5
    for i, pt in enumerate(paths):
        inputs += ["-loop", "1", "-t", str(dur), "-i", pt]
    parts = []
    for i in range(n):
        parts.append(f"[{i}:v]fade=t=in:st=0:d=0.4,fade=t=out:st={dur-0.4}:d=0.4,format=yuv420p[v{i}]")
    filt = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[out]"
    mp4 = f"{OUT}/post{p['id']}_reel.mp4"
    subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", "[out]", "-r", "24",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4],
                   check=True, capture_output=True)
    return mp4

manifest = []
for p in POSTS:
    files = []
    if p["tipo"] == "carrossel":
        n = len(p["slides"]) + 2
        pt = f"{OUT}/post{p['id']}_s1.png"; save(cover(p), pt); files.append(pt)
        for i, s in enumerate(p["slides"], start=2):
            pt = f"{OUT}/post{p['id']}_s{i}.png"; save(slide(p, i, s, n), pt); files.append(pt)
        pt = f"{OUT}/post{p['id']}_s{n}.png"; save(cta(p, n), pt); files.append(pt)
    elif p["tipo"] == "post":
        pt = f"{OUT}/post{p['id']}_s1.png"; save(single(p), pt); files.append(pt)
    else:
        folder = f"{OUT}/tmp{p['id']}"; os.makedirs(folder, exist_ok=True)
        files.append(make_reel(p, folder)); shutil.rmtree(folder)
    manifest.append({"id": p["id"], "tipo": p["tipo"], "data": p["data"], "titulo": p["titulo"],
                     "legenda": p["legenda"] + "\n\n" + HASHTAGS, "files": files})
json.dump(manifest, open(f"{OUT}/manifest.json", "w"), ensure_ascii=False, indent=1)
for m in manifest:
    print(m["id"], m["tipo"], [f"{os.path.basename(f)} {os.path.getsize(f)//1024}KB" for f in m["files"]])
