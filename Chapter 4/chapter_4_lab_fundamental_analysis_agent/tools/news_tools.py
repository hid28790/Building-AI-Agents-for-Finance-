"""
news_tools.py
-------------
Tools for fetching recent news and scoring market sentiment for a given ticker.
Uses yfinance for free news retrieval with no API key required.
"""

import json
import re
from datetime import datetime, timezone
import yfinance as yf
from agents import function_tool
from tools import cache as _cache


# ---------------------------------------------------------------------------
# Sentiment lexicon — simple but effective for financial news
# ---------------------------------------------------------------------------

BULLISH_SIGNALS = [
    "beat", "beats", "surpass", "record", "growth", "profit", "revenue",
    "upgrade", "buy", "outperform", "strong", "rally", "surge", "rises",
    "gains", "positive", "innovative", "launch", "partnership", "expansion",
    "dividend", "buyback", "raised", "exceeds", "momentum", "bullish",
    "breakthrough", "wins", "awarded", "approved", "acquisition",
]

BEARISH_SIGNALS = [
    "miss", "misses", "decline", "loss", "cut", "downgrade", "sell",
    "underperform", "weak", "fall", "drop", "concern", "warning", "risk",
    "lawsuit", "investigation", "fraud", "scandal", "layoffs", "recall",
    "fine", "penalty", "below", "disappoints", "slump", "crash", "bearish",
    "negative", "headwind", "uncertainty", "regulatory", "antitrust",
]


def _score_headline(headline: str) -> tuple[str, float]:
    """
    Score a single headline as bullish/bearish/neutral.
    Returns (label, score) where score is 0-1 for bullish, -1 to 0 for bearish.
    """
    text = headline.lower()
    bull_count = sum(1 for word in BULLISH_SIGNALS if word in text)
    bear_count = sum(1 for word in BEARISH_SIGNALS if word in text)

    total = bull_count + bear_count
    if total == 0:
        return "neutral", 0.0

    net_score = (bull_count - bear_count) / total
    if net_score > 0.15:
        label = "bullish"
    elif net_score < -0.15:
        label = "bearish"
    else:
        label = "neutral"

    return label, round(net_score, 3)


def _format_timestamp(ts) -> str:
    """Convert a Unix timestamp or ISO 8601 string to a readable date string."""
    if not ts:
        return "Unknown date"
    # ISO 8601 string (e.g. "2024-04-06T10:30:00Z")
    if isinstance(ts, str):
        try:
            ts_clean = ts.rstrip("Z").split(".")[0]
            return datetime.strptime(ts_clean, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M UTC")
        except ValueError:
            return ts  # return as-is if unparseable
    # Unix timestamp
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OSError):
        return "Unknown date"


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

# Maps a human-readable field path to an accessor function.
# Update this dict whenever yfinance changes its news response structure.
_EXPECTED_NEWS_FIELDS: dict[str, callable] = {
    "content.title":               lambda i: i.get("content", {}).get("title"),
    "content.summary/description": lambda i: i.get("content", {}).get("summary") or i.get("content", {}).get("description"),
    "content.provider.displayName": lambda i: (i.get("content", {}).get("provider") or {}).get("displayName"),
    "content.pubDate":             lambda i: i.get("content", {}).get("pubDate"),
    "content.clickThroughUrl.url": lambda i: (i.get("content", {}).get("clickThroughUrl") or {}).get("url"),
}


def _is_about_company(title: str, first_sentence: str | None, ticker: str, short_name: str) -> bool:
    """Return True if the article is primarily about the given company.

    Requires the ticker symbol or a meaningful word from the company's short
    name to appear in the title. The title is the primary signal — if the
    company is not named there, the article is considered a secondary mention
    rather than a primary subject. Words shorter than 4 characters are skipped
    to avoid false positives (e.g. "Inc", "The").
    """
    title_text = title.lower()
    if ticker.lower() in title_text:
        return True
    for word in short_name.lower().split():
        if len(word) >= 4 and word.rstrip(".,:") in title_text:
            return True
    return False


