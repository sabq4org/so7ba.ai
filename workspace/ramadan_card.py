from PIL import Image, ImageDraw, ImageFont, ImageFilter

font_path = "/tmp/amiri-bold.ttf"
font_title = ImageFont.truetype(font_path, 72)
font_sub = ImageFont.truetype(font_path, 36)
font_small = ImageFont.truetype(font_path, 28)

# Landscape card 1200x675
W, H = 1200, 675
img = Image.new('RGB', (W, H), '#0a1628')
d = ImageDraw.Draw(img)

# Background gradient effect - dark blue to purple
for y in range(H):
    r = int(10 + (30 * y / H))
    g = int(22 + (10 * y / H))
    b = int(40 + (60 * y / H))
    d.line([(0, y), (W, y)], fill=(r, g, b))

d = ImageDraw.Draw(img)

# Decorative circles (moon-like)
d.ellipse([850, 60, 1050, 260], fill='#ffd700')
d.ellipse([870, 50, 1060, 250], fill='#0f1f3d')  # crescent effect

# Stars
import random
random.seed(42)
for _ in range(50):
    x = random.randint(0, W)
    y = random.randint(0, H//2)
    size = random.randint(1, 3)
    d.ellipse([x, y, x+size, y+size], fill='#ffd700')

# Decorative line
d.line([(100, 500), (1100, 500)], fill='#ffd700', width=2)

# Main text
title = 'رمضان كريم'
bb = d.textbbox((0,0), title, font=font_title)
tw = bb[2] - bb[0]
d.text(((W - tw) // 2, 200), title, fill='#ffd700', font=font_title)

# Subtitle
sub = 'كل عام وأنتم بخير'
bb2 = d.textbbox((0,0), sub, font=font_sub)
sw = bb2[2] - bb2[0]
d.text(((W - sw) // 2, 320), sub, fill='white', font=font_sub)

# Bottom text
bottom = 'أعاده الله عليكم بالخير واليُمن والبركات'
bb3 = d.textbbox((0,0), bottom, font=font_small)
bw = bb3[2] - bb3[0]
d.text(((W - bw) // 2, 530), bottom, fill='#c0c0c0', font=font_small)

# Lantern shapes (simple)
for lx in [150, 350, 550, 750, 950]:
    d.rounded_rectangle([lx, 20, lx+40, 80], radius=8, fill='#ffd700', outline='#ffd700')
    d.line([(lx+20, 0), (lx+20, 20)], fill='#ffd700', width=2)
    d.ellipse([lx+5, 70, lx+35, 100], fill='#ffd700')

img.save('/home/openclaw/.openclaw/workspace/ramadan_card.png', quality=95)
print("DONE")
