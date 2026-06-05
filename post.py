import os
import time
import requests
from google import genai

# =========================
# SECRETS
# =========================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]

# =========================
# GEMINI CLIENT
# =========================

client = genai.Client(api_key=GEMINI_API_KEY)

caption = None

print("Generating content with Gemini...")

for attempt in range(3):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="""
Create an Instagram post about AI tools.

Requirements:
- Engaging caption
- 15 hashtags
- Maximum 150 words
"""
        )

        caption = response.text
        print("Gemini content generated successfully.")
        break

    except Exception as e:
        print(f"Attempt {attempt + 1} failed:")
        print(str(e))

        if attempt < 2:
            print("Waiting 30 seconds...")
            time.sleep(30)

# =========================
# FALLBACK CAPTION
# =========================

if caption is None:
    print("Using fallback caption...")

    caption = """
🚀 AI is transforming the future.

Discover powerful AI tools that help you learn faster, work smarter, and save time.

Follow for daily AI tips and tools.

#AI
#AITools
#ArtificialIntelligence
#Technology
#Innovation
#MachineLearning
#FutureTech
#Productivity
#Automation
#DigitalMarketing
#TechTips
#AICommunity
#TechNews
#Startup
#Learning
"""

print("\n===== CAPTION =====\n")
print(caption)

# =========================
# IMAGE URL
# =========================

image_url = (
    "https://image.pollinations.ai/prompt/"
    "futuristic%20artificial%20intelligence%20workspace"
)

print("\nCreating Instagram media container...")

# =========================
# CREATE MEDIA CONTAINER
# =========================

container_url = (
    f"https://graph.facebook.com/v25.0/"
    f"{INSTAGRAM_ACCOUNT_ID}/media"
)

container_response = requests.post(
    container_url,
    data={
        "image_url": image_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
)

print("Container response:")
print(container_response.text)

container_json = container_response.json()

if "id" not in container_json:
    raise Exception(
        f"Container creation failed:\n{container_response.text}"
    )

creation_id = container_json["id"]

print(f"Creation ID: {creation_id}")

# =========================
# WAIT BEFORE PUBLISH
# =========================

print("Waiting 15 seconds before publish...")
time.sleep(15)

# =========================
# PUBLISH POST
# =========================

publish_url = (
    f"https://graph.facebook.com/v25.0/"
    f"{INSTAGRAM_ACCOUNT_ID}/media_publish"
)

publish_response = requests.post(
    publish_url,
    data={
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }
)

print("Publish response:")
print(publish_response.text)

publish_json = publish_response.json()

if "id" in publish_json:
    print("\nSUCCESS!")
    print("Instagram post published.")
else:
    raise Exception(
        f"Publish failed:\n{publish_response.text}"
    )