def _validate_news_schema(item: dict) -> list[str]:
    """Check that all expected fields are reachable in a raw yfinance news item.

    Returns a list of field paths that are missing or empty. An empty list
    means the schema is intact. Call this on the first raw item before
    processing the full list — if warnings are returned, the yfinance news
    structure may have changed and the accessors in _EXPECTED_NEWS_FIELDS
    need to be updated.
    """
    missing = []
    for path, accessor in _EXPECTED_NEWS_FIELDS.items():
        try:
            value = accessor(item)
            if not value:
                missing.append(path)
        except (AttributeError, TypeError):
            missing.append(f"{path} (access error — possible structure change)")
    return missing


# ---------------------------------------------------------------------------
# Tool 1: Search Recent News
# ---------------------------------------------------------------------------

@function_tool
def search_recent_news(ticker: str, max_results: int) -> str:
    """
    Fetch recent news articles and headlines for a given stock ticker.

    Uses yfinance to retrieve the latest news. Returns titles, publishers,
    publication dates, and article links. This data feeds into sentiment
    analysis and helps identify current market narratives around the stock.

    Args:
        ticker: The stock ticker symbol, e.g. 'AAPL', 'MSFT', 'GOOGL'.
        max_results: Maximum number of news articles to retrieve (1-20).
    """
    try:
        max_results = max(1, min(int(max_results), 20))

        _key = ("search_recent_news", ticker.upper(), max_results)
        _hit = _cache.get(_key)
        if _hit is not None:
            return _hit

        stock       = yf.Ticker(ticker.upper())
        short_name  = stock.info.get("shortName", "")
        raw_news    = stock.news or []

        if not raw_news:
            return json.dumps({
                "ticker":  ticker.upper(),
                "message": "No recent news found.",
                "articles": [],
            })

        # Validate schema on the first item before processing
        schema_warnings = _validate_news_schema(raw_news[0])
        if schema_warnings:
            return json.dumps({
                "error": (
                    "yfinance news schema has changed. The following expected fields "
                    f"are missing or empty: {schema_warnings}. "
                    "Update _EXPECTED_NEWS_FIELDS in news_tools.py to match the new structure."
                ),
                "ticker": ticker.upper(),
                "raw_keys_found": list(raw_news[0].keys()),
                "raw_content_keys_found": list((raw_news[0].get("content") or {}).keys()),
            })

        articles = []
        for item in raw_news:
            if len(articles) >= max_results:
                break

            content   = item.get("content") or {}
            title     = content.get("title") or "No title"
            publisher = (content.get("provider") or {}).get("displayName") or "Unknown"
            pub_time  = _format_timestamp(content.get("pubDate"))
            link      = (content.get("clickThroughUrl") or {}).get("url") or ""

            # First sentence from summary or description
            raw_summary = content.get("summary") or content.get("description") or ""
            if raw_summary:
                match = re.search(r"([^.!?]*[.!?])", raw_summary.strip())
                first_sentence = match.group(1).strip() if match else raw_summary.strip()[:200]
            else:
                first_sentence = None

            # Skip articles not primarily about this company
            if not _is_about_company(title, first_sentence, ticker.upper(), short_name):
                continue

            scoring_text = f"{title} {first_sentence}" if first_sentence else title
            label, score = _score_headline(scoring_text)

            articles.append({
                "title":           title,
                "publisher":       publisher,
                "published_at":    pub_time,
                "sentiment":       label,
                "sentiment_score": score,
                "url":             link,
                "first_sentence":  first_sentence,
                "scoring_text":    scoring_text,
            })

        # Aggregate quick stats
        sentiments = [a["sentiment"] for a in articles]
        bull_count = sentiments.count("bullish")
        bear_count = sentiments.count("bearish")
        neut_count = sentiments.count("neutral")

        result = {
            "ticker":       ticker.upper(),
            "articles_found": len(articles),
            "sentiment_summary": {
                "bullish":  bull_count,
                "bearish":  bear_count,
                "neutral":  neut_count,
                "dominant": max(
                    [("bullish", bull_count), ("bearish", bear_count), ("neutral", neut_count)],
                    key=lambda x: x[1],
                )[0],
            },
            "articles": articles,
        }

        output = json.dumps(result, indent=2, default=str)
        _cache.store(_key, output)
        return output

    except Exception as e:
        return json.dumps({"error": str(e), "ticker": ticker})


