import requests
import base64
import json

API_KEY = "[REDACTED:GOOGLE_API_KEY]"

# Use Imagen 4 for the caricature
url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key={API_KEY}"

prompt = """A fun colorful caricature illustration of a confident Saudi Arabian man in his 40s, wearing a white thobe and red-white checkered shemagh (ghutra) with black agal. He has a warm smile with a mustache and goatee. 

He is sitting like a boss in a high-tech newsroom command center, surrounded by multiple glowing screens showing breaking news headlines in Arabic. In one hand he holds a V60 pour-over coffee cup, in the other hand a smartphone buzzing with notifications. 

Around him: stacks of newspapers, a "SABQ" logo on the wall, an AI robot assistant floating beside him carrying documents, a clock showing "BREAKING NEWS" time. His desk has 5 screens, each showing different news channels. 

Style: exaggerated caricature art, big head, small body, vibrant colors, humorous editorial cartoon style, professional newsroom setting with a comedic twist. The character looks like he's juggling 100 tasks at once but doing it with a cool confident smile."""

payload = {
    "instances": [{"prompt": prompt}],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "1:1"
    }
}

headers = {"Content-Type": "application/json"}
resp = requests.post(url, headers=headers, json=payload, timeout=60)
print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    if "predictions" in data and len(data["predictions"]) > 0:
        img_b64 = data["predictions"][0]["bytesBase64Encoded"]
        with open("caricature_abu_mohammed.png", "wb") as f:
            f.write(base64.b64decode(img_b64))
        print("SUCCESS: saved caricature_abu_mohammed.png")
    else:
        print(f"No predictions: {json.dumps(data, indent=2)[:500]}")
else:
    print(f"Error: {resp.text[:500]}")
