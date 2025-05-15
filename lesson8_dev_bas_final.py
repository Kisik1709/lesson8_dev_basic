import os
import json
import folium
import logging
import requests
from geopy import distance
from decouple import config


logging.basicConfig(level=logging.DEBUG)

API_KEY = config("API_KEY")
TOP_COFFEE_SHOP = 5


def fetch_coordinates(API_KEY, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def distance_to_coffee(coffee_store_list):
    return coffee_store_list["distance"]


def main():
    logging.info("Старт программы")
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "coffee.json")

    with open(file_path, "r", encoding="CP1251") as coffees_store_file:
        coffee_store = coffees_store_file.read()

    logging.info("Данные из файла успешно загружены")
    coffee_store = json.loads(coffee_store)

    address = input("Введите Ваш адрес: ")
    user_coordinates = fetch_coordinates(API_KEY, address)
    logging.info(f"Получены координаты {user_coordinates}")

    if not user_coordinates:
        logging.error(
            "Пользователь ввел некоректные данные. Завершение программы.")
        return

    logging.info("Пользователь ввел координаты и они приняты")

    coffee_store_list = []

    for coffee_list in coffee_store:
        name = coffee_list["Name"]
        longitude, latitude = coffee_list["geoData"]["coordinates"]

        coffee_coordinates = (latitude, longitude)
        user_coordinates = (user_coordinates[1], user_coordinates[0])
        geodic = distance.distance(user_coordinates, coffee_coordinates).km

        coffee_data = {
            "title": name,
            "distance": geodic,
            "longitude": longitude,
            "latitude": latitude
        }

        coffee_store_list.append(coffee_data)

    pages = sorted(coffee_store_list, key=distance_to_coffee)

    map_coffee = folium.Map(
        location=[float(user_coordinates[1]), float(user_coordinates[0])],
        zoom_start=16)

    folium.Marker(
        location=[float(user_coordinates[1]), float(user_coordinates[0])],
        popup="Я сейчас здесь!",
        icon=folium.Icon(icon="user", prefix="fa", color='red')
    ).add_to(map_coffee)

    for coffee in pages[:TOP_COFFEE_SHOP]:
        logging.debug(
            f"Добавляю метку: {coffee['title']} — координаты: {coffee['latitude']}, {coffee['longitude']}")
        folium.Marker(
            location=[float(coffee["latitude"]), float(coffee["longitude"])],
            popup=f'{coffee["title"]}',
            icon=folium.Icon(icon="coffee", prefix="fa", color="blue")
        ).add_to(map_coffee)

    map_coffee.save('map_coffee.html')
    logging.info("Карта успешно сохранена")


if __name__ == "__main__":
    main()
