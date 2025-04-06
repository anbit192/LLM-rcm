from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
EMBED_MODEL=os.getenv("EMBED_MODEL")
GEN_MODEL=os.getenv("GEN_MODEL")
OUTPUT_DIMENSION=os.getenv("OUTPUT_DIMENSION")

MONGODB_URL=os.getenv("MONGODB_URL")

