
import os
import requests
from dotenv import load_dotenv

load_dotenv()

async def get_weather(city: str = "Bangalore") -> str:
    # Use consistent API key name
    api_key = os.getenv("OPENWEATHER_API_KEY") or os.getenv("OPENWEATHER_API")
    
    if not api_key:
        return "❌ OpenWeather API key ಸಿಗಲಿಲ್ಲ!"
    
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("cod") != 200:
            return f"❌ {city}ಗೆ ಹವಾಮಾನ ಮಾಹಿತಿ ಸಿಗಲಿಲ್ಲ: {data.get('message', '')}"
        
        if "main" not in data or "weather" not in data:
            return "❌ ಹವಾಮಾನ ಮಾಹಿತಿ incomplete ಆಗಿದೆ 😢"
        
        temp = data["main"]["temp"]
        feels_like = data["main"].get("feels_like", temp)
        desc = data["weather"][0]["description"]
        humidity = data["main"].get("humidity", "N/A")
        
        return (f"🌤️ {city}ನಲ್ಲಿ ಹವಾಮಾನ:\n"
                f"- ಸ್ಥಿತಿ: {desc}\n"
                f"- ತಾಪಮಾನ: {temp}°C (feels like {feels_like}°C)\n"
                f"- ಆರ್ದ್ರತೆ: {humidity}%")
    
    except requests.exceptions.Timeout:
        return "❌ ಹವಾಮಾನ service timeout ಆಗಿದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ."
    except requests.exceptions.RequestException as e:
        return f"❌ ಹವಾಮಾನ service error: {str(e)}"
    except KeyError as e:
        return f"❌ ಹವಾಮಾನ data format error: {str(e)}"
    except Exception as e:
        return f"❌ ಹವಾಮಾನ ಪಡೆಯೋಕೆ ಸಾಧ್ಯವಾಗಲಿಲ್ಲ 😞: {str(e)}"
