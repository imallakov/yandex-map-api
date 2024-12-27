import os

import requests
from PIL import Image
from io import BytesIO


def get_map_image(api_key, stadiums_location):
    # Base URL for Yandex Static Maps API
    base_url = "https://static-maps.yandex.ru/1.x/"

    # Create points string for all stadiums
    # Reverse coordinates order for Yandex Maps API (lon,lat to lat,lon)
    points = []
    for name, coords in stadiums_location.items():
        lat, lon = coords.split(',')
        points.append(f"{lat},{lon},pm2rdm")

    # Parameters for the API request
    params = {
        "apikey": api_key,
        "l": "map",  # Layer type (map)
        "pt": "~".join(points),  # Points with markers
        "z": 11,  # Zoom level
        "size": "650,450",  # Image size
        "lang": "ru_RU"  # Language setting for Russian labels
    }

    try:
        # Make the request
        response = requests.get(base_url, params=params)

        # Print the URL for debugging (remove in production)
        print("Request URL:", response.url)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.save("moscow_stadiums.png")
            print("Map saved as moscow_stadiums.png")
            return True
        else:
            print(f"Error: {response.status_code}")
            print("Response content:", response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False


def main():
    api_key = os.getenv('API_KEY')

    # Stadium coordinates (latitude,longitude format)
    stadiums_location = {
        "Лужники": "37.554191,55.715551",
        "Спартак": "37.440262,55.818015",
        "Динамо": "37.559809,55.791540"
    }

    get_map_image(api_key, stadiums_location)


if __name__ == "__main__":
    main()