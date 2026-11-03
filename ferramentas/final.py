# Slide final (carrossel) e card final (Reel) com a foto do Gerson e @gersononovo + bandeira
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
BG, RED, YEL, WHITE, GREY = "#0B0B0B", "#E63946", "#FFD400", "#FFFFFF", "#9A9A9A"
HANDLE = "@gersononovo"
FOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "foto.png")

def font(w, s): return ImageFont.truetype(F % w, s)

def flag(size=109):
    """Bandeira do Brasil via Noto Color Emoji (tamanho fixo 109, redimensionada depois)."""
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), "\U0001F1E7\U0001F1F7", font=f, embedded_color=True)
    bbox = im.getbbox(); im = im.crop(bbox)
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)

def photo_panel(W, H, side="right", width_frac=0.52, fade=260):
    """Foto recortada ocupando a altura toda, com esfumado para o preto do lado do texto."""
    ph = Image.open(FOTO).convert("RGB")
    pw = int(W * width_frac)
    scale = H / ph.height
    ph = ph.resize((int(ph.width * scale), H), Image.LANCZOS)
    # recorte centralizado no rosto/torso (leve deslocamento para a esquerda da foto)
    left = max(0, int(ph.width * 0.5 - pw * 0.5))
    ph = ph.crop((left, 0, left + pw, H))
    mask = Image.new("L", (pw, H), 255)
    md = ImageDraw.Draw(mask)
    for i in range(fade):
        a = int(255 * i / fade)
        x = i if side == "right" else pw - 1 - i
        md.line([(x, 0), (x, H)], fill=a)
    return ph, mask, pw

def handle_line(d, im, x, y, size, color=YEL):
    f = font("Black", size); d.text((x, y), HANDLE, font=f, fill=color)
    w = d.textlength(HANDLE, font=f)
    fl = flag(int(size * 0.95))
    im.paste(fl, (int(x + w + size * 0.25), int(y + size * 0.12)), fl)

def cta_carrossel(W=1080, H=1350):
    im = Image.new("RGB", (W, H), BG)
    ph, mask, pw = photo_panel(W, H, "right", 0.55, 300)
    im.paste(ph, (W - pw, 0), mask)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 18, H], fill=RED)
    # tag
    f = font("ExtraBold", 34); t = "PONTO DE VISTA"; w = d.textlength(t, font=f)
    d.rectangle([80, 110, 80 + w + 40, 170], fill=YEL); d.text((100, 120), t, font=f, fill=BG)
    # texto
    y = 330
    for line in ["Concorda", "ou", "discorda?"]:
        d.text((80, y), line, font=font("Black", 92), fill=WHITE); y += 100
    y += 30
    for line in ["Deixa seu ponto", "de vista nos", "comentários."]:
        d.text((80, y), line, font=font("SemiBold", 44), fill=GREY); y += 54
    # handle + bandeira
    handle_line(d, im, 80, 980, 64)
    d.text((80, 1070), "Siga e compartilhe", font=font("SemiBold", 34), fill=WHITE)
    d.text((80, H - 110), "Gerson Santos  |  Executivo na Área da Saúde", font=font("Medium", 26), fill=GREY)
    return im

def cta_reel(W=1080, H=1920):
    im = Image.new("RGB", (W, H), BG)
    # foto no topo, com esfumado para baixo
    ph = Image.open(FOTO).convert("RGB")
    scale = W / ph.width
    ph = ph.resize((W, int(ph.height * scale)), Image.LANCZOS)
    ph = ph.crop((0, 0, W, min(ph.height, 1150)))
    mask = Image.new("L", ph.size, 255); md = ImageDraw.Draw(mask)
    fade = 380
    for i in range(fade):
        a = int(255 * (1 - i / fade)); yy = ph.height - fade + i
        md.line([(0, yy), (W, yy)], fill=a)
    im.paste(ph, (0, 0), mask)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 18, H], fill=RED)
    f = font("ExtraBold", 34); t = "PONTO DE VISTA"; w = d.textlength(t, font=f)
    d.rectangle([80, 120, 80 + w + 40, 180], fill=YEL); d.text((100, 130), t, font=f, fill=BG)
    d.text((80, 1130), "Concorda?", font=font("Black", 110), fill=WHITE)
    d.text((80, 1250), "Comenta aqui.", font=font("Black", 110), fill=YEL)
    handle_line(d, im, 80, 1440, 72)
    d.text((80, 1545), "Siga e compartilhe", font=font("SemiBold", 36), fill=WHITE)
    d.text((80, H - 130), "Gerson Santos  |  Executivo na Área da Saúde", font=font("Medium", 28), fill=GREY)
    return im

if __name__ == "__main__":
    cta_carrossel().save("/home/claude/ig_agent/out/cta_prev.png")
    cta_reel().save("/home/claude/ig_agent/out/ctareel_prev.png")
    print("ok")
