   from PIL import Image, ExifTags


def get_decimal_from_dms(dms, ref):
    """ Преобразува градуси, минути и секунди в десетични координати """
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])

    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

    # Ако посоката е Юг или Запад, координатата е отрицателна
    if ref in ['S', 'W']:
        decimal = -decimal

    return decimal


def extract_exif_data(image_file):
    """ Извлича дата и GPS координати от снимка """
    try:
        img = Image.open(image_file)
        exif_raw = img._getexif()

        if not exif_raw:
            return None, None, None

            # Декодиране на основните Exif тагове
        exif_data = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}

        # Извличане на датата на заснемане
        # Форматът обикновено е: 'YYYY:MM:DD HH:MM:SS'
        datetime_taken = exif_data.get('DateTimeOriginal')

        # Извличане на GPS данни
        lat, lon = None, None
        if 'GPSInfo' in exif_data:
            gps_info = {}
            for key in exif_data['GPSInfo'].keys():
                decode = ExifTags.GPSTAGS.get(key, key)
                gps_info[decode] = exif_data['GPSInfo'][key]

                # Проверка дали имаме нужната информация за ширина и дължина
            if all(k in gps_info for k in ['GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']):
                lat = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
                lon = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])

        return datetime_taken, lat, lon

    except Exception as e:
        print(f"Грешка при четене на Exif: {e}")
        return None, None, None