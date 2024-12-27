import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_city_coordinates(api_key, city_name):
    """
    Get coordinates for a city using Yandex Geocoder API

    Args:
        api_key (str): Yandex Geocoder API key
        city_name (str): Name of the city

    Returns:
        tuple: (latitude, longitude) or None if not found
    """
    base_url = "https://geocode-maps.yandex.ru/1.x/"

    params = {
        "apikey": api_key,
        "geocode": city_name,
        "format": "json",
        "results": 1
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Get the first result's coordinates
            features = data["response"]["GeoObjectCollection"]["featureMember"]

            if features:
                # Get coordinates (they come as "longitude latitude")
                coords_str = features[0]["GeoObject"]["Point"]["pos"]
                lon, lat = map(float, coords_str.split())
                return lat, lon  # Return as (latitude, longitude)
            else:
                print(f"City not found: {city_name}")
                return None

        else:
            print(f"Error for {city_name}: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error processing {city_name}: {e}")
        return None


def find_southernmost_city(cities_data):
    """
    Find the southernmost city from a list of (city, coordinates) pairs

    Args:
        cities_data (list): List of tuples (city_name, (latitude, longitude))

    Returns:
        str: Name of the southernmost city
    """
    if not cities_data:
        return None

    # Find city with minimum latitude
    return min(cities_data, key=lambda x: x[1][0] if x[1] else float('inf'))[0]


def main():
    api_key = os.getenv('GEOCODE_API_KEY')

    if not api_key:
        print("Error: API_KEY not found in environment variables")
        return

    # Get input from user
    print("Enter city names separated by comma (e.g., Moscow, Saint Petersburg, Novosibirsk):")
    cities_input = input().strip()

    # Split and clean input
    cities = [city.strip() for city in cities_input.split(',') if city.strip()]

    if not cities:
        print("No valid cities entered")
        return

    # Get coordinates for each city
    cities_with_coords = []
    for city in cities:
        coords = get_city_coordinates(api_key, city)
        if coords:
            cities_with_coords.append((city, coords))
            print(f"Found coordinates for {city}: {coords}")

    if not cities_with_coords:
        print("Could not find coordinates for any of the entered cities")
        return

    # Find southernmost city
    southernmost = find_southernmost_city(cities_with_coords)
    if southernmost:
        print(f"\nThe southernmost city is: {southernmost}")


if __name__ == "__main__":
    main()