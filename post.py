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

print("INSTAGRAM_ACCOUNT_ID:", INSTAGRAM_ACCOUNT_ID)
print("TOKEN LOADED:", len(META_ACCESS_TOKEN) > 20)

# =========================
# GEMINI
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
# FALLBACK
# =========================

if caption is None:
    caption = """
🚀 AI is changing the future.

Discover powerful AI tools that help you learn faster, work smarter, and save time.

Follow for daily AI tips.


#Technology
#Innovation
#MachineLearning
#FutureTech
#Productivity
#Automation
#TechTips
#DigitalMarketing
#Learning
#Startup
#Business
#Growth
"""

print("\n===== CAPTION =====")
print(caption)

# =========================
# IMAGE URL
# =========================

image_url = (
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e"
    "?auto=format&fit=crop&w=1200&q=80"
)

print("\nUsing image:")
print(image_url)

# =========================
# CREATE MEDIA CONTAINER
# =========================

container_url = (
    f"https://graph.facebook.com/v25.0/"
    f"{INSTAGRAM_ACCOUNT_ID}/media"
)

print("\nCreating Instagram media container...")

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

print("Creation ID:", creation_id)

# =========================
# WAIT
# =========================

print("Waiting 15 seconds...")
time.sleep(15)

# =========================
# PUBLISH
# =========================

publish_url = (
    f"https://graph.facebook.com/v25.0/"
    f"{INSTAGRAM_ACCOUNT_ID}/media_publish"
)

print("Publishing post...")

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

