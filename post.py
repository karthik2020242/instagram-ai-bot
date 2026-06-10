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

# డిఫాల్ట్ ఇమేజ్ (ఫీడ్‌లో ఇమేజ్ దొరక్కపోతే ఇది వాడుతుంది)
DEFAULT_IMAGE_URL = (
    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"
    "?auto=format&fit=crop&w=1200&q=80"
)


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
    if not raw_html:
        return ""
    clean_text = re.sub(r'<.*?>', '', raw_html)
    return clean_text.strip()


def extract_image(item):
    """ఆర్టికల్ నుండి ఇమేజ్ URLని వెతికి పట్టుకుంటుంది (Best Approach)"""
    
    # 1. మీరు చెప్పినట్టు media_content లో ఉందేమో చూస్తుంది
    if "media_content" in item and len(item.media_content) > 0:
        if "url" in item.media_content[0]:
            return item.media_content[0]["url"]

    # 2. ఒకవేళ ఫీడ్స్ ఎన్‌క్లోజర్స్‌లో ఇమేజ్ ఉంటే (కొన్ని సైట్లలో ఇలా ఉంటుంది)
    if "enclosures" in item and len(item.enclosures) > 0:
        for enc in item.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href")

    # 3. ఒకవేళ ఆర్టికల్ లింక్స్ లో ఇమేజ్ ఉంటే
    if "links" in item:
        for link in item.links:
            if link.get("type", "").startswith("image/"):
                return link.get("href")

    # 4. ఒకవేళ సమ్మరీ/డిస్క్రిప్షన్ లోపల <img src="..."> ట్యాగ్ ఉంటే దాన్ని లాగుతుంది
    summary = getattr(item, "summary", "")
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', summary)
    if img_match:
        return img_match.group(1)

    return None


def latest_news():
    """ఫీడ్ నుండి సరికొత్త వార్తను మరియు దాని ఇమేజ్‌ను తీసుకుంటుంది"""
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

                # ఇమేజ్ ఉందో లేదో చెక్ చేస్తుంది
                image_url = extract_image(item)
                
                # ఇమేజ్ దొరక్కపోతే డిఫాల్ట్ ఇమేజ్ సెట్ చేస్తుంది
                if not image_url:
                    image_url = DEFAULT_IMAGE_URL

                raw_summary = getattr(item, "summary", "")
                
                return {
                    "title": getattr(item, "title", ""),
                    "summary": clean_html(raw_summary),
                    "link": link,
                    "image_url": image_url
                }

        except Exception as e:
            print(f"Feed Error ({feed_url}):", str(e))

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
print("Title:", news["title"])
print("Image URL:", news["image_url"])

# 1. మీడియా కంటైనర్ క్రియేట్ చేయడం (ఆర్టికల్ ఇమేజ్‌తో)
container = requests.post(
    f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media",
    data={
        "image_url": news["image_url"],
        "caption": caption,
        "access_token": META_ACCESS_TOKEN
    }
)

container_json = container.json()
print("Container Response:", container_json)

if "id" not in container_json:
    raise Exception(f"Container creation failed: {container_json}")

creation_id = container_json["id"]

# ఫేస్‌బుక్ సర్వర్ ఇమేజ్ డౌన్‌లోడ్ చేసి ప్రాసెస్ చేయడానికి 15 సెకన్లు ఆగడం
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
