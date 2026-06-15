import google.generativeai as genai

# PASTE YOUR API KEY HERE
GOOGLE_API_KEY = "AIzaSyDn5aG-5WOX-RiDGYWwinsF9gIWF6QQ7c8"

genai.configure(api_key=GOOGLE_API_KEY)

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"FOUND MODEL: {m.name}")
except Exception as e:
    print(f"Error: {e}")