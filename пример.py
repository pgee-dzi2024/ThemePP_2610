import os
from PIL import Image, ExifTags
import folium


def get_gps_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()

    if not exif_data:
        return None

    gps_info = {}
    for tag, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag)
        if tag_name == "GPSInfo":
            for t in value:
                sub_tag = ExifTags.GPSTAGS.get(t)
                gps_info[sub_tag] = value[t]

    return gps_info


def convert_to_degrees(value):
    d, m, s = value
    return float(d) + float(m) / 60 + float(s) / 3600


def get_coordinates(gps_info):
    if not gps_info:
        return None

    lat = convert_to_degrees(gps_info["GPSLatitude"])
    if gps_info["GPSLatitudeRef"] == "S":
        lat = -lat

    lon = convert_to_degrees(gps_info["GPSLongitude"])
    if gps_info["GPSLongitudeRef"] == "W":
        lon = -lon

    return lat, lon


def create_map(images_folder):
    travel_map = folium.Map(location=[42.7, 25.4], zoom_start=6)

    for file in os.listdir(images_folder):
        if file.lower().endswith((".jpg", ".jpeg")):
            path = os.path.join(images_folder, file)
            gps_info = get_gps_data(path)
            coords = get_coordinates(gps_info)

            if coords:
                folium.Marker(
                    location=coords,
                    popup=file,
                    icon=folium.Icon(color="blue", icon="camera")
                ).add_to(travel_map)

    travel_map.save("my_trip.html")


if __name__ == "__main__":
    create_map("images")
