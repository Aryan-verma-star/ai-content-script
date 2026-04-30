import requests
import json

VIDEO_ID = "TJIP4K5qvmI"

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

    print(f"Testing video: https://youtu.be/{VIDEO_ID}")
    
    try:
        print("Step 1: Initialize session...")
        r = session.get('https://kome.ai/tools/youtube-transcript-generator')
        print(f"  Init status: {r.status_code}")
        print(f"  Cookies: {dict(session.cookies)}")

        url = f"https://youtu.be/{VIDEO_ID}"
        payload = {'video_id': url, 'format': True, 'source': 'tool'}
        
        print(f"Step 2: POST to API...")
        print(f"  URL: https://kome.ai/api/transcript")
        print(f"  Payload: {payload}")
        
        response = session.post('https://kome.ai/api/transcript', json=payload)
        
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        
        raw_text = response.text
        print(f"  Raw response (first 1000): {raw_text[:1000]}")
        print(f"  Is valid JSON start '[': {raw_text.strip().startswith('[')}")
        print(f"  Is valid JSON start '{{': {raw_text.strip().startswith('{')}")
        
        # Test parsing
        print("Step 3: Parse response...")
        try:
            data = response.json()
            print(f"  response.json() succeeded: {type(data)}")
            if isinstance(data, list):
                print(f"  List length: {len(data)}")
                print(f"  First item: {data[0]}")
            elif isinstance(data, dict):
                print(f"  Dict keys: {data.keys()}")
        except Exception as e:
            print(f"  response.json() failed: {e}")
            print(f"  Trying json.loads on raw text...")
            try:
                data = json.loads(raw_text)
                print(f"  json.loads succeeded: {type(data)}")
            except Exception as e2:
                print(f"  json.loads also failed: {e2}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcript()