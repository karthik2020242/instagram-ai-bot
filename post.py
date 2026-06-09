import os
import time
import feedparser
import requests

META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]

RSS_FEEDS = [
"https://www.123telugu.com/feed",
"https://www.gulte.com/feed"
]

POSTED_FILE = "posted_news.txt"

IMAGE_URL = (
"https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"
"?auto=format&fit=crop&w=1200&q=80"
)

def load_posted():
try:
with open(POSTED_FILE, "r", encoding="utf-8") as f:
return set(line.strip() for line in f if line.strip())
except FileNotFoundError:
return set()

def save_posted(link):
with open(POSTED_FILE, "a", encoding="utf-8") as f:
f.write(link + "\n")

def latest_news():
posted = load_posted()

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
        print("Feed Error:", e)

return None

news = latest_news()

if not news:
print("No new Tollywood news found.")
raise SystemExit(0)

caption = f"""
🎬 {news['title']}

{news['summary'][:400]}

What do you think about this update?

Follow for daily Tollywood movie news.

#Tollywood
#TeluguCinema
#MovieNews
#TeluguMovies
#TollywoodUpdates
#CinemaNews
#MovieUpdate
#TeluguFilmIndustry
#MovieBuzz
#FilmNews
#Entertainment
#SouthCinema
#TollywoodFans
#LatestNews
#Trending
"""

container = requests.post(
f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media",
data={
"image_url": IMAGE_URL,
"caption": caption,
"access_token": META_ACCESS_TOKEN
}
).json()

print(container)

if "id" not in container:
raise Exception(str(container))

creation_id = container["id"]

time.sleep(15)

publish = requests.post(
f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media_publish",
data={
"creation_id": creation_id,
"access_token": META_ACCESS_TOKEN
}
).json()

print(publish)

if "id" in publish:
save_posted(news["link"])
print("SUCCESS")
else:
raise Exception(str(publish))
