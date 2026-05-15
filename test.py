import google.generativeai as genai
import os

# ----------------------------
# CONFIGURE YOUR API KEY HERE
# ----------------------------
GEMINI_API_KEY = "AIzaSyDLaicHwSIgprNa6ff0nIhHuswhCDiDju0"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✓ Gemini API key configured successfully.\n")

    # List available models
    print("Fetching available models...\n")
    models = genai.list_models()

    available_models = []
    for model in models:
        # Only include models that support text generation or chat
        if "generateContent" in model.supported_generation_methods:
            available_models.append(model.name)

    if available_models:
        print("✅ Available Gemini Models:")
        for i, m in enumerate(available_models, start=1):
            print(f"{i}. {m}")
    else:
        print("⚠️ No generative models found for your key.")

except Exception as e:
    print("❌ Error:", e)
