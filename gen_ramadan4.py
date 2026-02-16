from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyDXUmfShZDCqPlqO1jHd_BdhGdGBu4Y1ck")

prompt = "Create a stunning professional Ramadan Kareem greeting card. Landscape orientation 16:9. Dark navy blue night sky background with golden crescent moon, elegant hanging traditional lanterns (fawanees) with warm glow, Islamic geometric arabesque patterns, scattered golden stars. Beautiful Arabic calligraphy text 'رمضان كريم' prominently in gold, with 'كل عام وأنتم بخير' below in white. Luxurious, elegant, high quality design suitable for sharing."

# Try gemini-3-pro-image-preview (Nano Banana Pro)
print("Trying gemini-3-pro-image-preview...")
try:
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
    )
    
    saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            mime = part.inline_data.mime_type or 'image/png'
            ext = 'png' if 'png' in mime else 'jpg'
            path = f'/home/openclaw/.openclaw/workspace/ramadan_gen.{ext}'
            with open(path, 'wb') as f:
                f.write(part.inline_data.data)
            print(f"SUCCESS! Saved {path} ({len(part.inline_data.data)} bytes, {mime})")
            saved = True
        elif part.text:
            print(f"Text: {part.text[:200]}")
    
    if not saved:
        print("No image in response")
        
except Exception as e:
    print(f"Error: {e}")
