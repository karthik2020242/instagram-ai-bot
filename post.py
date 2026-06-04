from google import genai
import os

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""
Generate:
1 Instagram caption
15 hashtags

Topic: AI tools for students
"""
)

print("\n===== GEMINI OUTPUT =====\n")
print(response.text)
