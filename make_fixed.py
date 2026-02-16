from PIL import Image, ImageDraw, ImageFont

font_path = "/tmp/amiri-bold.ttf"
font_big = ImageFont.truetype(font_path, 200)
font_name = ImageFont.truetype(font_path, 44)
font_en = ImageFont.truetype(font_path, 30)

# Use raw unicode without reshaper for short words
letter = 'ص'
name_ar = 'صُحبة'

def cx(draw, text, font, img_w=512):
    bb = draw.textbbox((0,0), text, font=font)
    return (img_w - (bb[2]-bb[0])) // 2

# === Avatar 1: Dark blue + cyan ring ===
img1 = Image.new('RGB', (512, 512), '#1a1a2e')
d1 = ImageDraw.Draw(img1)
d1.ellipse([42, 42, 470, 470], outline='#00d4ff', width=4)
d1.ellipse([56, 56, 456, 456], fill='#0f3460')
d1.text((cx(d1, letter, font_big), 90), letter, fill='#00d4ff', font=font_big)
d1.text((cx(d1, name_ar, font_name), 370), name_ar, fill='#00d4ff', font=font_name)
img1.save('/home/openclaw/.openclaw/workspace/fix1.png')

# === Avatar 2: Purple square ===
img2 = Image.new('RGB', (512, 512), '#1a1a2e')
d2 = ImageDraw.Draw(img2)
d2.rounded_rectangle([30, 30, 482, 482], radius=50, fill='#6c63ff')
d2.text((cx(d2, letter, font_big), 80), letter, fill='white', font=font_big)
d2.text((cx(d2, 'SOHBA', font_en), 400), 'SOHBA', fill='#d4d0ff', font=font_en)
img2.save('/home/openclaw/.openclaw/workspace/fix2.png')

# === Avatar 3: Teal circle ===
img3 = Image.new('RGB', (512, 512), '#0d1117')
d3 = ImageDraw.Draw(img3)
d3.ellipse([56, 56, 456, 456], fill='#00b4d8')
d3.text((cx(d3, letter, font_big), 80), letter, fill='white', font=font_big)
d3.text((cx(d3, name_ar, font_name), 360), name_ar, fill='white', font=font_name)
img3.save('/home/openclaw/.openclaw/workspace/fix3.png')

print("FIXED")
