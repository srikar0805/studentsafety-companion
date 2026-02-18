"""
Local Safety News Service.

Fetches RSS feeds from Columbia, MO news sources, classifies articles,
performs sentiment analysis, and geocodes to campus locations.
"""

import hashlib
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ─── RSS Feed Sources ─────────────────────────────────────────
NEWS_FEEDS = [
    {"url": "https://www.columbiamissourian.com/search/?f=rss&t=article&c=news/local&l=25&s=start_time&sd=desc", "name": "Columbia Missourian"},
    {"url": "https://www.komu.com/rss/", "name": "KOMU 8"},
    {"url": "https://www.abc17news.com/feed/", "name": "ABC 17 (KMIZ)"},
]

# ─── Keyword Dictionaries ─────────────────────────────────────
CRIME_KEYWORDS = [
    "crime", "assault", "robbery", "theft", "burglary", "murder", "homicide",
    "shooting", "stabbing", "arrest", "charged", "suspect", "victim", "police",
    "mupd", "investigation", "felony", "misdemeanor", "drug", "domestic",
]

SAFETY_KEYWORDS = [
    "safety", "safe", "emergency", "alert", "warning", "danger", "hazard",
    "patrol", "security", "lighting", "camera", "escort", "prevention",
]

POLICY_KEYWORDS = [
    "policy", "ordinance", "law", "regulation", "ban", "legislation",
    "city council", "vote", "approved", "budget",
]

PROTEST_KEYWORDS = [
    "protest", "rally", "march", "demonstration", "activist", "petition",
]

# Sentiment word lists
NEGATIVE_WORDS = [
    "crime", "assault", "robbery", "theft", "murder", "shooting", "stabbing",
    "arrest", "victim", "danger", "threat", "fatal", "killed", "injured",
    "attacked", "stolen", "suspect", "flee", "weapon", "violence", "death",
    "crashed", "collision", "accident", "fire", "drug", "overdose",
]

POSITIVE_WORDS = [
    "safe", "safety", "protect", "secure", "help", "rescue", "saved",
    "community", "volunteer", "improved", "new", "award", "success",
    "reduced", "prevention", "program", "grant", "initiative", "support",
]

# Campus location keywords → coordinates
CAMPUS_LOCATIONS = {
    "jesse hall": (38.9438, -92.3268),
    "memorial union": (38.9465, -92.3275),
    "student center": (38.9480, -92.3280),
    "rec center": (38.9380, -92.3300),
    "library": (38.9448, -92.3266),
    "engineering": (38.9470, -92.3310),
    "mizzou": (38.9404, -92.3277),
    "mu campus": (38.9404, -92.3277),
    "university of missouri": (38.9404, -92.3277),
    "tiger avenue": (38.9382, -92.3300),
    "hitt street": (38.9430, -92.3260),
    "rollins": (38.9424, -92.3250),
    "virginia ave": (38.9392, -92.3238),
    "hospital": (38.9384, -92.3283),
    "greek town": (38.9395, -92.3310),
    "downtown columbia": (38.9517, -92.3341),
    "broadway": (38.9510, -92.3220),
    "providence": (38.9465, -92.3390),
    "stadium": (38.9355, -92.3390),
}


def classify_article(text: str) -> str:
    """Classify article into categories based on keyword matching."""
    text_lower = text.lower()

    scores = {
        "crime": sum(1 for w in CRIME_KEYWORDS if w in text_lower),
        "safety": sum(1 for w in SAFETY_KEYWORDS if w in text_lower),
        "policy": sum(1 for w in POLICY_KEYWORDS if w in text_lower),
        "protest": sum(1 for w in PROTEST_KEYWORDS if w in text_lower),
    }

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "general"
    return best


def simple_sentiment(text: str) -> float:
    """
    Simple sentiment analysis using keyword counting.
    Returns -1.0 (negative) to 1.0 (positive).
    """
    text_lower = text.lower()
    words = re.findall(r'\w+', text_lower)

    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)

    total = neg_count + pos_count
    if total == 0:
        return 0.0

    score = (pos_count - neg_count) / total
    return round(max(-1.0, min(1.0, score)), 2)


def geocode_article(text: str) -> Optional[Dict]:
    """Extract location from article text using keyword matching."""
    text_lower = text.lower()
    for keyword, (lat, lon) in CAMPUS_LOCATIONS.items():
        if keyword in text_lower:
            return {"lat": lat, "lon": lon}
    return None


