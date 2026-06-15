import google.generativeai as genai

# --- PASTE YOUR API KEY HERE ---
GOOGLE_API_KEY = "AIzaSyDn5aG-5WOX-RiDGYWwinsF9gIWF6QQ7c8"
genai.configure(api_key=GOOGLE_API_KEY)

# List of common model names to try
possible_models = [
    'gemini-1.5-flash',
    'gemini-pro',
    'gemini-1.0-pro',
    'gemini-1.5-pro'
]

print("--- STARTING TEST ---")

for model_name in possible_models:
    print(f"\nTesting: {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"✅ SUCCESS! The working model name is: '{model_name}'")
        print(f"Response: {response.text}")
        break # Stop after finding the first working one
    except Exception as e:
        print(f"❌ Failed: {e}")

print("\n--- TEST FINISHED ---")