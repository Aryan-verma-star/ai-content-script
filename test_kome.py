import requests
import json

VIDEO_ID = "TJIP4K5qvmI"  # User provided video

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
    print(f"Video URL: https://youtu.be/{VIDEO_ID}")
    
    try:
        print("\n[1] Initializing session...")
        session.get('https://kome.ai/tools/youtube-transcript-generator')
        print(f"    Cookies: {dict(session.cookies)}")

        url = f"https://youtu.be/{VIDEO_ID}"
        payload = {'video_id': url, 'format': True, 'source': 'tool'}
        
        print(f"\n[2] Posting to API...")
        response = session.post('https://kome.ai/api/transcript', json=payload)
        
        print(f"    Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"    Error response: {response.text[:500]}")
            return
            
        print(f"    Response type: {type(response.text)}")
        print(f"    Response length: {len(response.text)}")
        
        # Try to parse as JSON
        try:
            data = response.json()
            print(f"\n[3] Parsed as JSON")
            print(f"    Type: {type(data)}")
            
            if isinstance(data, list):
                print(f"    List length: {len(data)}")
                print(f"    First item: {data[0] if data else 'empty'}")
            elif isinstance(data, dict):
                print(f"    Keys: {list(data.keys())}")
                if 'transcript' in data:
                    print(f"    Transcript length: {len(data['transcript'])}")
                print(f"    Sample: {str(data)[:300]}")
            else:
                print(f"    Data: {str(data)[:300]}")
                
        except json.JSONDecodeError as e:
            print(f"\n[3] Failed to parse JSON: {e}")
            print(f"    Raw response: {response.text[:500]}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_transcript()