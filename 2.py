import requests
from PIL import Image
from io import BytesIO
import math
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 kilometers in meters
    a_lon, a_lat = a
    b_lon, b_lat = b

    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    return math.sqrt(dx * dx + dy * dy)


def calculate_path_length(coordinates):
    total_distance = 0
    for i in range(len(coordinates) - 1):
        total_distance += lonlat_distance(coordinates[i], coordinates[i + 1])
    return total_distance


def get_middle_point(coordinates):
    if not coordinates:
        return None

    middle_idx = len(coordinates) // 2
    return coordinates[middle_idx]


def visualize_path(api_key, coordinates):
    base_url = "https://static-maps.yandex.ru/1.x/"

    # Create path string in the correct format for Yandex API
    path_points = []
    for lon, lat in coordinates:
        path_points.append(f"{lon:.6f},{lat:.6f}")  # Yandex polyline expects lon,lat

    # Get middle point for marker
    middle_point = get_middle_point(coordinates)
    middle_point_str = f"{middle_point[0]},{middle_point[1]}"  # lon,lat
    # f"c:blue,w:3," +
    params = {
        "apikey": api_key,
        "l": "map",
        "pl": ",".join(path_points),  # Path line
        "pt": f"{middle_point_str},pm2rdm",  # Middle point marker
        "z": 13,
        "size": "650,450",
        "lang": "ru_RU"
    }

    try:
        response = requests.get(base_url, params=params)

        # Print URL for debugging (remove in production)
        print("Request URL:", response.url)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image.save("path_visualization.png")
            print("Map saved as path_visualization.png")
            return True
        else:
            print(f"Error: {response.status_code}")
            print("Response content:", response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False


def main():
    # Get API key from environment variable
    api_key = os.getenv('API_KEY')

    if not api_key:
        print("Error: API_KEY not found in environment variables")
        return

    # Example coordinates of Moscow landmarks (longitude, latitude)
    coordinates = [
        (37.617635, 55.752121),  # Red Square
        (37.630510, 55.743749),  # Zaryadye Park
        (37.545517, 55.747012),  # Moscow City
        (37.595512, 55.741283)  # Gorky Park
    ]

    # Calculate total path length
    total_distance = calculate_path_length(coordinates)
    print(f"Total path length: {total_distance / 1000:.2f} km")

    # Visualize path
    if visualize_path(api_key, coordinates):
        print("Path visualization saved as path_visualization.png")
    else:
        print("Failed to generate path visualization")


if __name__ == "__main__":
    main()