def _fetch_rss_articles() -> List[Dict]:
    """Fetch articles from RSS feeds. Falls back to sample data on failure."""
    articles = []

    try:
        import feedparser
    except ImportError:
        logger.warning("feedparser not installed. Using fallback articles.")
        return _create_fallback_articles()

    for feed_info in NEWS_FEEDS:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:10]:
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                # Strip HTML tags from summary
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                if len(summary) > 200:
                    summary = summary[:200] + "..."

                pub_date = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
                    except Exception:
                        pub_date = entry.get("published", "")
                elif hasattr(entry, "published"):
                    pub_date = entry.published

                article_id = hashlib.md5(
                    f"{title}{pub_date}".encode()
                ).hexdigest()[:12]

                combined_text = f"{title} {summary}"
                category = classify_article(combined_text)
                sentiment = simple_sentiment(combined_text)
                location = geocode_article(combined_text)

                articles.append({
                    "id": article_id,
                    "title": title,
                    "source": feed_info["name"],
                    "url": entry.get("link", ""),
                    "published_date": pub_date,
                    "summary": summary,
                    "sentiment_score": sentiment,
                    "lat": location["lat"] if location else None,
                    "lon": location["lon"] if location else None,
                    "categories": category,
                })
        except Exception as e:
            logger.warning(f"Failed to fetch {feed_info['name']}: {e}")

    if not articles:
        articles = _create_fallback_articles()

    return articles


def _create_fallback_articles() -> List[Dict]:
    """Sample articles for when RSS feeds are unavailable."""
    return [
        {
            "id": "fb001",
            "title": "MUPD Increases Night Patrols Near Campus",
            "source": "Columbia Missourian",
            "url": "",
            "published_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "MU Police Department has increased patrol frequency near Greek Town and Hitt Street in response to recent safety concerns.",
            "sentiment_score": 0.3,
            "lat": 38.9395,
            "lon": -92.3310,
            "categories": "safety",
        },
        {
            "id": "fb002",
            "title": "Vehicle Break-ins Reported Near Stadium Boulevard",
            "source": "KOMU 8",
            "url": "",
            "published_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "Multiple vehicle break-ins reported in parking lots along Stadium Boulevard. MUPD reminds students to lock vehicles and hide valuables.",
            "sentiment_score": -0.6,
            "lat": 38.9355,
            "lon": -92.3390,
            "categories": "crime",
        },
        {
            "id": "fb003",
            "title": "New Emergency Blue Light Phones Installed on Campus",
            "source": "Columbia Missourian",
            "url": "",
            "published_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "The university has installed 12 new emergency blue light phones along popular walking paths between the library and recreation center.",
            "sentiment_score": 0.7,
            "lat": 38.9448,
            "lon": -92.3266,
            "categories": "safety",
        },
        {
            "id": "fb004",
            "title": "City Council Approves Improved Street Lighting Downtown",
            "source": "ABC 17 (KMIZ)",
            "url": "",
            "published_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "Columbia City Council voted to upgrade street lighting in the downtown and Broadway corridor, improving safety for pedestrians.",
            "sentiment_score": 0.5,
            "lat": 38.9510,
            "lon": -92.3220,
            "categories": "policy",
        },
        {
            "id": "fb005",
            "title": "Assault Reported Near Tiger Avenue Late Saturday",
            "source": "KOMU 8",
            "url": "",
            "published_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "An assault was reported near Tiger Avenue around 1 AM Saturday. Police are investigating and urge students to walk in groups at night.",
            "sentiment_score": -0.8,
            "lat": 38.9382,
            "lon": -92.3300,
            "categories": "crime",
        },
    ]


# ─── Public API ───────────────────────────────────────────────

def get_news_articles() -> List[Dict]:
    """Get classified, sentiment-scored news articles."""
    return _fetch_rss_articles()


def get_news_sentiment() -> Dict:
    """Get aggregated sentiment statistics."""
    articles = _fetch_rss_articles()
    if not articles:
        return {"average": 0.0, "total_articles": 0}

    scores = [a["sentiment_score"] for a in articles]
    return {
        "average": round(sum(scores) / len(scores), 2),
        "total_articles": len(articles),
    }
