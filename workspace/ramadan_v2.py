from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

font_path = "/tmp/amiri-bold.ttf"
font_title = ImageFont.truetype(font_path, 90)
font_sub = ImageFont.truetype(font_path, 40)
font_small = ImageFont.truetype(font_path, 26)

W, H = 1200, 675
img = Image.new('RGB', (W, H), '#0a0a2e')
d = ImageDraw.Draw(img)

# Rich gradient background - deep navy to dark purple
for y in range(H):
    ratio = y / H
    r = int(8 + 20 * ratio)
    g = int(8 + 5 * ratio)
    b = int(46 - 10 * ratio + 30 * math.sin(ratio * math.pi))
    d.line([(0, y), (W, y)], fill=(r, g, b))

d = ImageDraw.Draw(img)

# Geometric Islamic pattern (top border)
for x in range(0, W, 60):
    # Diamond pattern
    pts = [(x+30, 0), (x+60, 30), (x+30, 60), (x, 30)]
    d.polygon(pts, outline='#ffd70040', fill=None)
    d.polygon(pts, outline=(255, 215, 0, 30))

# Stars - varied sizes and brightness
random.seed(7)
for _ in range(80):
    x = random.randint(0, W)
    y = random.randint(30, H-100)
    size = random.choice([1, 1, 2, 2, 3])
    brightness = random.randint(150, 255)
    d.ellipse([x, y, x+size, y+size], fill=(255, 215, 0, brightness))

# Crescent moon - larger and more elegant
moon_x, moon_y = 950, 80
d.ellipse([moon_x, moon_y, moon_x+180, moon_y+180], fill='#ffd700')
d.ellipse([moon_x+30, moon_y-15, moon_x+195, moon_y+170], fill='#0e0e3a')

# Glow around moon
for i in range(20, 0, -1):
    alpha = int(10 * (20 - i) / 20)
    glow_color = (255, 215, 0, alpha)
    d.ellipse([moon_x-i*2, moon_y-i*2, moon_x+180+i*2, moon_y+180+i*2], outline=(255, 215, 0, max(5, alpha)))

# Hanging lanterns (fawanees) - more detailed
def draw_lantern(draw, cx, top_y, size=1.0):
    s = size
    # Chain
    draw.line([(cx, top_y), (cx, top_y+30*s)], fill='#ffd700', width=2)
    # Top cap
    draw.rounded_rectangle([cx-12*s, top_y+28*s, cx+12*s, top_y+42*s], radius=4, fill='#ffd700')
    # Body
    body_top = top_y + 42*s
    body_bot = top_y + 100*s
    # Lantern body with glow
    draw.rounded_rectangle([cx-18*s, body_top, cx+18*s, body_bot], radius=10, fill='#ffd700', outline='#ffed4a', width=2)
    # Inner glow
    draw.rounded_rectangle([cx-12*s, body_top+6*s, cx+12*s, body_bot-6*s], radius=6, fill='#fff5cc')
    # Bottom
    draw.ellipse([cx-10*s, body_bot-4*s, cx+10*s, body_bot+8*s], fill='#ffd700')

for i, lx in enumerate([80, 200, 340, 860, 1000, 1120]):
    sz = random.uniform(0.8, 1.2)
    draw_lantern(d, lx, -10 + (i%3)*15, sz)

# Ornamental divider
div_y = 480
d.line([(150, div_y), (1050, div_y)], fill='#ffd700', width=1)
# Center ornament on divider
d.ellipse([590, div_y-6, 610, div_y+6], fill='#ffd700')
d.ellipse([560, div_y-3, 572, div_y+3], fill='#ffd700')
d.ellipse([628, div_y-3, 640, div_y+3], fill='#ffd700')

# Main title - رمضان كريم
title = 'رمضان كريم'
bb = d.textbbox((0,0), title, font=font_title)
tw = bb[2] - bb[0]
# Shadow
d.text(((W - tw) // 2 + 3, 203), title, fill='#1a0a00', font=font_title)
# Main
d.text(((W - tw) // 2, 200), title, fill='#ffd700', font=font_title)

# Subtitle
sub = 'كل عام وأنتم بخير'
bb2 = d.textbbox((0,0), sub, font=font_sub)
sw = bb2[2] - bb2[0]
d.text(((W - sw) // 2, 340), sub, fill='#ffffff', font=font_sub)

# Bottom prayer
bottom = 'تقبّل الله منّا ومنكم صالح الأعمال'
bb3 = d.textbbox((0,0), bottom, font=font_small)
bw = bb3[2] - bb3[0]
d.text(((W - bw) // 2, 520), bottom, fill='#c8b080', font=font_small)

# Bottom border pattern
for x in range(0, W, 40):
    d.arc([x, H-30, x+40, H+10], 0, 180, fill='#ffd70050', width=1)

img.save('/home/openclaw/.openclaw/workspace/ramadan_v2.png', quality=95)
print("DONE")
