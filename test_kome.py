import requests
import json

def get_transcript_mac():
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

    try:
        print("Initializing new MacBook session...")
        session.get('https://kome.ai/tools/youtube-transcript-generator')
        
        print("Cookies after init:", dict(session.cookies))

        api_url = 'https://kome.ai/api/transcript'
        payload = {
            'video_id': 'https://youtu.be/awzJu4nlHVU',
            'format': True,
            'source': 'tool'
        }

        print("Requesting transcript via MacBook identity...")
        print(f"URL: {api_url}")
        print(f"Payload: {payload}")
        print(f"Headers: {dict(session.headers)}")
        
        response = session.post(api_url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text[:1000] if len(response.text) > 1000 else response.text}")
        
        response.raise_for_status()
        
        print("Success!")
        print("Raw response:", response.json())

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response: {response.text}")
    except Exception as err:
        print(f"An error occurred: {err}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_transcript_mac()