
import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def google_search(query: str) -> str:
    # Use consistent API key names
    key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("SEARCH_ENGINE_ID") or os.getenv("GOOGLE_CSE_ID")
    
    if not key or not cx:
        return "❌ Google Search API key ಅಥವಾ CSE ID ಸಿಗಲಿಲ್ಲ!"
    
    if not query.strip():
        return "❌ Search query ಖಾಲಿ ಇದೆ!"
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": key,
        "cx": cx,
        "q": query.strip(),
        "num": 3,
        "safe": "active"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            error_msg = data["error"].get("message", "Unknown error")
            return f"❌ Search error: {error_msg}"
        
        items = data.get("items", [])
        if not items:
            return f"🔍 '{query}'ಗೆ ಯಾವುದೇ ಫಲಿತಾಂಶ ಸಿಕ್ಕಿಲ್ಲ 🤷‍♂️"
        
        result = f"🔍 '{query}'ಗೆ ಫಲಿತಾಂಶಗಳು:\n\n"
        for i, item in enumerate(items, 1):
            title = item.get('title', 'No title')
            link = item.get('link', 'No link')
            snippet = item.get('snippet', '')
            if len(snippet) > 100:
                snippet = snippet[:100] + '...'
            result += f"{i}. {title}\n{link}\n{snippet}\n\n"
        
        return result.strip()
    
    except requests.exceptions.Timeout:
        return "❌ Search service timeout ಆಗಿದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
    except requests.exceptions.RequestException as e:
        return f"❌ Search service error: {str(e)}"
    except KeyError as e:
        return f"❌ Search data format error: {str(e)}"
    except Exception as e:
        return f"❌ ಸರ್ಚ್ ನಲ್ಲಿ ದೋಷ: {str(e)}"
