import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Key present:", bool(os.getenv("OPENAI_API_KEY")))

resp = client.responses.create(
    model="gpt-4.1-mini",
    input="Say 'ok' in one word.",
    timeout=30,
)

print("SUCCESS:", resp.output_text)