# ---------------------------------------------------------------------------
# Tool 2: Analyze Sentiment
# ---------------------------------------------------------------------------

@function_tool
def analyze_sentiment(news_json: str) -> str:
    """
    Perform a structured sentiment analysis on a set of news articles.

    Takes the JSON output from search_recent_news and produces a detailed
    sentiment report: an aggregate sentiment score, key bullish and bearish
    themes extracted from headlines, and an overall market narrative summary.

    Args:
        news_json: JSON string output from search_recent_news containing
                   a list of articles with titles and sentiment scores.
    """
    try:
        data = json.loads(news_json)

        if "error" in data:
            return json.dumps({"error": data["error"]})

        articles = data.get("articles", [])
        if not articles:
            return json.dumps({
                "ticker":    data.get("ticker", "UNKNOWN"),
                "sentiment": "neutral",
                "score":     0.0,
                "summary":   "No articles available for sentiment analysis.",
            })

        ticker = data.get("ticker", "UNKNOWN")

        # Weighted aggregate score
        scores = [a.get("sentiment_score", 0.0) for a in articles]
        avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

        # Extract key themes
        all_titles = " ".join(a.get("scoring_text") or a.get("title", "") for a in articles).lower()
        bullish_themes = [w for w in BULLISH_SIGNALS if w in all_titles][:5]
        bearish_themes = [w for w in BEARISH_SIGNALS if w in all_titles][:5]

        # Top headlines by sentiment
        top_bullish = sorted(
            [a for a in articles if a.get("sentiment") == "bullish"],
            key=lambda x: x.get("sentiment_score", 0), reverse=True,
        )[:3]

        top_bearish = sorted(
            [a for a in articles if a.get("sentiment") == "bearish"],
            key=lambda x: x.get("sentiment_score", 0),
        )[:3]

        # Overall label — 5-level scale aligned with agent verdict categories
        if avg_score > 0.40:
            overall = "strongly bullish"
        elif avg_score > 0.15:
            overall = "bullish"
        elif avg_score < -0.40:
            overall = "strongly bearish"
        elif avg_score < -0.15:
            overall = "bearish"
        else:
            overall = "neutral"

        # Risk flags — headlines that mention high-impact bearish keywords
        high_risk_keywords = ["fraud", "investigation", "antitrust", "lawsuit", "recall", "scandal", "penalty", "fine"]
        risk_flags = [
            a["title"] for a in articles
            if any(kw in a.get("title", "").lower() for kw in high_risk_keywords)
        ]

        result = {
            "ticker":          ticker,
            "overall_sentiment": overall,
            "aggregate_score": avg_score,
            "interpretation": (
                f"Score of {avg_score:.3f} on a scale of -1 (very bearish) to +1 (very bullish)"
            ),
            "article_count": len(articles),
            "sentiment_breakdown": data.get("sentiment_summary", {}),
            "key_bullish_themes": bullish_themes,
            "key_bearish_themes": bearish_themes,
            "top_bullish_headlines": [h["title"] for h in top_bullish],
            "top_bearish_headlines": [h["title"] for h in top_bearish],
            "risk_flags": risk_flags,
            "risk_flag_count": len(risk_flags),
            "all_articles": [
                {
                    "title":          a["title"],
                    "publisher":      a["publisher"],
                    "published_at":   a["published_at"],
                    "sentiment":      a["sentiment"],
                    "score":          a["sentiment_score"],
                    "url":            a["url"],
                    "first_sentence": a.get("first_sentence"),
                }
                for a in articles
            ],
        }

        return json.dumps(result, indent=2, default=str)

    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Failed to parse news JSON: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
