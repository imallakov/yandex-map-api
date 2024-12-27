import requests
import os
from dotenv import load_dotenv
from math import radians, cos, sqrt

# Load environment variables
load_dotenv()


def lonlat_distance(a, b):
    """Calculate distance between two points in meters"""
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = radians((a_lat + b_lat) / 2.)
    lat_lon_factor = cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    return sqrt(dx * dx + dy * dy)


def get_coordinates(api_key, address):
    """Get coordinates for an address using Yandex Geocoder"""
    base_url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        "apikey": api_key,
        "geocode": address,
        "format": "json"
    }

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            features = data["response"]["GeoObjectCollection"]["featureMember"]

            if features:
                coords_str = features[0]["GeoObject"]["Point"]["pos"]
                lon, lat = map(float, coords_str.split())
                return lon, lat
            else:
                print("Address not found")
                return None

        else:
            print(f"Geocoding error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error getting coordinates: {e}")
        return None


def find_nearest_pharmacy(api_key, coords):
    """Find nearest pharmacy using Yandex Organization Search"""
    search_url = "https://search-maps.yandex.ru/v1/"

    params = {
        "apikey": api_key,
        "text": "аптека",
        "ll": f"{coords[0]},{coords[1]}",
        "type": "biz",
        "lang": "ru_RU",
        "results": 10,
        "spn": "0.02,0.02"
    }

    try:
        response = requests.get(search_url, params=params)

        if response.status_code == 200:
            data = response.json()

            if not data.get("features"):
                print("No pharmacies found nearby")
                return None

            # Find nearest pharmacy
            nearest = None
            min_distance = float('inf')

            for feature in data["features"]:
                pharmacy_coords = feature["geometry"]["coordinates"]
                distance = lonlat_distance(coords, pharmacy_coords)

                if distance < min_distance:
                    min_distance = distance
                    nearest = {
                        "name": feature["properties"]["CompanyMetaData"].get("name", "Неизвестная аптека"),
                        "address": feature["properties"]["CompanyMetaData"].get("address", "Адрес не указан"),
                        "distance": distance,
                        "coordinates": pharmacy_coords
                    }

            return nearest

        else:
            print(f"Search error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error finding pharmacy: {e}")
        return None


def main():
    # Get API keys from environment variables
    geocoder_api_key = os.getenv('GEOCODE_API_KEY')
    search_api_key = os.getenv('SEARCH_API_KEY')  # You'll need a separate key for organization search

    if not geocoder_api_key or not search_api_key:
        print("Error: API keys not found in environment variables")
        return

    # Get address from user
    address = input("Введите ваш адрес: ").strip()

    if not address:
        print("Адрес не введен")
        return

    # Get coordinates for the address
    coords = get_coordinates(geocoder_api_key, address)

    if not coords:
        return

    print(f"Координаты адреса: {coords}")

    # Find nearest pharmacy
    nearest = find_nearest_pharmacy(search_api_key, coords)

    if nearest:
        print("\nБлижайшая аптека:")
        print(f"Название: {nearest['name']}")
        print(f"Адрес: {nearest['address']}")
        print(f"Расстояние: {nearest['distance']:.0f} метров")

        # Optionally: Generate a static map showing both points
        map_url = (
            "https://static-maps.yandex.ru/1.x/"
            f"?apikey={geocoder_api_key}"
            f"&ll={coords[0]},{coords[1]}"
            "&l=map"
            "&z=15"
            f"&pt={coords[0]},{coords[1]},pm2rdm~"
            f"{nearest['coordinates'][0]},{nearest['coordinates'][1]},pm2gnm"
        )

        print("\nКарта доступна по ссылке:")
        print(map_url)


if __name__ == "__main__":
    main()