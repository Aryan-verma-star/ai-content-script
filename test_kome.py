import requests
import json

VIDEO_ID = "o9eG0QdZEh4"  # One of the videos from your log that failed

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
        print("Initializing session...")
        session.get('https://kome.ai/tools/youtube-transcript-generator')
        print(f"Cookies: {dict(session.cookies)}")
        print(f"Session headers: {dict(session.headers)}")

        url = f"https://youtu.be/{VIDEO_ID}"
        payload = {'video_id': url, 'format': True, 'source': 'tool'}
        
        print(f" Posting to: https://kome.ai/api/transcript")
        print(f" Payload: {payload}")
        
        response = session.post('https://kome.ai/api/transcript', json=payload)
        
        print(f"Status: {response.status_code}")
        print(f"Response text (first 500): {response.text[:500]}")
        print(f"Response type: {type(response.text)}")
        
        try:
            data = response.json()
            print(f"JSON parsed: {type(data)}")
            print(f"Data: {data[:200] if len(str(data)) > 200 else data}")
        except:
            print("Failed to parse as JSON")
            print(f"Raw: {response.text[:200]}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcript()