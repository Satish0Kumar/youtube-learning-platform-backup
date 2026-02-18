import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

key = os.getenv('GEMINI_API_KEY')
print('Key found:', bool(key))
print('Key starts with:', key[:15] if key else 'NONE')
print('Key length:', len(key) if key else 0)

if not key:
    print("❌ No API key found in .env!")
else:
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents='Say hello in one word'
        )
        print('✅ API Working! Response:', response.text)
    except Exception as e:
        print('❌ API Error:', str(e))
