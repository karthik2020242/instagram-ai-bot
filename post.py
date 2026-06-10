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
    "https://www.gulte.com/feed",
    "https://www.greatandhra.com/feed",
    "https://www.telugu360.com/feed",
]

POSTED_FILE = "posted_news.txt"
FALLBACK_IMAGE = (
    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"
    "?auto=format&fit=crop&w=1200&q=80"
)


def load_posted():
    """ఇప్పటికే పోస్ట్ చేసిన లింకులను లోడ్ చేస్తుంది."""
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_posted(link):
    """పోస్ట్ చేసిన లింకును ఫైల్‌లో సేవ్ చేస్తుంది."""
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")


def score_news(title):
    """కీవర్డ్స్ ఆధారంగా వార్తకు స్కోర్ ఇస్తుంది."""
    title = title.lower()
    score = 0

    keywords = {
        "prabhas": 25,
        "allu arjun": 25,
        "ntr": 25,
        "mahesh": 25,
        "pawan": 25,
        "rajamouli": 25,
        "teaser": 20,
        "trailer": 20,
        "first look": 20,
        "box office": 20,
        "record": 20,
        "release date": 15,
        "pan india": 15,
        "blockbuster": 15,
    }

    for word, points in keywords.items():
        if word in title:
            score += points

    return score


def get_article_image(url):
    """ఆర్టికల్ నుండి og:image లేదా twitter:image లను సేకరిస్తుంది."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=20)
        html = r.text

        patterns = [
            r'<meta property="og:image" content="([^"]+)"',
            r'<meta name="twitter:image" content="([^"]+)"',
            r"<meta property=\"og:image\" content='([^']+)'",
            r"<meta name=\"twitter:image\" content='([^']+)'",
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)

    except Exception as e:
        print("Image fetch error:", e)

    return FALLBACK_IMAGE


def get_best_news():
    """ఫీడ్స్ నుండి అత్యధిక స్కోర్ ఉన్న సరికొత్త వార్తను ఎంపిక చేస్తుంది."""
    posted = load_posted()
    articles = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for item in feed.entries:
                link = getattr(item, "link", "")

                if not link or link in posted:
                    continue

                title = getattr(item, "title", "")
                summary = getattr(item, "summary", "")

                articles.append(
                    {
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "score": score_news(title),
                    }
                )
        except Exception as e:
            print("Feed Error:", e)

    if not articles:
        return None

    # స్కోర్ ఆధారంగా డిసెండింగ్ ఆర్డర్‌లో సార్ట్ చేస్తుంది
    articles.sort(key=lambda x: x["score"], reverse=True)
    return articles[0]


# --- ప్రధాన ప్రక్రియ (Main Execution) ---

news = get_best_news()

if not news:
    print("No new news available.")
    raise SystemExit(0)

image_url = get_article_image(news["link"])

print("Selected News:", news["title"])
print("Image:", image_url)

# ఇన్‌స్టాగ్రామ్ క్యాప్షన్ ఫార్మాటింగ్
clean_summary = re.sub("<.*?>", "", news["summary"])[:350]
caption = f"""
🔥 TRENDING TOLLYWOOD UPDATE

🎬 {news['title']}

{clean_summary}

👇 What do you think?

Follow for daily Tollywood updates.

#Tollywood #TeluguCinema #MovieNews #TeluguMovies #Prabhas
#NTR #AlluArjun #MaheshBabu #PawanKalyan #MovieUpdate
#CinemaNews #TollywoodUpdates #FilmNews #Entertainment #Trending
"""

# 1. ఇన్‌స్టాగ్రామ్ మీడియా కంటైనర్ క్రియేషన్
container_url = f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media"
container_response = requests.post(
    container_url,
    data={
        "image_url": image_url,
        "caption": caption,
        "access_token": META_ACCESS_TOKEN,
    },
)

container = container_response.json()
print("Container Response:", container)

if "id" not in container:
    raise Exception(f"Container creation failed: {container}")

creation_id = container["id"]

# ఫేస్‌బుక్ సర్వర్లలో ఇమేజ్ ప్రాసెస్ అవ్వడానికి కాస్త సమయం ఇస్తున్నాము
print("Waiting 15 seconds...")
time.sleep(15)

# 2. కంటైనర్‌ను ఇన్‌స్టాగ్రామ్‌లో పబ్లిష్ చేయడం
publish_url = (
    f"https://graph.facebook.com/v25.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
)
publish_response = requests.post(
    publish_url,
    data={"creation_id": creation_id, "access_token": META_ACCESS_TOKEN},
)

publish = publish_response.json()
print("Publish Response:", publish)

if "id" in publish:
    save_posted(news["link"])
    print("SUCCESS")
else:
    raise Exception(f"Publish failed: {publish}")
