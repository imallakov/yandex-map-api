import requests
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()


class CityGuessingGame:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        # Список городов России
        self.cities = [
            {"name": "Москва", "coords": "37.6173,55.7558"},
            {"name": "Санкт-Петербург", "coords": "30.3350,59.9343"},
            {"name": "Казань", "coords": "49.1233,55.7887"},
            {"name": "Нижний Новгород", "coords": "44.0021,56.3269"},
            {"name": "Екатеринбург", "coords": "60.6122,56.8519"},
            {"name": "Новосибирск", "coords": "82.9346,55.0084"},
            {"name": "Владивосток", "coords": "131.8735,43.1056"},
            {"name": "Сочи", "coords": "39.7303,43.6028"},
            {"name": "Калининград", "coords": "20.5070,54.7065"},
            {"name": "Красноярск", "coords": "92.8672,56.0090"}
        ]

    def get_random_city(self):
        """Выбрать случайный город из списка"""
        return random.choice(self.cities)

    def get_random_zoom(self):
        """Получить случайный уровень зума"""
        return random.randint(13, 16)

    def get_random_map_type(self):
        """Случайно выбрать тип карты"""
        return 'map'
        # return random.choice(['map', 'sat'])

    def get_city_image(self, city, save_path):
        """Получить изображение города"""
        base_url = "https://static-maps.yandex.ru/1.x/"

        # Получаем координаты
        lon, lat = map(float, city["coords"].split(','))

        # Случайное смещение для того, чтобы показать разные части города
        delta = 0.02  # примерно 2км
        lon_offset = random.uniform(-delta, delta)
        lat_offset = random.uniform(-delta, delta)

        params = {
            "apikey": self.api_key,
            "l": self.get_random_map_type(),
            "ll": f"{lon + lon_offset},{lat + lat_offset}",
            "z": self.get_random_zoom(),
            "size": "650,450",
            "lang": "ru_RU"
        }

        try:
            response = requests.get(base_url, params=params)

            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                image.save(save_path)
                return True
            else:
                print(f"Error: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error getting image: {e}")
            return False

    def play_round(self):
        """Провести один раунд игры"""
        city = self.get_random_city()
        image_path = f"city_{random.randint(1000, 9999)}.png"

        if self.get_city_image(city, image_path):
            print("\nНовое изображение города сохранено как", image_path)
            print("\nПопробуйте угадать город!")
            print("Доступные города:")
            # Показываем список всех городов
            for i, c in enumerate(self.cities, 1):
                print(f"{i}. {c['name']}")

            while True:
                guess = input("\nВаш ответ (или 'выход' для завершения): ").strip()

                if guess.lower() == 'выход':
                    return False

                if guess.lower() == city['name'].lower():
                    print("Правильно! Это действительно", city['name'])
                    return True
                else:
                    print("Неверно, попробуйте еще раз!")

        return False

    def play_game(self):
        """Основной игровой цикл"""
        print("Добро пожаловать в игру 'Угадай город'!")
        print("В каждом раунде вам будет показано изображение города.")
        print("Попробуйте угадать, какой это город из списка.")

        score = 0
        rounds_played = 0

        while True:
            rounds_played += 1
            if self.play_round():
                score += 1

            print(f"\nВаш текущий счет: {score}/{rounds_played}")

            play_again = input("\nХотите сыграть еще раз? (да/нет): ").strip().lower()
            if play_again != 'да':
                break

        print(f"\nИгра окончена! Итоговый счет: {score}/{rounds_played}")


def main():
    if not os.getenv('API_KEY'):
        print("Error: API_KEY not found in environment variables")
        return

    game = CityGuessingGame()
    game.play_game()


if __name__ == "__main__":
    main()