#!/usr/bin/env python3
"""LINEスタンプ仕上げパイプライン
白背景イラスト → 透過 → 文字合成 → LINE規格リサイズ → ZIP化
使い方:
  python3 finish_stamps.py --map mapping.json --out build/set1
mapping.json: [{"num": 1, "src": "path/to/img.webp", "text": "おはよう"}, ...]
出力: NN.png (370x320以内), main.png (240x240), tab.png (96x74), stamps.zip
"""
import argparse, json, os, zipfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = os.path.join(os.path.dirname(__file__), "fonts", "ZenMaruGothic-Bold.ttf")
STAMP_W, STAMP_H = 370, 320
TEXT_FILL = (74, 52, 64)       # 濃いプラムグレー（ダル可愛い基調）
TEXT_STROKE = (255, 255, 255)


def white_to_alpha(img: Image.Image, thresh: int = 42) -> Image.Image:
    """四隅からフラッドフィルして白背景だけを透過する"""
    img = img.convert("RGB")
    key = img.copy()
    w, h = key.size
    marker = (255, 0, 255)
    for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(key, xy, marker, thresh=thresh)
    import numpy as np
    a = np.array(key)
    bg = (a[:, :, 0] == 255) & (a[:, :, 1] == 0) & (a[:, :, 2] == 255)
    alpha = np.where(bg, 0, 255).astype("uint8")
    out = img.convert("RGBA")
    out.putalpha(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.6)))
    return out


def trim(img: Image.Image, pad: int = 8) -> Image.Image:
    bbox = img.getchannel("A").getbbox()
    if not bbox:
        return img
    l = max(0, bbox[0] - pad); u = max(0, bbox[1] - pad)
    r = min(img.width, bbox[2] + pad); d = min(img.height, bbox[3] + pad)
    return img.crop((l, u, r, d))


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int, start: int = 64) -> ImageFont.FreeTypeFont:
    size = start
    while size > 18:
        f = ImageFont.truetype(FONT, size)
        bb = draw.textbbox((0, 0), text, font=f, stroke_width=max(2, size // 14))
        if bb[2] - bb[0] <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(FONT, 18)


def make_stamp(src: str, text: str) -> Image.Image:
    img = trim(white_to_alpha(Image.open(src)))
    # 文字帯ぶんの高さを確保してキャンバスに配置
    band_ratio = 0.24
    art_h = int(STAMP_H * (1 - band_ratio))
    scale = min(STAMP_W / img.width, art_h / img.height)
    nw, nh = max(2, int(img.width * scale) // 2 * 2), max(2, int(img.height * scale) // 2 * 2)
    img = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (STAMP_W, STAMP_H), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((STAMP_W - nw) // 2, STAMP_H - nh - 4))
    d = ImageDraw.Draw(canvas)
    f = fit_font(d, text, STAMP_W - 24)
    bb = d.textbbox((0, 0), text, font=f, stroke_width=max(2, f.size // 14))
    tw = bb[2] - bb[0]
    d.text(((STAMP_W - tw) // 2 - bb[0], 6), text, font=f, fill=TEXT_FILL,
           stroke_width=max(2, f.size // 14), stroke_fill=TEXT_STROKE)
    # 余白を詰めて偶数サイズに
    out = trim(canvas, pad=2)
    w = min(STAMP_W, out.width + (out.width % 2)); h = min(STAMP_H, out.height + (out.height % 2))
    final = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    final.alpha_composite(out, ((w - out.width) // 2, (h - out.height) // 2))
    return final


def make_main_tab(base_src: str, out_dir: str):
    img = trim(white_to_alpha(Image.open(base_src)))
    main = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    s = min(232 / img.width, 232 / img.height)
    r = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    main.alpha_composite(r, ((240 - r.width) // 2, (240 - r.height) // 2))
    main.save(os.path.join(out_dir, "main.png"))
    tab = main.resize((96, 74), Image.LANCZOS)
    tab.save(os.path.join(out_dir, "tab.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default=None, help="メイン/タブ画像の元画像")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    items = json.load(open(args.map, encoding="utf-8"))
    made = []
    for it in items:
        stamp = make_stamp(it["src"], it["text"])
        name = f'{it["num"]:02d}.png'
        stamp.save(os.path.join(args.out, name))
        made.append(name)
        print("made", name, stamp.size)
    if args.base:
        make_main_tab(args.base, args.out)
        made += ["main.png", "tab.png"]
    with zipfile.ZipFile(os.path.join(args.out, "stamps.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for n in made:
            z.write(os.path.join(args.out, n), n)
    print("zip done:", len(made), "files")


if __name__ == "__main__":
    main()
