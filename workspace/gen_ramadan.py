from google import genai
from google.genai import types
import base64

client = genai.Client(api_key="[REDACTED:GOOGLE_API_KEY_2]")

# Try Imagen first
try:
    result = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt="Professional Ramadan Kareem greeting card, landscape orientation, dark navy blue background with golden crescent moon, elegant hanging lanterns (fawanees), Islamic geometric patterns, stars, Arabic calligraphy text 'رمضان كريم' in gold, subtitle 'كل عام وأنتم بخير' in white, luxurious and elegant design, high quality",
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
        )
    )
    
    for i, img in enumerate(result.generated_images):
        with open(f'/home/openclaw/.openclaw/workspace/ramadan_ai_{i}.png', 'wb') as f:
            f.write(img.image.image_bytes)
        print(f"Imagen saved: ramadan_ai_{i}.png")

except Exception as e:
    print(f"Imagen error: {e}")
    
    # Fallback to Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents="Generate a professional Ramadan Kareem greeting card image. Landscape orientation, dark navy blue background with golden crescent moon, elegant hanging lanterns, Islamic geometric patterns, stars. Include Arabic calligraphy text 'رمضان كريم' in gold and 'كل عام وأنتم بخير' in white. Luxurious and elegant design.",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            )
        )
        
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open('/home/openclaw/.openclaw/workspace/ramadan_ai_0.png', 'wb') as f:
                    f.write(part.inline_data.data)
                print("Gemini image saved!")
            elif part.text:
                print(f"Text: {part.text}")
    except Exception as e2:
        print(f"Gemini error: {e2}")
