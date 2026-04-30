"""Test script for Kome AI transcript API."""

import requests
import json


def get_transcript(video_id: str, max_chars: int = 1500) -> str:
    """Fetch the transcript for a YouTube video using Kome AI API."""
    try:
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
        
        print(f"Step 1: Visiting site to get session...")
        session.get('https://kome.ai/tools/youtube-transcript-generator')
        print(f"Session cookies: {session.cookies.get_dict()}")
        
        url = f"https://youtu.be/{video_id}"
        payload = {
            'video_id': url,
            'format': True,
            'source': 'tool'
        }
        
        print(f"Step 2: Posting to API with video_id: {url}")
        response = session.post('https://kome.ai/api/transcript', json=payload)
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response text (first 500): {response.text[:500]}")
        
        if response.status_code != 200:
            print(f"ERROR: API returned {response.status_code}")
            return "[Transcript unavailable]"
        
        data = response.text
        print(f"Data type: {type(data)}")
        
        if isinstance(data, str):
            print(f"Trying to parse as JSON...")
            try:
                data = json.loads(data)
                print(f"Parsed successfully, type: {type(data)}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                if data.strip().startswith('['):
                    data = json.loads(data)
                else:
                    return data[:max_chars] if len(data) <= max_chars else data[:max_chars] + "..."
        
        if isinstance(data, list):
            print(f"Data is a list with {len(data)} items")
            transcript_list = data
        elif isinstance(data, dict):
            print(f"Data is a dict with keys: {data.keys()}")
            transcript_list = data.get("transcript", data.get("result", []))
        else:
            print(f"Unexpected data type: {type(data)}")
            return "[Transcript unavailable]"
        
        print(f"Transcript list type: {type(transcript_list)}, length: {len(transcript_list) if transcript_list else 0}")
        
        transcript_text = " ".join(str(segment.get("text", segment)) for segment in transcript_list)
        print(f"Transcript text length: {len(transcript_text)}")

        if len(transcript_text) > max_chars:
            transcript_text = transcript_text[:max_chars] + "..."

        return transcript_text

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return "[Transcript unavailable]"


if __name__ == "__main__":
    # Test with a known working video
    video_id = "lK_slUdCJlw"
    print(f"\n=== Testing Kome AI transcript for: {video_id} ===\n")
    result = get_transcript(video_id)
    print(f"\n=== RESULT ===\n{result[:500]}")