
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from darling_prompts import behavior_prompts, Reply_prompts, greet_user
import requests
import os
from dotenv import load_dotenv
import datetime

# Load environment variables (.env file)
load_dotenv()

# Consistent API key names
GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("SEARCH_ENGINE_ID") or os.getenv("GOOGLE_CSE_ID")
OPENWEATHER_API = os.getenv("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API")

app = FastAPI(title="Darling AI Backend", version="1.0.0")


# ---- MODELS ----
class MessageRequest(BaseModel):
    query: str
    language: str = "en"


# ---- UTILITIES ----
def get_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning!"
    elif hour < 17:
        return "Good afternoon!"
    else:
        return "Good evening!"


# ---- ROUTES ----
@app.get("/")
def root():
    return {"message": "❤️ Darling is alive and ready!", "status": "healthy"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}


@app.post("/talk")
def talk(request: MessageRequest):
    try:
        user_query = request.query.lower().strip()
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Weather queries
        if any(word in user_query for word in ["weather", "climate", "temperature"]):
            city = "Bangalore"  # Default city
            # Extract city name if mentioned
            words = user_query.split()
            for i, word in enumerate(words):
                if word in ["in", "for", "at"] and i + 1 < len(words):
                    city = words[i + 1].title()
                    break
            return {"reply": get_weather(city)}
        
        # Search queries
        elif any(word in user_query for word in ["search", "google", "find"]):
            keyword = user_query
            for word in ["search", "google", "find"]:
                keyword = keyword.replace(word, "").strip()
            if not keyword:
                return {"reply": "Please specify what you want to search for."}
            return {"reply": google_search(keyword)}
        
        # Greetings
        elif any(word in user_query for word in ["hello", "hi", "hey", "namaste"]):
            return {"reply": f"{get_greeting()} Darling reporting in! How can I help you?"}
        
        # Default response
        else:
            return {
                "reply": f"I received: '{request.query}' — I'm still learning how to handle that. Try asking about weather, search, or just say hello! 😊"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/weather")
def get_weather(city: str = "Bangalore"):
    if not OPENWEATHER_API:
        raise HTTPException(status_code=503, detail="❌ OpenWeather API key not configured!")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_API, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") != 200:
            return f"❌ Couldn't fetch weather for {city}. {data.get('message', '')}"

        desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humid = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        return (f"🌤️ Weather in {city}:\n"
                f"- Condition: {desc}\n"
                f"- Temperature: {temp}°C (feels like {feels_like}°C)\n"
                f"- Humidity: {humid}%\n"
                f"- Wind Speed: {wind} m/s")
    
    except requests.exceptions.Timeout:
        return "❌ Weather service timeout. Please try again."
    except requests.exceptions.RequestException as e:
        return f"❌ Weather service error: {str(e)}"
    except KeyError as e:
        return f"❌ Unexpected weather data format: {str(e)}"
    except Exception as e:
        return f"❌ Error fetching weather: {str(e)}"


@app.get("/search")
def google_search(query: str = Query(..., description="Search query")):
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        raise HTTPException(status_code=503, detail="❌ Google Search API or CSE ID not configured!")

    if not query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY, 
        "cx": GOOGLE_CSE_ID, 
        "q": query.strip(), 
        "num": 3,
        "safe": "active"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return f"❌ Search error: {data['error'].get('message', 'Unknown error')}"
        
        items = data.get("items", [])
        if not items:
            return f"🔍 No results found for '{query}'"

        result = f"🔍 Search results for '{query}':\n\n"
        for i, item in enumerate(items, 1):
            title = item.get('title', 'No title')
            link = item.get('link', 'No link')
            snippet = item.get('snippet', '')[:100] + '...' if len(item.get('snippet', '')) > 100 else item.get('snippet', '')
            result += f"{i}. {title}\n{link}\n{snippet}\n\n"
        
        return result.strip()

    except requests.exceptions.Timeout:
        return "❌ Search service timeout. Please try again."
    except requests.exceptions.RequestException as e:
        return f"❌ Search service error: {str(e)}"
    except KeyError as e:
        return f"❌ Unexpected search data format: {str(e)}"
    except Exception as e:
        return f"❌ Search failed: {str(e)}"


@app.get("/greet")
def get_greet():
    """Get a personalized greeting from Darling"""
    return {"reply": greet_user()}
