import os
import time
import requests
import feedparser
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
# CONFIG
# =========================

RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/startups/feed/",
    "https://www.socialmediatoday.com/feeds/news/"
]

POSTED_FILE = "posted_news.txt"

IMAGE_URL = (
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e"
    "?auto=format&fit=crop&w=1200&q=80"
)

# =========================
# NEWS HISTORY
# =========================

def get_posted_links():
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_posted_link(link):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")


# =========================
# GET LATEST NEWS
# =========================

def get_latest_news():
    posted = get_posted_links()

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for item in feed.entries:
                link = getattr(item, "link", "")

                if not link:
                    continue

                if link in posted:
                    continue

                return {
                    "title": getattr(item, "title", ""),
                    "summary": getattr(item, "summary", ""),
                    "link": link
                }

        except Exception as e:
            print("Feed error:", str(e))

    return None


# =========================
# FETCH NEWS
# =========================

news = get_latest_news()

if news:
    print("\nLATEST NEWS:")
    print(news["title"])
else:
    print("No new news found.")

# =========================
# GEMINI
# =========================

client = genai.Client(api_key=GEMINI_API_KEY)

caption = None

for attempt in range(3):
    try:

        if news:
            prompt = f"""
Latest trending technology news:

Title:
{news['title']}

Summary:
{news['summary']}

Create an Instagram post.

Rules:
- Explain in simple language
- Why this matters
- Add motivation/inspiration
- Make it engaging
- Maximum 180 words
- Add CTA
- Add 15 hashtags
"""
        else:
            prompt = """
Create an Instagram post about AI, startups,
technology, digital marketing, productivity,
or innovation.

Requirements:
- Motivational
- Engaging
- 15 hashtags
- Max 180 words
"""

        print("Generating content with Gemini...")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
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
🚀 Technology is changing the future.

The biggest opportunities often come from embracing new tools,
new ideas, and continuous learning.

Stay curious.
Stay innovative.

Follow for daily tech insights.

#Technology
#Innovation
#AI
#Startup
#Business
#DigitalMarketing
#Automation
#Productivity
#MachineLearning
#FutureTech
#Growth
#Entrepreneur
#Learning
#Success
#TechNews
"""

print("\n===== CAPTION =====")
print(caption)

# =========================
# CREATE CONTAINER
# =========================

container_url = (
    f"https://graph.facebook.com/v25.0/"
    f"{INSTAGRAM_ACCOUNT_ID}/media"
)

print("\nCreating Instagram media container...")

container_response = requests.post(
    container_url,
    data={
        "image_url": IMAGE_URL,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
)

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

print(publish_response.text)

publish_json = publish_response.json()

if "id" in publish_json:

    if news:
        save_posted_link(news["link"])

    print("\nSUCCESS!")
    print("Instagram post published.")

else:
    raise Exception(
        f"Publish failed:\n{publish_response.text}"
    )
