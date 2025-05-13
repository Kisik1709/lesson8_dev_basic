import os
import json
import folium
import requests
from geopy import distance
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")
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
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "coffee.json")

    with open(file_path, "r", encoding="CP1251") as coffees_store_file:
        coffee_store = coffees_store_file.read()

    coffee_store = json.loads(coffee_store)

    address = input("Введите Ваш адрес: ")
    user_coordinates = fetch_coordinates(API_KEY, address)
    print("Ваши координаты: ", user_coordinates)

    coffee_store_list = []

    for coffee_list in coffee_store:
        name = coffee_list["Name"]
        longitude = coffee_list["geoData"]["coordinates"][0]
        latitude = coffee_list["geoData"]["coordinates"][1]

        coffee_coordinates = (longitude, latitude)
        geodic = distance.distance(user_coordinates, coffee_coordinates).km

        coffee_data = {
            "title": name,
            "distance": geodic,
            "latitude": latitude,
            "longitude": longitude
        }

        coffee_store_list.append(coffee_data)

    pages = sorted(coffee_store_list, key=distance_to_coffee)

    map_coffee = folium.Map(
        location=[float(user_coordinates[1]), float(user_coordinates[0])], zoom_start=16)

    folium.Marker(
        location=[float(user_coordinates[1]), float(user_coordinates[0])],
        popup="Я сейчас здесь!",
        icon=folium.Icon(color='red')
    ).add_to(map_coffee)

    for coffee in pages[:TOP_COFFEE_SHOP]:
        folium.Marker(
            location=[coffee["latitude"], coffee["longitude"]],
            popup=f'{coffee["title"]}',
            icon=folium.Icon(color="blue")
        ).add_to(map_coffee)

    map_coffee.save('map_coffee.html')


if __name__ == "__main__":
    main()
