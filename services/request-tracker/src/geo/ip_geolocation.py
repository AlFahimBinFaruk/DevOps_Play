import requests
from typing import Optional,Dict

def get_getlocation(ip:str) -> Dict[str,Optional[str]]:
    """
    Get geolocation from IP address using ip-api.com (free, no API key needed)
    Returns dict with country, city, lat, lon or None values
    """
    if not ip or ip == "127.0.0.1" or ip.startswith("192.168.") or ip.startswith("10."):
        return {"country": None, "city": None, "latitude": None, "longitude": None}

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon", timeout=5)

        if response.status_code == 200:
            data=response.json()
            if data.get("status") == "success":
                return {
                    "country": data.get("country"),
                    "city": data.get("city"),
                    "latitude": data.get("lat"),
                    "longitude": data.get("lon")
                }
    except Exception as e:
        print(f"Geolocation lookup failed for IP {ip}: {e}")
        return {"country": None, "city": None, "latitude": None, "longitude": None}