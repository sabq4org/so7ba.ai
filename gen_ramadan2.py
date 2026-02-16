from google import genai
from google.genai import types

client = genai.Client(api_key="[REDACTED:GOOGLE_API_KEY_2]")

# Try gemini-2.5-flash-image
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents="Generate a beautiful professional Ramadan Kareem greeting card image. Landscape 16:9, dark navy background, golden crescent moon, hanging lanterns, Islamic patterns, Arabic text 'رمضان كريم' in gold calligraphy, 'كل عام وأنتم بخير' in white. Elegant luxurious design.",
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
    )
    
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            with open('/home/openclaw/.openclaw/workspace/ramadan_ai_0.png', 'wb') as f:
                f.write(part.inline_data.data)
            print("Image saved!")
        elif part.text:
            print(f"Text: {part.text}")
except Exception as e:
    print(f"Error 1: {e}")

# Try gemini-3-pro
try:
    response2 = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Generate a beautiful Ramadan greeting card image",
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )
    )
    for part in response2.candidates[0].content.parts:
        if part.inline_data:
            with open('/home/openclaw/.openclaw/workspace/ramadan_ai_1.png', 'wb') as f:
                f.write(part.inline_data.data)
            print("Image 2 saved!")
except Exception as e2:
    print(f"Error 2: {e2}")
