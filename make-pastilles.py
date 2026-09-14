#!/usr/bin/env python3
"""
Génère les pastilles d'application Garig — Compte rendu Hebdo.

Le lettrage « Garig » n'est pas retypographié : il est repris tel quel depuis
garig-wordmark.png, extrait du logo d'origine. Seule la ligne « Compte rendu Hebdo »
est composée avec une police.

    python3 brand/make-pastilles.py            # tout régénérer
    python3 brand/make-pastilles.py --font /chemin/vers/Quicksand-Bold.ttf

Si vous disposez de la police exacte du logo (elle ressemble à Quicksand),
passez-la avec --font : la ligne de sous-titre sera alors identique au logo.

Dépendance : pillow  (pip install pillow)
"""

import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

WORDMARK = os.path.join(HERE, "garig-wordmark.png")
FONT_DEFAULT = os.path.join(HERE, "fonts", "Outfit-Regular.ttf")
OUT = os.path.join(ROOT, "icons")

VERT_OLIVE = (115, 148, 28)
VERT_VIF = (99, 179, 5)
NOIR = (10, 10, 10)
BLANC = (255, 255, 255)
ANTHRACITE = (28, 34, 24)

SUBTITLE = "Compte rendu Hebdo"
S = 1024  # côté de référence


def fit_font(path, text, target_w, start=40):
    size = start
    while size < 400:
        f = ImageFont.truetype(path, size)
        if f.getbbox(text)[2] - f.getbbox(text)[0] >= target_w:
            return f
        size += 2
    return ImageFont.truetype(path, size)


def tinted(mask_img, color):
    """Colore le lettrage extrait (masque alpha) dans la couleur voulue."""
    out = Image.new("RGBA", mask_img.size, color + (0,))
    out.putalpha(mask_img.split()[3])
    return out


def draw_content(canvas, wm_src, font_path, wm_color, sub_color,
                 wm_ratio=0.60, sub_ratio=0.62, block_shift=-0.015):
    """Pose le lettrage + le sous-titre, centrés, sur le canvas fourni."""
    d = ImageDraw.Draw(canvas)
    W, H = canvas.size

    wm_w = int(W * wm_ratio)
    wm_h = int(wm_w * wm_src.size[1] / wm_src.size[0])
    wm = wm_src.resize((wm_w, wm_h), Image.LANCZOS)
    wm = tinted(wm, wm_color)

    font = fit_font(font_path, SUBTITLE, W * sub_ratio)
    bb = font.getbbox(SUBTITLE)
    sub_w, sub_h = bb[2] - bb[0], bb[3] - bb[1]

    gap = int(H * 0.045)
    total = wm_h + gap + sub_h
    top = int((H - total) / 2 + H * block_shift)

    canvas.alpha_composite(wm, ((W - wm_w) // 2, top))
    d.text(((W - sub_w) // 2 - bb[0], top + wm_h + gap - bb[1]),
           SUBTITLE, font=font, fill=sub_color + (255,))
    return canvas


def disc(color):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([0, 0, S - 1, S - 1], fill=color + (255,))
    return im


def rounded(color, radius_ratio=0.225):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle(
        [0, 0, S - 1, S - 1], radius=int(S * radius_ratio), fill=color + (255,))
    return im


def build(font_path):
    wm_src = Image.open(WORDMARK).convert("RGBA")
    os.makedirs(OUT, exist_ok=True)
    made = []

    # 1 — disque vert olive, lettrage blanc (fidèle au logo d'origine)
    p = disc(VERT_OLIVE)
    draw_content(p, wm_src, font_path, BLANC, BLANC)
    made.append(("pastille-1-olive", p))

    # 2 — disque vert vif
    p = disc(VERT_VIF)
    draw_content(p, wm_src, font_path, BLANC, BLANC)
    made.append(("pastille-2-vert-vif", p))

    # 3 — disque noir, lettrage et sous-titre vert olive
    p = disc(NOIR)
    draw_content(p, wm_src, font_path, VERT_OLIVE, VERT_OLIVE)
    made.append(("pastille-3-noir-vert", p))

    # 4 — disque blanc cerclé de vert, lettrage vert
    p = disc(BLANC)
    ImageDraw.Draw(p).ellipse(
        [0, 0, S - 1, S - 1], outline=VERT_OLIVE + (255,), width=int(S * 0.035))
    draw_content(p, wm_src, font_path, VERT_OLIVE, ANTHRACITE)
    made.append(("pastille-4-blanche", p))

    # 5 — carré arrondi noir et vert (style iOS), bandeau vert en bas
    p = rounded(NOIR)
    band_h = int(S * 0.225)
    band = Image.new("RGBA", (S, band_h), (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, 0, S, band_h], fill=VERT_OLIVE + (255,))
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.paste(band, (0, S - band_h))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, S - 1, S - 1], radius=int(S * 0.225), fill=255)
    p = Image.composite(Image.alpha_composite(p, layer), p, mask)

    wm_w = int(S * 0.58)
    wm_h = int(wm_w * wm_src.size[1] / wm_src.size[0])
    wm = tinted(wm_src.resize((wm_w, wm_h), Image.LANCZOS), VERT_OLIVE)
    p.alpha_composite(wm, ((S - wm_w) // 2, int(S * 0.30)))
    font = fit_font(font_path, SUBTITLE, S * 0.64)
    bb = font.getbbox(SUBTITLE)
    ImageDraw.Draw(p).text(
        ((S - (bb[2] - bb[0])) // 2 - bb[0],
         S - band_h + (band_h - (bb[3] - bb[1])) // 2 - bb[1]),
        SUBTITLE, font=font, fill=NOIR + (255,))
    made.append(("pastille-5-carre-noir-vert", p))

    for name, img in made:
        img.save(os.path.join(OUT, name + ".png"))
        print("écrit", os.path.join("icons", name + ".png"))
    return made


def export_set(img, prefix=""):
    """Décline la pastille choisie aux tailles attendues par le navigateur."""
    for size, name in [(512, "icon-512.png"), (192, "icon-192.png"),
                       (180, "apple-touch-icon.png"), (32, "favicon-32.png")]:
        img.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, prefix + name))
        print("écrit", os.path.join("icons", prefix + name))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default=FONT_DEFAULT,
                    help="police du sous-titre (TTF/OTF)")
    ap.add_argument("--choix", type=int, default=5,
                    help="pastille déclinée en jeu d'icônes (1 à 5)")
    a = ap.parse_args()
    if not os.path.exists(a.font):
        sys.exit("Police introuvable : " + a.font)
    made = build(a.font)
    export_set(made[a.choix - 1][1])
    print("\nJeu d'icônes basé sur", made[a.choix - 1][0])
