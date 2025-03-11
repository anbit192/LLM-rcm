from google import genai
from config import *

def get_google_model():
    client = genai.Client(api_key=GEMINI_API_KEY)
    return client