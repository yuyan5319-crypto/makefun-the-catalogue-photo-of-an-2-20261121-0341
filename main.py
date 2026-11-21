#!/usr/bin/env python3
"""SOCKMATIC 2-slice sock toaster — studio catalogue photo, drawn procedurally.

Deterministic, no network, stdlib + PIL + numpy only.
Renders at 2048x2048, downscales to 1024x1024, saves JPEG to /output/entry.png.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2048                      # supersample size
OUT = "/output/entry.png"
random.seed(42)
rng = np.random.default_rng(42)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def rr(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


def vgrad(size, top, bottom):
    """Vertical linear gradient image."""
    t = np.linspace(0, 1, size[1])[:, None, None]
    top = np.array(top, dtype=np.float32)
    bot = np.array(bottom, dtype=np.float32)
    arr = top + (bot - top) * t
    arr = np.repeat(arr, size[0], axis=1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def brushed_metal(w, h, base=(198, 203, 208), seed=7):
    """Horizontal brushed-metal bands with slight noise."""
    r = np.random.default_rng(seed)
    base_arr = np.zeros((h, w, 3), dtype=np.float32)
    band = r.normal(0, 7, (h, 1, 1))
    slow = np.sin(np.linspace(0, 40, h))[:, None, None] * 5
    base_arr[:] = np.array(base, dtype=np.float32)
    base_arr += band + slow
    # fine horizontal streaks
    streak = r.normal(0, 3, (h, w, 1))
    base_arr += streak
    return Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8), "RGB")


def sock(draw, cx, top_y, w, h, tilt_deg, toasted=True):
    """Draw one cream sock, cuff up, tilted. Returns nothing; draws on draw.
    Sock shape: cuff rectangle at top, leg down, foot bending right at bottom.
    We draw in a local layer then rotate/paste for the tilt."""
    layer = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = w // 2, h // 4  # local origin near top centre
    cw, ch = int(w * 0.62), int(h * 0.30)   # cuff
    leg_w = int(w * 0.58)
    leg_h = int(h * 0.52)
    cream = (246, 236, 214, 255)
    cream_sh = (228, 214, 184, 255)
    red = (196, 52, 48, 255)

    # --- leg (below cuff) with slight taper ---
    leg_top = oy + ch
    leg_bot = leg_top + leg_h
    d.rounded_rectangle([ox - leg_w // 2, leg_top, ox + leg_w // 2, leg_bot],
                        radius=int(leg_w * 0.18), fill=cream)
    # --- foot: rounded blob bending to the right at bottom ---
    foot_w, foot_h = int(w * 0.72), int(h * 0.30)
    fx0, fy0 = ox - leg_w // 2 + 6, leg_bot - int(h * 0.06)
    d.rounded_rectangle([fx0, fy0, fx0 + foot_w, fy0 + foot_h],
                        radius=int(foot_h * 0.45), fill=cream)
    # toe patch (right end of foot)
    d.rounded_rectangle([fx0 + foot_w - int(foot_w * 0.34), fy0 + 4,
                         fx0 + foot_w - 2, fy0 + foot_h - 4],
                        radius=int(foot_h * 0.40), fill=red)
    # heel patch (left side of foot, small)
    d.rounded_rectangle([fx0 + 2, fy0 + int(foot_h * 0.15),
                         fx0 + int(foot_w * 0.20), fy0 + foot_h - int(foot_h * 0.15)],
                        radius=int(foot_h * 0.30), fill=(214, 84, 72, 255))
    # --- cuff ---
    d.rounded_rectangle([ox - cw // 2, oy, ox + cw // 2, oy + ch],
                        radius=int(cw * 0.10), fill=(250, 242, 224, 255))
    # ribbed cuff: horizontal stripes
    for i in range(5):
        y = oy + int(ch * (0.16 + 0.17 * i))
        d.line([ox - cw // 2 + 6, y, ox + cw // 2 - 6, y],
               fill=(205, 190, 160, 255), width=max(3, ch // 22))
    # red stripes on cuff
    d.rectangle([ox - cw // 2, oy + int(ch * 0.62), ox + cw // 2, oy + int(ch * 0.74)],
                fill=red)
    d.rectangle([ox - cw // 2, oy + int(ch * 0.84), ox + cw // 2, oy + int(ch * 0.90)],
                fill=red)
    # --- knit lines on leg: fine horizontal lines, subtle ---
    for i in range(12):
        y = leg_top + int(leg_h * (0.06 + 0.07 * i))
        d.line([ox - leg_w // 2 + 10, y, ox + leg_w // 2 - 10, y],
               fill=(234, 222, 196, 255), width=3)
    # vertical knit hint lines, few and faint
    for i in range(4):
        x = ox - leg_w // 2 + int(leg_w * (0.2 + 0.2 * i))
        d.line([x, leg_top + 8, x, leg_bot - 6], fill=(238, 226, 200, 255), width=3)
    # --- toasted browning on the lower visible part of the leg (just above slot) ---
    if toasted:
        toast = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        td = ImageDraw.Draw(toast)
        tb0 = leg_top + int(leg_h * 0.50)
        tb1 = leg_bot + int(h * 0.06)
        for i in range(48):
            frac = i / 48.0
            y0 = tb0 + int((tb1 - tb0) * frac)
            alpha = int(210 * (frac ** 1.2))
            col = (158 + int(26 * frac), 96, 34, alpha)
            td.line([ox - leg_w // 2 - 2, y0, ox + leg_w // 2 + 2, y0], fill=col, width=4)
        toast = toast.filter(ImageFilter.GaussianBlur(5))
        layer = Image.alpha_composite(layer, toast)
    # soft shading on right edge of sock
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle([ox + leg_w // 2 - 14, leg_top, ox + leg_w // 2 + 6,
                          leg_bot], radius=8, fill=(120, 100, 70, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    layer = Image.alpha_composite(layer, sh)

    layer = layer.rotate(tilt_deg, resample=Image.BICUBIC, expand=True,
                         center=(ox, oy + h // 2))
    # paste centred at (cx, top_y)
    px = cx - layer.width // 2
    py = top_y - int(h * 0.10)
    return layer, (px, py)


def steam_wisp(draw, x, y_top, y_bot, amp, phase):
    """One smooth curling steam wisp: a thick translucent sine polyline."""
    pts = []
    steps = 60
    for i in range(steps + 1):
        f = i / steps
        y = y_bot - (y_bot - y_top) * f
        xx = x + amp * math.sin(phase + f * 4.2) * (0.4 + f)
        pts.append((xx, y))
    draw.line(pts, fill=(255, 255, 255, 60), width=9, joint="curve")


def folded_sock_stack(draw, x, y, w, h):
    """Neat stack of 2-3 folded socks on the floor (the ONE accessory)."""
    # soft shadow under stack
    sh = Image.new("RGBA", (w * 2, h * 3), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([10, h * 2 - 30, w * 2 - 10, h * 2 + 30], fill=(0, 0, 0, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    # draw stack: three folded rounded bars, slightly offset, cream/navy/cream
    cols = [(238, 228, 204), (74, 96, 128), (246, 236, 214)]
    reds = [(196, 52, 48), (220, 220, 220), (196, 52, 48)]
    layer = Image.new("RGBA", (w * 2, h * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bw, bh = int(w * 0.92), int(h * 0.30)
    for i, (c, rc) in enumerate(zip(cols, reds)):
        bx = w // 2 - bw // 2 + (i - 1) * 14
        by = h * 2 - 40 - i * (bh + 8)
        d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2 - 4, fill=c + (255,))
        # fold seam line
        d.line([bx + 18, by + bh // 2, bx + bw - 18, by + bh // 2],
               fill=(200, 186, 150, 255), width=4)
        # small stripe near one end
        d.rectangle([bx + bw - 46, by + 6, bx + bw - 30, by + bh - 6], fill=rc + (255,))
        # knit lines
        for k in range(3):
            yy = by + int(bh * (0.25 + 0.25 * k))
            d.line([bx + 20, yy, bx + bw - 56, yy], fill=(210, 196, 164, 255), width=3)
    layer = Image.alpha_composite(sh, layer)
    return layer, (x - w // 2, y - h * 2 + 40)


def main():
    img = vgrad((S, S), (238, 236, 232), (206, 203, 198))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- radial glow behind product ---
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([S // 2 - 620, 300, S // 2 + 620, 1560], fill=(255, 255, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- floor line at ~72% ---
    floor_y = int(S * 0.72)
    draw.line([0, floor_y, S, floor_y], fill=(170, 166, 160, 255), width=4)
    # floor slightly darker below line
    fl = Image.new("RGBA", (S, S - floor_y), (196, 192, 186, 90))
    img.paste(Image.alpha_composite(img.crop((0, floor_y, S, S)).convert("RGBA"), fl),
              (0, floor_y))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- contact shadow under toaster ---
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([560, 1690, 1490, 1840], fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, sh)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- socks (behind toaster top, drawn first so slots overlap their bases) ----
    sock_w, sock_h = 330, 620
    # left sock, slot centre ~ x=880, right sock ~ x=1170 (2048 scale)
    l_layer, l_pos = sock(draw, 880, 560, sock_w, sock_h, -9)
    r_layer, r_pos = sock(draw, 1180, 560, sock_w, sock_h, 10)
    img = Image.alpha_composite(img, Image.new("RGBA", img.size, (0, 0, 0, 0)))
    tmp = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tmp.paste(l_layer, l_pos, l_layer)
    tmp.paste(r_layer, r_pos, r_layer)
    img = Image.alpha_composite(img, tmp)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- toaster body ----
    bx0, by0, bx1, by1 = 600, 1120, 1450, 1760
    body = brushed_metal(bx1 - bx0, by1 - by0)
    mask = Image.new("L", (bx1 - bx0, by1 - by0), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, bx1 - bx0, by1 - by0], radius=90, fill=255)
    img.paste(body, (bx0, by0), mask)
    draw = ImageDraw.Draw(img, "RGBA")
    # body outline
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=90,
                           outline=(120, 124, 130, 255), width=6)
    # left specular highlight strip
    hl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.rounded_rectangle([bx0 + 70, by0 + 30, bx0 + 190, by1 - 30], radius=55,
                         fill=(255, 255, 255, 90))
    hl = hl.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, hl)
    # right edge darker
    dk = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dk)
    dd.rounded_rectangle([bx1 - 130, by0 + 20, bx1 - 10, by1 - 20], radius=50,
                         fill=(60, 64, 70, 70))
    dk = dk.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, dk)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- top plate with two slots ----
    draw.rounded_rectangle([bx0 + 30, by0 - 26, bx1 - 30, by0 + 64], radius=34,
                           fill=(88, 92, 98, 255), outline=(60, 62, 66, 255), width=4)
    # slots (dark, socks emerge from them)
    draw.rounded_rectangle([760, by0 - 6, 1000, by0 + 48], radius=22, fill=(28, 28, 30, 255))
    draw.rounded_rectangle([1050, by0 - 6, 1290, by0 + 48], radius=22, fill=(28, 28, 30, 255))

    # ---- steam wisps above slots ----
    steam = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    std = ImageDraw.Draw(steam)
    steam_wisp(std, 880, 300, 1080, 42, 0.4)
    steam_wisp(std, 940, 330, 1080, 34, 2.1)
    steam_wisp(std, 1170, 300, 1080, 42, 1.2)
    steam_wisp(std, 1230, 340, 1080, 30, 3.0)
    steam = steam.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, steam)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- brand plate ----
    f_brand = ImageFont.truetype(FONT_BOLD, 64)
    f_sub = ImageFont.truetype(FONT_REG, 34)
    draw.rounded_rectangle([bx0 + 90, by0 + 300, bx0 + 560, by0 + 470], radius=18,
                           fill=(52, 54, 58, 255))
    draw.text((bx0 + 130, by0 + 316), "SOCKMATIC", font=f_brand,
              fill=(240, 240, 238, 255))
    draw.text((bx0 + 132, by0 + 398), "2-SLICE SOCK TOASTER", font=f_sub,
              fill=(200, 200, 196, 255))

    # ---- dial knob front-right ----
    kx, ky, kr = 1290, 1500, 92
    draw.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(70, 72, 76, 255),
                 outline=(200, 204, 208, 255), width=6)
    draw.ellipse([kx - kr + 26, ky - kr + 26, kx + kr - 26, ky + kr - 26],
                 fill=(150, 154, 160, 255))
    # tick marks around dial
    for i in range(9):
        ang = math.radians(-120 + i * 30)
        x1 = kx + int((kr + 14) * math.cos(ang))
        y1 = ky + int((kr + 14) * math.sin(ang))
        x2 = kx + int((kr + 34) * math.cos(ang))
        y2 = ky + int((kr + 34) * math.sin(ang))
        draw.line([x1, y1, x2, y2], fill=(90, 92, 96, 255), width=6)
    # pointer
    ang = math.radians(-40)
    draw.line([kx, ky, kx + int((kr - 30) * math.cos(ang)),
               ky + int((kr - 30) * math.sin(ang))], fill=(40, 40, 42, 255), width=8)

    # ---- side lever pushed down (right side, clearly visible) ----
    draw.rounded_rectangle([bx1 - 6, by0 + 150, bx1 + 56, by0 + 420], radius=18,
                           fill=(70, 72, 76, 255), outline=(190, 194, 198, 255), width=4)
    draw.rounded_rectangle([bx1 + 10, by0 + 320, bx1 + 84, by0 + 420], radius=16,
                           fill=(40, 40, 44, 255))

    # ---- ONE accessory: folded sock stack, right of toaster, on the floor ----
    stack, spos = folded_sock_stack(draw, 1760, floor_y + 90, 300, 300)
    tmp2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    tmp2.paste(stack, spos, stack)
    img = Image.alpha_composite(img, tmp2)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- finish: downscale, grain, vignette ----
    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32)
    noise = rng.normal(0, 3.0, arr.shape[:2])[..., None]
    arr = np.clip(arr + noise, 0, 255)
    # subtle vignette
    yy, xx = np.mgrid[0:1024, 0:1024]
    dx = (xx - 512) / 512.0
    dy = (yy - 512) / 512.0
    dist = np.sqrt(dx * dx + dy * dy)
    vig = 1.0 - 0.10 * np.clip(dist - 0.55, 0, 1) ** 2
    arr *= vig[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

    os.makedirs("/output", exist_ok=True)
    q = 88
    img.save(OUT, "JPEG", quality=q)
    while os.path.getsize(OUT) > 1_048_576 and q > 60:
        q -= 6
        img.save(OUT, "JPEG", quality=q)
    print(f"saved {OUT} {os.path.getsize(OUT)} bytes quality={q}")


if __name__ == "__main__":
    main()
