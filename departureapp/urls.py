from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('reload_stations', views.reload_stations, name='reload-stations'),
]