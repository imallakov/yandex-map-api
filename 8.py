import math
import os

import requests
from dotenv import load_dotenv


def get_coordinates(address, api_key):
    """
    Получает координаты (долгота, широта) для указанного адреса
    """
    url = f"https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": api_key,
        "geocode": address,
        "format": "json",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    geo_data = response.json()
    try:
        pos = geo_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        lon, lat = map(float, pos.split())
        return lon, lat
    except (KeyError, IndexError):
        raise ValueError(f"Не удалось найти координаты для адреса: {address}")


def lonlat_distance(a, b):
    """
    Считает расстояние между двумя точками (долгота, широта) в метрах
    """
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее
    radians_lattitude = math.radians((a_lat + b_lat) / 2.0)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


def main():
    load_dotenv()
    api_key = os.getenv('GEOCODE_API_KEY')

    home_address = input("Введите адрес вашего дома: ")
    university_address = input("Введите адрес университета: ")

    try:
        home_coords = get_coordinates(home_address, api_key)
        university_coords = get_coordinates(university_address, api_key)

        distance = lonlat_distance(home_coords, university_coords)
        print(f"Расстояние от дома до университета: {distance:.2f} метров")
    except ValueError as e:
        print(e)
    except requests.RequestException as e:
        print(f"Ошибка при запросе к API Яндекс.Карт: {e}")


if __name__ == "__main__":
    main()
