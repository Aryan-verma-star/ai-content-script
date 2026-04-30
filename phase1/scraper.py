"""Scraper module for AI Content Engine Phase 1.

Fetches trending YouTube video data and transcripts for a given niche,
and provides mock data for TikTok and Instagram platforms.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from googleapiclient.discovery import build

from phase1.config import config

logger = logging.getLogger(__name__)


def get_youtube_trending(niche: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Fetch the top trending YouTube videos for a given niche.

    Uses the YouTube Data API v3 to search for videos matching the niche,
    ordered by view count from the last 7 days.

    Args:
        niche: The search query for trending content.
        max_results: Maximum number of videos to return (default 5).

    Returns:
        A list of dictionaries containing video data with keys:
        platform, video_id, title, channel, published_at, description,
        view_count, like_count, comment_count, transcript.
    """
    youtube = build(
        "youtube",
        "v3",
        developerKey=config.youtube_api_key,
        cache_discovery=False,
    )

    published_after = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"

    try:
        search_response = (
            youtube.search()
            .list(
                q=niche,
                part="snippet",
                type="video",
                order="viewCount",
                publishedAfter=published_after,
                maxResults=max_results,
            )
            .execute()
        )
    except Exception as e:
        logger.error(f"YouTube search API call failed: {e}")
        return []

    if "items" not in search_response or not search_response["items"]:
        logger.info(f"No videos found for niche: {niche}")
        return []

    video_ids = [item["id"]["videoId"] for item in search_response["items"]]

    try:
        videos_response = (
            youtube.videos()
            .list(part="statistics", id=",".join(video_ids))
            .execute()
        )
    except Exception as e:
        logger.error(f"YouTube videos API call failed: {e}")
        return []

    stats_map = {}
    if "items" in videos_response:
        for item in videos_response["items"]:
            vid = item["id"]
            stats_map[vid] = item.get("statistics", {})

    results = []
    for item in search_response["items"]:
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        stats = stats_map.get(video_id, {})

        description = snippet.get("description", "")
        if len(description) > 300:
            description = description[:300]

        results.append(
            {
                "platform": "youtube",
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "description": description,
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "transcript": "",
            }
        )

    logger.info(f"Fetched {len(results)} YouTube videos for niche: {niche}")
    return results


def get_transcript(video_id: str, max_chars: int) -> str:
    """Fetch the transcript for a YouTube video using Kome AI API.

    Args:
        video_id: The YouTube video ID.
        max_chars: Maximum characters to return (truncates with "..." if exceeded).

    Returns:
        The transcript text, or "[Transcript unavailable]" if fetching fails.
    """
    try:
        url = f"https://youtu.be/{video_id}"
        response = httpx.post(
            "https://kome.ai/api/transcript",
            json={
                "video_id": url,
                "format": True,
                "source": "tool",
            },
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            transcript_list = data
        elif isinstance(data, dict):
            transcript_list = data.get("transcript", data.get("result", []))
        else:
            transcript_list = []
        
        transcript_text = " ".join(segment.get("text", str(segment)) for segment in transcript_list)

        if len(transcript_text) > max_chars:
            transcript_text = transcript_text[:max_chars] + "..."

        return transcript_text

    except Exception as e:
        logger.warning(f"Failed to get transcript for {video_id}: {e}")
        return "[Transcript unavailable]"


def get_tiktok_mock(niche: str) -> list[dict[str, Any]]:
    """Return mock TikTok data for the given niche.

    MOCK: intentional placeholder — replace with real TikTok API or scraper in v2.0

    Args:
        niche: The target niche for generating mock data.

    Returns:
        A list of 3 dictionaries representing mock TikTok posts.
    """
    return [
        {
            "platform": "tiktok",
            "video_id": "tk_test_001",
            "title": f"Top 5 {niche} tips that changed my life",
            "channel": "@trendingcreator",
            "view_count": 125000,
            "like_count": 15000,
            "transcript": f"Here's {niche} tip #1 that nobody talks about... "
            f"This is literally gamechanging for anyone into {niche}. "
            f"Let me show you exactly how this works.",
        },
        {
            "platform": "tiktok",
            "video_id": "tk_test_002",
            "title": f"Why {niche} is blowing up right now",
            "channel": "@nicheexpert",
            "view_count": 89000,
            "like_count": 9500,
            "transcript": f"Everyone asking about {niche} — watch this! "
            f"The trend is just getting started. Here's what's coming...",
        },
        {
            "platform": "tiktok",
            "video_id": "tk_test_003",
            "title": f"My {niche} routine that actually works",
            "channel": "@dailyhacks",
            "view_count": 67000,
            "like_count": 7200,
            "transcript": f"Morning {niche} routine activated! "
            f"If you want results with {niche}, consistency is key. "
            f"Let me share my exact daily workflow.",
        },
    ]


def get_instagram_mock(niche: str) -> list[dict[str, Any]]:
    """Return mock Instagram Reels data for the given niche.

    MOCK: intentional placeholder — replace with Meta Graph API in v2.0

    Args:
        niche: The target niche for generating mock data.

    Returns:
        A list of 3 dictionaries representing mock Instagram posts.
    """
    return [
        {
            "platform": "instagram",
            "post_id": "ig_test_001",
            "caption": f"Top {niche} secrets revealed! Who else wants to master this? Drop a 🙋 below! #"
            f"{niche.replace(' ', '')} #trending",
            "account": "@influencer_one",
            "view_count": 45000,
            "like_count": 5200,
            "transcript": f"Stop scrolling if you want to learn about {niche}! "
            f"I've tested everything and here are the results...",
        },
        {
            "platform": "instagram",
            "post_id": "ig_test_002",
            "caption": f"This {niche} trend is only getting bigger. Save for later! 🔥 #"
            f"{niche.replace(' ', '')} #viral",
            "account": "@niche_creator",
            "view_count": 38000,
            "like_count": 4100,
            "transcript": f"What if I told you {niche} could be this simple? "
            f"Watch till the end for the big reveal!",
        },
        {
            "platform": "instagram",
            "post_id": "ig_test_003",
            "caption": f"POV: You're learning {niche} and it clicks 💡 #"
            f"{niche.replace(' ', '')} #learn",
            "account": "@edutok",
            "view_count": 29000,
            "like_count": 3100,
            "transcript": f"That moment when {niche} finally makes sense! "
            f"Save this video for when you need a refresher.",
        },
    ]


def run_scraper() -> dict[str, Any]:
    """Execute the full scraping pipeline.

    Fetches YouTube trending videos with transcripts, TikTok mock data,
    and Instagram mock data for the configured niche.

    Returns:
        A dictionary containing:
        - niche: The target niche string
        - scraped_at: ISO timestamp of when scraping occurred
        - youtube: List of YouTube video data
        - tiktok: List of TikTok mock data
        - instagram: List of Instagram mock data
    """
    niche = config.target_niche
    max_transcript_chars = config.max_transcript_chars

    logger.info(f"Starting scraper for niche: {niche}")

    youtube_results = get_youtube_trending(niche)

    for video in youtube_results:
        video["transcript"] = get_transcript(
            video["video_id"], max_transcript_chars
        )

    tiktok_results = get_tiktok_mock(niche)
    instagram_results = get_instagram_mock(niche)

    result = {
        "niche": niche,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "youtube": youtube_results,
        "tiktok": tiktok_results,
        "instagram": instagram_results,
    }

    print(
        f"[Phase 1] Scraping complete: {len(youtube_results)} YouTube, "
        f"{len(tiktok_results)} TikTok, {len(instagram_results)} Instagram"
    )

    return result