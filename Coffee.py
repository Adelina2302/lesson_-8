import json
import requests
from geopy import distance
import folium
import os
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_cafes_distance(cafe):
    return cafe['distance']


def main():
    load_dotenv()
    apikey = os.getenv('APIKEY')
    with open("coffee.json", "r", encoding="utf-8") as my_file:
        coffee_raw_content = my_file.read()
    coffee_content = json.loads(coffee_raw_content)

    address = input("Где вы находитесь? ")
    user_coords = fetch_coordinates(apikey, address)
    
    cafes_with_distance = []
    for cafe in coffee_content:
        name = cafe.get('Name')
        lon = cafe.get('Longitude_WGS84')
        lat = cafe.get('Latitude_WGS84')

        if not (lat and lon):
            continue

        cafe_coords = (lat, lon)
        dist = distance.distance(user_coords, cafe_coords).km

        cafes_with_distance.append({
            "title": name,
            "distance": dist,
            "latitude": lat,
            "longitude": lon,
        })

    nearest_cafes = sorted(cafes_with_distance, key=get_cafes_distance)[:5]
    
    m = folium.Map(location=[user_coords[0], user_coords[1]], zoom_start=14)

    folium.Marker(
        location=[user_coords[0], user_coords[1]],
        tooltip="Вы здесь",
        popup="Ваше местоположение",
        icon=folium.Icon(color="red", icon="home"),
    ).add_to(m)

    for cafe in nearest_cafes:
        folium.Marker(
            location=[cafe["latitude"], cafe["longitude"]],
            tooltip=cafe["title"],
            popup=cafe["title"],
            icon=folium.Icon(color="green", icon="coffee"),
        ).add_to(m)

    m.save("cafes_map.html")


if __name__ == "__main__":
    main()