import requests
import os
from dotenv import load_dotenv
import sys

load_dotenv()


class DistrictFinder:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEOCODE_API_KEY')
        self.base_url = "https://geocode-maps.yandex.ru/1.x/"

    def get_coordinates(self, address):
        """Получить координаты по адресу"""
        params = {
            "apikey": self.api_key,
            "geocode": address,
            "format": "json"
        }

        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                features = data["response"]["GeoObjectCollection"]["featureMember"]

                if features:
                    coords_str = features[0]["GeoObject"]["Point"]["pos"]
                    return coords_str.split()
                else:
                    print("Адрес не найден")
                    return None

            else:
                print(f"Ошибка получения координат: {response.status_code}")
                return None

        except Exception as e:
            print(f"Ошибка при запросе координат: {e}")
            return None

    def get_district(self, coords):
        """Получить район по координатам"""
        params = {
            "apikey": self.api_key,
            "geocode": f"{coords[0]},{coords[1]}",
            "kind": "district",
            "format": "json"
        }

        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                features = data["response"]["GeoObjectCollection"]["featureMember"]

                # Найдем первый объект с типом district
                for feature in features:
                    geo_object = feature["GeoObject"]
                    meta_data = geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {})

                    # Получаем информацию о типе объекта и его названии
                    if meta_data.get("kind") == "district":
                        district_name = geo_object.get("name", "")
                        district_description = geo_object.get("description", "")
                        return {
                            "name": district_name,
                            "description": district_description
                        }

                print("Район не найден")
                return None

            else:
                print(f"Ошибка получения района: {response.status_code}")
                return None

        except Exception as e:
            print(f"Ошибка при запросе района: {e}")
            return None

    def find_district(self, address):
        """Основной метод для поиска района по адресу"""
        print(f"\nИщем район для адреса: {address}")

        # Получаем координаты
        coords = self.get_coordinates(address)
        if not coords:
            return

        print(f"Найдены координаты: {coords[0]}, {coords[1]}")

        # Получаем район
        district_info = self.get_district(coords)
        if district_info:
            print("\nНайдена информация о районе:")
            print(f"Название: {district_info['name']}")
            if district_info['description']:
                print(f"Описание: {district_info['description']}")
        else:
            print("Не удалось определить район")


def main():
    # Проверяем наличие API ключа
    if not os.getenv('GEOCODE_API_KEY'):
        print("Ошибка: API_KEY не найден в переменных окружения")
        return

    finder = DistrictFinder()

    # Если адрес передан как аргумент командной строки
    if len(sys.argv) > 1:
        address = ' '.join(sys.argv[1:])
    else:
        # Иначе запрашиваем адрес у пользователя
        address = input("Введите адрес: ").strip()

    if not address:
        print("Адрес не указан")
        return

    finder.find_district(address)


if __name__ == "__main__":
    main()
