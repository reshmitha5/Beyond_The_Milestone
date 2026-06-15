import google.generativeai as genai

# Your Key
KEY = "AIzaSyDn5aG-5WOX-RiDGYWwinsF9gIWF6QQ7c8" 
genai.configure(api_key=KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')
print("--- DIAGNOSING YOUR KEY ---")

try:
    # 1. List all models available to your key
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if not available_models:
        print("❌ No models found for this key. You might need to enable the Gemini API in Google Cloud Console.")
    else:
        print(f"Found {len(available_models)} possible models: {available_models}")
        
        # 2. Try each one automatically
        for m_name in available_models:
            print(f"Testing {m_name}...")
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content("Hi")
                print(f"✅ SUCCESS! This one works: {m_name}")
                print(f"Response: {response.text}")
                print(f"\nCOPY THIS TO app.py: model = genai.GenerativeModel('{m_name}')")
                exit() # Stop once we find one!
            except Exception as e:
                print(f"   - {m_name} failed: {e}")

except Exception as e:
    print(f"❌ Could not even list models. Error: {e}")