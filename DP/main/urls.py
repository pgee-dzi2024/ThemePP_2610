from django.urls import path
from .views import *

# По-късно ще добавим и път за самия HTML файл (фронтенда),
# но засега регистрираме само API Endpoint-ите
urlpatterns = [
    path('old', IndexViewOld.as_view(), name='home_old'),
    path('', IndexView.as_view(), name='index'), # Това зарежда фронтенда
    path('api/photos/upload/', PhotoUploadView.as_view(), name='api-photo-upload'),
    path('api/photos/', PhotoListView.as_view(), name='api-photo-list'),
    path('api/photos/<int:pk>/', PhotoDeleteView.as_view(), name='api-photo-delete'),
    path('api/photos/clear/', ProjectClearView.as_view(), name='api-project-clear'),
]


