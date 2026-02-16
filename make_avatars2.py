from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

font_path = "/tmp/amiri-bold.ttf"

def shape(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def center_text(draw, img_size, text, font, y_offset=0):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = (img_size - tw) // 2
    y = (img_size - th) // 2 + y_offset
    return x, y

sizes = [160, 180, 200, 240]
for s in sizes:
    try:
        f = ImageFont.truetype(font_path, s)
        img = Image.new('RGB', (100, 100), 'white')
        d = ImageDraw.Draw(img)
        txt = shape('ص')
        bb = d.textbbox((0,0), txt, font=f)
        print(f"Size {s}: bbox={bb}, w={bb[2]-bb[0]}, h={bb[3]-bb[1]}")
    except Exception as e:
        print(f"Size {s}: ERROR {e}")

# Test render
img = Image.new('RGB', (512, 512), '#0f3460')
d = ImageDraw.Draw(img)
font_big = ImageFont.truetype(font_path, 200)
font_name = ImageFont.truetype(font_path, 48)
letter = shape('ص')
d.text((150, 80), letter, fill='#00d4ff', font=font_big)
name = shape('صُحبة')
d.text((160, 380), name, fill='#00d4ff', font=font_name)
img.save('/home/openclaw/.openclaw/workspace/test_ar.png')
print("Test saved")
