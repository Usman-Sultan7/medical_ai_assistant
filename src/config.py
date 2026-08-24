import os
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Form options
GENDER_OPTIONS = ["Male", "Female", "Other", "Prefer not to say"]
DURATION_OPTIONS = ["Less than 1 day", "1-3 days", "4-7 days", "1-2 weeks", "More than 2 weeks"]
LANGUAGE_OPTIONS = ["English", "Urdu", "Spanish", "French"]
SYMPTOMS_LIST = ["Fever", "Cough", "Headache", "Sore throat", "Chest pain", "Shortness of breath", "Fatigue", "Nausea"]

# Mandatory Safety Disclaimer
MEDICAL_DISCLAIMER = """
⚠️ **IMPORTANT MEDICAL & SAFETY NOTICE**
This application is an educational AI prototype only. It is NOT a replacement for a licensed doctor, professional diagnosis, emergency service, or medical treatment. It does not present a confirmed diagnosis. Always consult a qualified healthcare professional and seek emergency help in urgent situations.
"""