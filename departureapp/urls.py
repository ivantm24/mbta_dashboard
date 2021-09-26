from django.urls import path

from . import views

urlpatterns = [
    path('', views.SearchStationView.as_view(), name='search_stops'),

    path('station/<str:stop_id>', views.station_board, name='station-board'),

    path('reload_stations', views.reload_stations, name='reload-stations'),
]