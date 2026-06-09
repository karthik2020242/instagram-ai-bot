import os
import time
import requests
import feedparser
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]

RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/startups/feed/",
    "https://www.socialmediatoday.com/feeds/news/",
]

POSTED_FILE = "posted_news.txt"

def get_posted_links():
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_posted_link(link):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\\n")

def get_latest_news():
    posted = get_posted_links()

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for item in feed.entries:
                link = getattr(item, "link", "")

                if not link or link in posted:
                    continue

                return {
                    "title": getattr(item, "title", ""),
                    "summary": getattr(item, "summary", ""),
                    "link": link,
                }

        except Exception as e:
            print("Feed error:", e)

    return None

news = get_latest_news()

if not news:
    print("No new news found.")
    raise SystemExit(0)

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = f"""
NEWS TITLE:
{news['title']}

NEWS SUMMARY:
{news['summary']}

Create an Instagram post.

Requirements:
- Explain what happened
- Why it matters
- Motivational tone
- Easy language
- CTA
- 15 hashtags
- Maximum 180 words
- Focus only on this news
"""

caption = None

for attempt in range(3):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        caption = response.text
        break
    except Exception as e:
        print("Gemini error:", e)
        time.sleep(20)

if not caption:
    caption = f"🚀 {news['title']}\\n\\nStay updated with technology."

IMAGE_URL = "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=1200&q=80"

container_url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media"

container_response = requests.post(
    container_url,
    data={
        "image_url": IMAGE_URL,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
)

container_json = container_response.json()

if "id" not in container_json:
    raise Exception(container_response.text)

creation_id = container_json["id"]

time.sleep(15)

publish_url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"

publish_response = requests.post(
    publish_url,
    data={
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }
)

publish_json = publish_response.json()

if "id" in publish_json:
    save_posted_link(news["link"])
    print("SUCCESS")
else:
    raise Exception(publish_response.text)
