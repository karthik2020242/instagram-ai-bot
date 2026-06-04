from google import genai
import os

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""
Generate:
1 Instagram caption
15 hashtags

Topic: AI tools
"""
)

print(response.text)
