import requests
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_satellite_image(api_key, longitude, latitude, zoom=16):
    """
    Download satellite image for given coordinates

    Args:
        api_key (str): Yandex Maps API key
        longitude (float): Longitude coordinate
        latitude (float): Latitude coordinate
        zoom (int): Zoom level (1-17)

    Returns:
        bool: True if successful, False otherwise
    """
    base_url = "https://static-maps.yandex.ru/1.x/"

    params = {
        "apikey": api_key,
        "l": "map",  # Layer type should be 'sat' for satellite but api doesn't allow?
        "ll": f"{latitude},{longitude}",  # Location
        "z": zoom,  # Zoom level
        "size": "650,450",  # Image size
        "lang": "ru_RU"
    }

    try:
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            # Save the image
            image = Image.open(BytesIO(response.content))
            filename = f"satellite_image_{longitude}_{latitude}.png"
            image.save(filename)
            print(f"Satellite image saved as {filename}")
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

    if not api_key:
        print("Error: API_KEY not found in environment variables")
        return

    try:
        # Get coordinates from user
        print("Enter coordinates for the location:")
        longitude = float(input("Longitude (e.g., 37.6173): "))
        latitude = float(input("Latitude (e.g., 55.7558): "))

        # Optional: get zoom level
        zoom = input("Enter zoom level (1-17, default is 16): ")
        zoom = int(zoom) if zoom.strip() else 16

        if zoom < 1 or zoom > 17:
            print("Invalid zoom level. Using default zoom level of 16.")
            zoom = 16

        # Get and save the satellite image
        get_satellite_image(api_key, longitude, latitude, zoom)

    except ValueError:
        print("Error: Please enter valid numerical coordinates")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()