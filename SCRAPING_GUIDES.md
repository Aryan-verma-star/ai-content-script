# Google Search Prompt for TikTok & Instagram Scraping Techniques

Use this prompt with your custom LLM (qwen.aikit.club or similar) to find real scraping methods:

---

## TikTok Scraping Search Prompt:

```
Search the web for: "how to scrape TikTok trending videos API 2025 without authentication" 

Find and provide:
1. Official TikTok Creative API documentation link
2. Any public GitHub repositories for TikTok scraping
3. Alternative methods to get trending TikTok data ( hashtags, sounds, creators )
4. Working endpoints that don't require app approval

Focus on: python requests implementation, not TikTok's official API that requires app approval
```

---

## Instagram Scraping Search Prompt:

```
Search the web for: "how to scrape Instagram reels and posts API 2025 without authentication" 

Find and provide:
1. Instagram Graph API for business vs Creator API differences
2. Public scraping methods using requests library
3. Instagram web scraping endpoints (not mobile API)
4. Any working alternatives to official Meta API

Focus on: python requests implementation for web scraping, not official Meta API
```

---

## Quick Tests (try manually):

### TikTok Test:
```bash
# Try this in browser console on tiktok.com:
fetch('https://www.tiktok.com/api/trending/fy/').then(r=>r.json()).then(console.log)

# Or for generic search:
https://www.tiktok.com/api/search/general/full/?keyword=personal+finance
```

### Instagram Test:
```bash
# Browser console on instagram.com:
fetch('https://www.instagram.com/api/v1/feed/reels_trending/').then(r=>r.json()).then(console.log)
```

---

## Note:
TikTok and Instagram frequently block server-side requests. For production:
1. Use rotating proxies
2. Rotate User-Agents (mobile vs desktop)
3. Add proper cookies/session data
4. Consider official APIs if available

The free/public endpoints often get rate-limited or blocked quickly.