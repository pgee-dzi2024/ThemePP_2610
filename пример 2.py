import os
from flask import Flask, render_template, request, redirect
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import folium

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            exif_data[decoded] = value
    return exif_data


def get_gps_info(exif_data):
    gps_info = {}
    if 'GPSInfo' in exif_data:
        for key in exif_data['GPSInfo']:
            decoded = GPSTAGS.get(key, key)
            gps_info[decoded] = exif_data['GPSInfo'][key]
    return gps_info


def convert_to_degrees(value):
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)


def get_coordinates(gps_info):
    try:
        lat = convert_to_degrees(gps_info['GPSLatitude'])
        if gps_info['GPSLatitudeRef'] != 'N':
            lat = -lat

        lon = convert_to_degrees(gps_info['GPSLongitude'])
        if gps_info['GPSLongitudeRef'] != 'E':
            lon = -lon

        return lat, lon
    except:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    images_data = []

    if request.method == 'POST':
        files = request.files.getlist('photos')

        m = folium.Map(location=[42.7, 25.3], zoom_start=6)

        for file in files:
            if file.filename.lower().endswith('.jpg') or file.filename.lower().endswith('.jpeg'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                image = Image.open(filepath)
                exif_data = get_exif_data(image)
                gps_info = get_gps_info(exif_data)
                coords = get_coordinates(gps_info)

                has_gps = coords is not None

                images_data.append({
                    'filename': file.filename,
                    'gps': has_gps
                })

                if has_gps:
                    lat, lon = coords
                    popup_text = f"""
                    <b>{file.filename}</b><br>
                    Date: {exif_data.get('DateTime', 'N/A')}
                    """
                    folium.Marker(
                        location=[lat, lon],
                        popup=popup_text
                    ).add_to(m)

        m.save('templates/map.html')
        return render_template('index.html', images=images_data, show_map=True)

    return render_template('index.html', images=[], show_map=False)


@app.route('/clear')
def clear():
    for file in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, file))
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
