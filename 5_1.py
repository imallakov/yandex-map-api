import requests
import os
from dotenv import load_dotenv
from math import radians, cos, sqrt
import time


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
    """Get coordinates using Yandex Geocoder"""
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


def find_nearest_pharmacy_osm(coords):
    """Find nearest pharmacy using OpenStreetMap Overpass API"""
    # Using Overpass API
    overpass_url = "https://overpass-api.de/api/interpreter"

    # Search for pharmacies within 2km radius
    radius = 2000  # meters
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="pharmacy"](around:{radius},{coords[1]},{coords[0]});
      way["amenity"="pharmacy"](around:{radius},{coords[1]},{coords[0]});
      relation["amenity"="pharmacy"](around:{radius},{coords[1]},{coords[0]});
    );
    out body;
    >;
    out skel qt;
    """

    try:
        response = requests.post(overpass_url, data={"data": query})

        if response.status_code == 200:
            data = response.json()

            if not data.get("elements"):
                print("No pharmacies found nearby")
                return None

            # Find nearest pharmacy
            nearest = None
            min_distance = float('inf')

            for element in data["elements"]:
                if element["type"] == "node":  # Process only nodes for simplicity
                    pharmacy_coords = (element.get("lon"), element.get("lat"))
                    distance = lonlat_distance(coords, pharmacy_coords)

                    if distance < min_distance:
                        min_distance = distance
                        nearest = {
                            "name": element.get("tags", {}).get("name", "Неизвестная аптека"),
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
    load_dotenv()
    api_key = os.getenv('GEOCODE_API_KEY')

    if not api_key:
        print("Error: API_KEY not found in environment variables")
        return

    # Get address from user
    address = input("Введите ваш адрес: ").strip()

    if not address:
        print("Адрес не введен")
        return

    # Get coordinates for the address using Yandex Geocoder
    coords = get_coordinates(api_key, address)

    if not coords:
        return

    print(f"Координаты адреса: {coords}")

    # Find nearest pharmacy using OpenStreetMap
    print("Поиск ближайших аптек...")
    nearest = find_nearest_pharmacy_osm(coords)

    if nearest:
        print("\nБлижайшая аптека:")
        print(f"Название: {nearest['name']}")
        print(f"Расстояние: {nearest['distance']:.0f} метров")

        # Generate a static map URL using Yandex Static Maps API
        map_url = (
            "https://static-maps.yandex.ru/1.x/"
            f"?apikey={api_key}"
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