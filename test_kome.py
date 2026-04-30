import requests
import json

VIDEO_ID = "dQw4w9WgXcQ"  # Rick Astley - Always has transcripts

def test_transcript():
    session = requests.Session()

    mac_safari_ua = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/18.0 Safari/605.1.15"
    )

    session.headers.update({
        'user-agent': mac_safari_ua,
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'origin': 'https://kome.ai',
        'referer': 'https://kome.ai/tools/youtube-transcript-generator',
    })

    print(f"Testing with video ID: {VIDEO_ID}")
    
    try:
        print("Step 1: Initialize session...")
        resp = session.get('https://kome.ai/tools/youtube-transcript-generator')
        print(f"  Init status: {resp.status_code}")
        print(f"  Cookies: {dict(session.cookies)}")

        url = f"https://youtu.be/{VIDEO_ID}"
        payload = {'video_id': url, 'format': True, 'source': 'tool'}
        
        print("Step 2: POST to API...")
        print(f"  URL: https://kome.ai/api/transcript")
        print(f"  Payload: {payload}")
        
        response = session.post('https://kome.ai/api/transcript', json=payload)
        
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Response (first 500): {response.text[:500]}")
        
        print("Step 3: Parse response...")
        data = response.json()
        print(f"  Type: {type(data)}")
        print(f"  Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")
        
        if isinstance(data, dict):
            transcript = data.get('transcript', '')
            print(f"  Transcript (first 200): {transcript[:200]}")
            print(f"  Has transcript: {bool(transcript and 'not available' not in transcript.lower())}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcript()