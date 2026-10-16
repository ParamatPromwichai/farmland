import math
from PIL import Image, ImageDraw, ImageFont

def create_farm_icon(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Rounded App Icon Background with Radiant Sky Gradient
    corner_r = int(size * 0.22)
    
    # Create mask for rounded square
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=corner_r, fill=255)

    # Base gradient: warm sunny sky to lush green meadow
    bg = Image.new("RGBA", (size, size))
    bg_draw = ImageDraw.Draw(bg)
    for y in range(size):
        ratio = y / size
        if ratio < 0.62:
            # Sunny sky: sky blue (#4dabf7) to warm sunny cream (#ffe066)
            t = ratio / 0.62
            r = int(77 * (1 - t) + 255 * t)
            g = int(171 * (1 - t) + 224 * t)
            b = int(247 * (1 - t) + 102 * t)
        else:
            # Rolling green pasture: lime green (#69db7c) to deep emerald (#2b8a3e)
            t = (ratio - 0.62) / 0.38
            r = int(105 * (1 - t) + 43 * t)
            g = int(219 * (1 - t) + 138 * t)
            b = int(124 * (1 - t) + 62 * t)
        bg_draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    img.paste(bg, (0, 0), mask)

    # Re-obtain draw handle
    draw = ImageDraw.Draw(img)

    # Inner Gold Border
    border_w = max(2, int(size * 0.025))
    draw.rounded_rectangle([border_w, border_w, size - border_w, size - border_w],
                           radius=corner_r - border_w, outline=(255, 235, 153, 220), width=border_w)

    scale = size / 512.0

    # 2. Sun with Warm Radiance in top-right
    sun_x, sun_y, sun_r = int(390 * scale), int(120 * scale), int(65 * scale)
    for i in range(12):
        angle = i * (math.pi / 6)
        r1, r2 = sun_r + int(10 * scale), sun_r + int(28 * scale)
        x1, y1 = sun_x + int(math.cos(angle) * r1), sun_y + int(math.sin(angle) * r1)
        x2, y2 = sun_x + int(math.cos(angle) * r2), sun_y + int(math.sin(angle) * r2)
        draw.line([(x1, y1), (x2, y2)], fill=(255, 212, 59, 200), width=max(2, int(6 * scale)))
    draw.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill=(255, 224, 102, 255), outline=(245, 159, 0, 255), width=max(1, int(3 * scale)))

    # 3. Fluffy Cloud in top-left
    def draw_cloud(cx, cy, cscale):
        s = cscale * scale
        draw.ellipse([cx - 40 * s, cy - 20 * s, cx + 40 * s, cy + 20 * s], fill=(255, 255, 255, 230))
        draw.ellipse([cx - 20 * s, cy - 35 * s, cx + 25 * s, cy + 15 * s], fill=(255, 255, 255, 240))
        draw.ellipse([cx + 10 * s, cy - 25 * s, cx + 55 * s, cy + 15 * s], fill=(255, 255, 255, 230))

    draw_cloud(130 * scale, 110 * scale, 1.1)

    # 4. Cozy Red Barn in Center-Left
    bx, by = int(140 * scale), int(210 * scale)
    bw, bh = int(190 * scale), int(160 * scale)

    # Barn Body
    draw.rectangle([bx, by + int(50 * scale), bx + bw, by + bh], fill=(201, 42, 42, 255), outline=(134, 27, 27, 255), width=max(1, int(3 * scale)))

    # Gambrel Roof
    roof_pts = [
        (bx - int(15 * scale), by + int(52 * scale)),
        (bx + int(35 * scale), by + int(10 * scale)),
        (bx + bw // 2, by - int(18 * scale)),
        (bx + bw - int(35 * scale), by + int(10 * scale)),
        (bx + bw + int(15 * scale), by + int(52 * scale)),
    ]
    draw.polygon(roof_pts, fill=(146, 27, 27, 255), outline=(255, 255, 255, 255))
    draw.line(roof_pts, fill=(255, 255, 255, 255), width=max(2, int(5 * scale)))

    # Roof Cupola & Weathervane
    cx = bx + bw // 2
    draw.rectangle([cx - int(16 * scale), by - int(42 * scale), cx + int(16 * scale), by - int(18 * scale)], fill=(255, 255, 255, 255), outline=(134, 27, 27, 255), width=max(1, int(2 * scale)))
    draw.polygon([(cx - int(20 * scale), by - int(42 * scale)), (cx, by - int(60 * scale)), (cx + int(20 * scale), by - int(42 * scale))], fill=(201, 42, 42, 255))

    # Barn White Corner Trims
    trim_w = max(2, int(8 * scale))
    draw.rectangle([bx, by + int(50 * scale), bx + trim_w, by + bh], fill=(255, 255, 255, 255))
    draw.rectangle([bx + bw - trim_w, by + int(50 * scale), bx + bw, by + bh], fill=(255, 255, 255, 255))

    # Double Barn Doors with White 'X'
    dw, dh = int(70 * scale), int(80 * scale)
    dx = bx + (bw - dw) // 2
    dy = by + bh - dh
    draw.rectangle([dx, dy, dx + dw, dy + dh], fill=(92, 19, 19, 255), outline=(255, 255, 255, 255), width=max(2, int(4 * scale)))
    draw.line([(dx, dy), (dx + dw, dy + dh)], fill=(255, 255, 255, 255), width=max(2, int(4 * scale)))
    draw.line([(dx, dy + dh), (dx + dw, dy)], fill=(255, 255, 255, 255), width=max(2, int(4 * scale)))

    # 5. Golden Wheat Sheaves in Front-Right
    def draw_wheat_ear(wx, wy, rot_deg):
        ear_len = int(80 * scale)
        rad = math.radians(rot_deg)
        # Stem
        ex = wx + int(math.sin(rad) * ear_len)
        ey = wy - int(math.cos(rad) * ear_len)
        draw.line([(wx, wy), (ex, ey)], fill=(217, 130, 43, 255), width=max(2, int(5 * scale)))
        # Grains
        for g in range(6):
            t = (g + 1) / 7.0
            gx = wx + int(math.sin(rad) * ear_len * t)
            gy = wy - int(math.cos(rad) * ear_len * t)
            # Left & right kernels
            perp_rad = rad + math.pi / 2
            kw = int(14 * scale)
            kh = int(8 * scale)
            draw.ellipse([gx - kw, gy - kh, gx + kw, gy + kh], fill=(255, 212, 59, 255), outline=(245, 159, 0, 255), width=max(1, int(2 * scale)))

    draw_wheat_ear(int(360 * scale), int(420 * scale), -25)
    draw_wheat_ear(int(400 * scale), int(430 * scale), 0)
    draw_wheat_ear(int(440 * scale), int(420 * scale), 25)

    # 6. Farmer's Straw Hat in Front Center
    hx, hy = int(220 * scale), int(380 * scale)
    # Brim
    draw.ellipse([hx - int(65 * scale), hy + int(10 * scale), hx + int(65 * scale), hy + int(50 * scale)], fill=(245, 197, 66, 255), outline=(184, 134, 11, 255), width=max(1, int(3 * scale)))
    # Crown
    draw.rounded_rectangle([hx - int(38 * scale), hy - int(25 * scale), hx + int(38 * scale), hy + int(25 * scale)], radius=int(14 * scale), fill=(255, 224, 102, 255), outline=(184, 134, 11, 255), width=max(1, int(3 * scale)))
    # Ribbon
    draw.rounded_rectangle([hx - int(39 * scale), hy + int(10 * scale), hx + int(39 * scale), hy + int(24 * scale)], radius=int(4 * scale), fill=(34, 139, 230, 255))

    # 7. Ribbon Banner at bottom: "3D FARM"
    banner_y = int(435 * scale)
    banner_h = int(52 * scale)
    draw.rounded_rectangle([int(40 * scale), banner_y, size - int(40 * scale), banner_y + banner_h], radius=int(16 * scale), fill=(92, 49, 9, 245), outline=(255, 212, 59, 255), width=max(1, int(3 * scale)))

    # Banner Text
    try:
        font_size = int(28 * scale)
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text = "COZY HAY FARM 3D"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2
    ty = banner_y + (banner_h - th) // 2 - int(2 * scale)
    # text shadow
    draw.text((tx + 2, ty + 2), text, font=font, fill=(0, 0, 0, 180))
    # text fill
    draw.text((tx, ty), text, font=font, fill=(255, 243, 191, 255))

    return img

if __name__ == "__main__":
    icon192 = create_farm_icon(192)
    icon192.save("icon-192.png", "PNG")
    print("Saved icon-192.png")

    icon512 = create_farm_icon(512)
    icon512.save("icon-512.png", "PNG")
    print("Saved icon-512.png")
