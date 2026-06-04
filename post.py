from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Generate an Instagram caption and 15 hashtags about AI tools."
)

print(response.text)
