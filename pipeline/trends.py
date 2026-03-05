"""
Finds trending History & Facts topics using Google Trends + Reddit.
Falls back to curated topic bank if APIs fail.
"""
import random
import logging
import requests
from datetime import datetime
from config import FALLBACK_TOPICS, ANTHROPIC_API_KEY

log = logging.getLogger(__name__)


def get_reddit_topics() -> list[str]:
    """Scrape top posts from history subreddits."""
    subs = ["history", "AskHistorians", "HistoryMemes", "Damnthatsinteresting"]
    topics = []
    headers = {"User-Agent": "AutoTuber/1.0"}
    for sub in subs[:2]:
        try:
            r = requests.get(
                f"https://www.reddit.com/r/{sub}/hot.json?limit=10",
                headers=headers, timeout=10
            )
            if r.ok:
                posts = r.json()["data"]["children"]
                for p in posts:
                    title = p["data"]["title"]
                    score = p["data"]["score"]
                    if score > 500 and len(title) > 20:
                        topics.append(title)
        except Exception as e:
            log.warning(f"Reddit {sub} failed: {e}")
    return topics


def get_pytrends_topics() -> list[str]:
    """Get trending searches related to history."""
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
        kw_list = ["ancient history", "historical facts", "world history"]
        pt.build_payload(kw_list, timeframe="now 7-d")
        related = pt.related_queries()
        topics = []
        for kw in kw_list:
            df = related.get(kw, {}).get("top")
            if df is not None and not df.empty:
                topics.extend(df["query"].head(5).tolist())
        return topics
    except Exception as e:
        log.warning(f"PyTrends failed: {e}")
        return []


def pick_best_topic(candidates: list[str], used_topics: list[str]) -> str:
    """Use Claude to pick the most YouTube-friendly topic."""
    if not candidates:
        return _fallback(used_topics)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

        candidates_str = "\n".join(f"- {t}" for t in candidates[:20])
        used_str = "\n".join(used_topics[-20:]) if used_topics else "None yet"

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"""You pick YouTube video topics about History & Facts.

Candidate topics from trending sources:
{candidates_str}

Already used (avoid repetition):
{used_str}

Pick the SINGLE best topic that:
1. Has high YouTube search volume potential
2. Is fascinating and clickbait-worthy  
3. Hasn't been covered yet
4. Can fill a 5-7 minute video

Reply with ONLY the topic title. No explanation. No quotes."""
            }]
        )
        return msg.content[0].text.strip()
    except Exception as e:
        log.warning(f"Claude topic selection failed: {e}")
        return _fallback(used_topics)


def _fallback(used_topics: list[str]) -> str:
    available = [t for t in FALLBACK_TOPICS if t not in used_topics]
    if not available:
        available = FALLBACK_TOPICS
    return random.choice(available)


def get_topic(used_topics: list[str] = []) -> str:
    """Main entry — returns the best topic for today's video."""
    log.info("Finding trending topic...")
    candidates = []
    candidates.extend(get_reddit_topics())
    candidates.extend(get_pytrends_topics())

    if candidates:
        log.info(f"Found {len(candidates)} candidate topics")
        topic = pick_best_topic(candidates, used_topics)
    else:
        log.info("No trending data, using fallback bank")
        topic = _fallback(used_topics)

    log.info(f"Selected topic: {topic}")
    return topic
