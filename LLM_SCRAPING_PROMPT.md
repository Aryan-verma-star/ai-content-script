# Prompt for Finding TikTok & Instagram Scraping Methods

Use this prompt with your LLM (e.g., qwen.aikit.club) to find working techniques:

---

## Prompt to send to LLM:

```
Research and provide working code/methods to scrape data from TikTok and Instagram using Python requests library (NOT their official APIs which require app approval).

## TikTok - Find:
1. Any working public endpoints like: https://www.tiktok.com/api/...
2. GitHub repos with working TikTok scrapers
3. Hashtag/sound trending endpoints
4. Code example using requests

## Instagram - Find:  
1. Any working public web endpoints like: https://www.instagram.com/web/...
2. Alternative non-Meta-API methods
3. Hashtag/reels trending endpoints
4. Code example using requests

Return only working, tested methods - not theoretical guides. If you know of any endpoints or libraries that work in 2025, provide them with code examples.
```

---

## Alternative: Search Keywords for Manual Research:

- `tiktok api python github trending 2025`
- `instagram web scraping python without api`
- `tiktok unofficial api python`
- `instagram public endpoints scraping`

---

## Current Working Approach (if APIs keep failing):

The fallback mock data with realistic numbers is already working. For production real data, you'd need:
1. **Official APIs** (TikTok Creative API, Instagram Graph API)
2. **Third-party services** (Social Blade, PhantomBuster)
3. **Browser automation** (Playwright/Selenium - but slower)

The current pipeline with mock fallback is functional for v1.0. For v2.0, consider adding official API keys.