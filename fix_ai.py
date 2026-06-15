import google.generativeai as genai

# --- PASTE YOUR API KEY HERE --- 
GOOGLE_API_KEY = "API KEY"
genai.configure(api_key=GOOGLE_API_KEY)

print("--- SEARCHING FOR WORKING MODELS ---")

found_any = False

# 1. Ask Google for list of all models
for m in genai.list_models():
    # Only look for models that can chat (generateContent)
    if 'generateContent' in m.supported_generation_methods:
        model_name = m.name # e.g., 'models/gemini-pro'
        print(f"\nTesting: {model_name}...")
        
        try:
            # 2. Try to actually use it
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            
            print(f"✅ SUCCESS! It works!")
            print(f"👇 COPY THIS LINE INTO app.py 👇")
            print(f"model = genai.GenerativeModel('{model_name}')")
            found_any = True
            break # Stop after finding the first working one
            
        except Exception as e:
            print(f"❌ Failed: {e}")

if not found_any:
    print("\n❌ NO WORKING MODELS FOUND. Your API Key might be invalid or not enabled for Generative AI.")
