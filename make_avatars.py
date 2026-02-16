from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

font_path = "/tmp/cairo.ttf"
font_big = ImageFont.truetype(font_path, 220)
font_med = ImageFont.truetype(font_path, 50)
font_sm = ImageFont.truetype(font_path, 36)

def shape(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

# Avatar 1: Dark blue circle, cyan accent
img = Image.new('RGB', (512, 512), '#1a1a2e')
d = ImageDraw.Draw(img)
d.ellipse([46, 46, 466, 466], outline='#00d4ff', width=4)
d.ellipse([56, 56, 456, 456], fill='#0f3460')
txt = shape('ص')
bb = d.textbbox((0,0), txt, font=font_big)
tw, th = bb[2]-bb[0], bb[3]-bb[1]
d.text(((512-tw)//2, (512-th)//2 - 30), txt, fill='#00d4ff', font=font_big)
name = shape('صُحبة')
bb2 = d.textbbox((0,0), name, font=font_sm)
nw = bb2[2]-bb2[0]
d.text(((512-nw)//2, 400), name, fill='rgba(0,212,255,200)', font=font_sm)
img.save('/home/openclaw/.openclaw/workspace/ar_avatar1.png')

# Avatar 2: Purple rounded
img2 = Image.new('RGB', (512, 512), '#1a1a2e')
d2 = ImageDraw.Draw(img2)
d2.rounded_rectangle([30, 30, 482, 482], radius=50, fill='#6c63ff')
txt2 = shape('ص')
bb = d2.textbbox((0,0), txt2, font=font_big)
tw, th = bb[2]-bb[0], bb[3]-bb[1]
d2.text(((512-tw)//2, (512-th)//2 - 30), txt2, fill='white', font=font_big)
name2 = "S O H B A"
bb3 = d2.textbbox((0,0), name2, font=font_sm)
nw2 = bb3[2]-bb3[0]
d2.text(((512-nw2)//2, 410), name2, fill='rgba(255,255,255,180)', font=font_sm)
img2.save('/home/openclaw/.openclaw/workspace/ar_avatar2.png')

# Avatar 3: Teal circle
img3 = Image.new('RGB', (512, 512), '#0d1117')
d3 = ImageDraw.Draw(img3)
d3.ellipse([56, 56, 456, 456], fill='#00b4d8')
txt3 = shape('ص')
bb = d3.textbbox((0,0), txt3, font=font_big)
tw, th = bb[2]-bb[0], bb[3]-bb[1]
d3.text(((512-tw)//2, (512-th)//2 - 30), txt3, fill='white', font=font_big)
name3 = shape('صُحبة')
bb4 = d3.textbbox((0,0), name3, font=font_med)
nw3 = bb4[2]-bb4[0]
d3.text(((512-nw3)//2, 380), name3, fill='rgba(255,255,255,200)', font=font_med)
img3.save('/home/openclaw/.openclaw/workspace/ar_avatar3.png')

print("DONE")
