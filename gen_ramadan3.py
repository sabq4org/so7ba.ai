from google import genai
from google.genai import types
import time

client = genai.Client(api_key="AIzaSyDXUmfShZDCqPlqO1jHd_BdhGdGBu4Y1ck")

models_to_try = [
    "gemini-2.5-flash-image",
    "gemini-3-pro-image-preview",
    "gemini-2.0-flash-exp-image-generation",
]

prompt = "Create a stunning professional Ramadan Kareem greeting card. Landscape orientation 16:9. Dark navy blue night sky background with golden crescent moon, elegant hanging traditional lanterns (fawanees) with warm glow, Islamic geometric arabesque patterns, scattered golden stars. Beautiful Arabic calligraphy text 'رمضان كريم' prominently in gold, with 'كل عام وأنتم بخير' below in white. Luxurious, elegant, high quality design suitable for sharing."

for model in models_to_try:
    try:
        print(f"Trying {model}...")
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )
        
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                ext = 'png' if 'png' in (part.inline_data.mime_type or '') else 'jpg'
                path = f'/home/openclaw/.openclaw/workspace/ramadan_ai.{ext}'
                with open(path, 'wb') as f:
                    f.write(part.inline_data.data)
                print(f"SUCCESS with {model}! Saved to {path}")
            elif part.text:
                print(f"Text: {part.text[:100]}")
        break
    except Exception as e:
        print(f"{model} failed: {str(e)[:200]}")
        time.sleep(2)
