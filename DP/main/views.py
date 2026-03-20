import os
from datetime import datetime

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Photo
from .serializers import PhotoSerializer
from .utils import extract_exif_data

from django.views.generic import TemplateView

class IndexView(TemplateView):
    template_name = 'main\index.html'

class PhotoUploadView(APIView):
    def post(self, request, *args, **kwargs):
        # Взимаме списъка с качени файлове от ключа 'images'
        files = request.FILES.getlist('images')
        if not files:
            return Response({"error": "Няма прикачени файлове."}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_photos = []
        for file in files:
            # Използваме функцията от Стъпка 2
            dt_taken, lat, lon = extract_exif_data(file)

            # Парсване на датата от Exif (формат "YYYY:MM:DD HH:MM:SS") към datetime обект
            parsed_date = None
            if dt_taken:
                try:
                    parsed_date = datetime.strptime(dt_taken, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    pass

                    # Проверка дали имаме валидни координати
            has_gps = lat is not None and lon is not None

            # Запис в базата данни
            photo = Photo.objects.create(
                image=file,
                filename=file.name,
                datetime_taken=parsed_date,
                latitude=lat,
                longitude=lon,
                has_gps=has_gps
            )
            uploaded_photos.append(photo)

        serializer = PhotoSerializer(uploaded_photos, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PhotoListView(APIView):
    def get(self, request, *args, **kwargs):
        # Връщаме всички снимки, сортирани по дата на качване (най-новите първи)
        photos = Photo.objects.all().order_by('-uploaded_at')
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)


class PhotoDeleteView(APIView):
    def delete(self, request, pk, *args, **kwargs):
        try:
            photo = Photo.objects.get(pk=pk)
            # Изтриваме самия файл от директорията media
            if photo.image and os.path.isfile(photo.image.path):
                os.remove(photo.image.path)
                # Изтриваме записа от базата данни
            photo.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Photo.DoesNotExist:
            return Response({"error": "Снимката не е намерена."}, status=status.HTTP_404_NOT_FOUND)


class ProjectClearView(APIView):
    def delete(self, request, *args, **kwargs):
        # Изтриваме всички файлове физически
        photos = Photo.objects.all()
        for photo in photos:
            if photo.image and os.path.isfile(photo.image.path):
                os.remove(photo.image.path)
                # Изтриваме всички записи от базата
        photos.delete()
        return Response({"message": "Проектът е изчистен успешно."}, status=status.HTTP_204_NO_CONTENT)


def index(request):
    return render(request, 'main/index_old.html')
