import os
import requests
from google import genai

# Secrets
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]

# Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Generate caption
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""
Create an Instagram post about AI tools.

Give:
1. Caption
2. 15 hashtags
"""
)

caption = response.text

print("Generated caption:")
print(caption)

# Generate image
image_url = "https://image.pollinations.ai/prompt/futuristic%20AI%20workspace"

# Create media container
container_url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media"

container_response = requests.post(
    container_url,
    data={
        "image_url": image_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
)

print(container_response.text)

creation_id = container_response.json()["id"]

# Publish post
publish_url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"

publish_response = requests.post(
    publish_url,
    data={
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }
)

print(publish_response.text)
