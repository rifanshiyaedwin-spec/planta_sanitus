import requests
import os

# Use Open-Meteo (no API key) for simple forecast
DEFAULT_LAT = float(os.environ.get('DEFAULT_LAT', '12.9716'))  # example: Bangalore
DEFAULT_LON = float(os.environ.get('DEFAULT_LON', '77.5946'))

def get_weather_forecast(lat=None, lon=None):
    lat = lat or DEFAULT_LAT
    lon = lon or DEFAULT_LON
    try:
        url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto'
        resp = requests.get(url, timeout=5)
        data = resp.json()
        # Return a small summarized structure
        daily = data.get('daily', {})
        forecast = {
            'max_temp': daily.get('temperature_2m_max', [])[0] if daily.get('temperature_2m_max') else None,
            'min_temp': daily.get('temperature_2m_min', [])[0] if daily.get('temperature_2m_min') else None,
            'precipitation': daily.get('precipitation_sum', [])[0] if daily.get('precipitation_sum') else None,
        }
        return {'source':'open-meteo','forecast':forecast}
    except Exception:
        # Fallback mocked forecast
        return {'source':'mock','forecast': {'max_temp': 30, 'min_temp': 22, 'precipitation': 2}}
