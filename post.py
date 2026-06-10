import os
import re
import time
import feedparser
import requests

# ఎన్విరాన్మెంట్ వేరియబుల్స్
META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
INSTAGRAM_ACCOUNT_ID = os.environ["INSTAGRAM_ACCOUNT_ID"]

# RSS ఫీడ్స్ లిస్ట్
RSS_FEEDS = [
    "https://www.123telugu.com/feed",
    "https://www.gulte.com/feed"
]

POSTED_FILE = "posted_news.txt"

# బ్యాక్‌గ్రౌండ్ ఇమేజ్ URL
image_url = None

if "media_content" in item:
    image_url = item.media_content[0]["url"]


def load_posted():
    """ఇంతకుముందు పోస్ట్ చేసిన లింకులను లోడ్ చేస్తుంది"""
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_posted(link):
    """పోస్ట్ చేసిన లింక్‌ను ఫైల్‌లో సేవ్ చేస్తుంది"""
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")


def clean_html(raw_html):
    """సమ్మరీలో ఉండే HTML ట్యాగ్‌లను క్లీన్ చేయడానికి"""
    clean_text = re.sub(r'<.*?>', '', raw_html)
    return clean_text


def latest_news():
    """ఫీడ్ నుండి సరికొత్త వార్తను తీసుకుంటుంది"""
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

                # కొత్త వార్త దొరికిన వెంటనే రిటర్న్ చేస్తుంది
                raw_summary = getattr(item, "summary", "")
                return {
                    "title": getattr(item, "title", ""),
                    "summary": clean_html(raw_summary),
                    "link": link
                }

        except Exception as e:
            print("Feed Error:", str(e))

    return None


# మెయిన్ ప్రోగ్రామ్ రన్ చేయడం
news = latest_news()

if not news:
    print("కొత్త Tollywood వార్తలు ఏమీ దొరకలేదు.")
    raise SystemExit(0)

# ఇన్‌స్టాగ్రామ్ క్యాప్షన్ ఫార్మాట్
caption = f"""
🎬 {news['title']}

{news['summary'][:400]}...

What do you think about this update?

Follow for daily Tollywood movie news.

#Tollywood #TeluguCinema #MovieNews #TeluguMovies #TollywoodUpdates
#CinemaNews #MovieUpdate #TeluguFilmIndustry #MovieBuzz #FilmNews
#Entertainment #SouthCinema #TollywoodFans #LatestNews #Trending
"""

print("Posting to Instagram:")
print(news["title"])

# 1. మీడియా కంటైనర్ క్రియేట్ చేయడం
container = requests.post(
    f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media",
    data={
        "image_url": IMAGE_URL,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
)

container_json = container.json()
print("Container Response:", container_json)

if "id" not in container_json:
    raise Exception(f"Container creation failed: {container_json}")

creation_id = container_json["id"]

# ఫేస్‌బుక్ సర్వర్ ఇమేజ్ ప్రాసెస్ చేయడానికి 15 సెకన్లు ఆగడం
print("Waiting 15 seconds...")
time.sleep(15)

# 2. కంటైనర్‌ను పబ్లిష్ చేయడం
publish = requests.post(
    f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media_publish",
    data={
        "creation_id": creation_id,
        "access_token": META_ACCESS_TOKEN
    }
)

publish_json = publish.json()
print("Publish Response:", publish_json)

if "id" in publish_json:
    save_posted(news["link"])
    print("SUCCESS: పోస్ట్ విజయవంతంగా అప్‌లోడ్ అయ్యింది!")
else:
    raise Exception(f"Publish failed: {publish_json}")
