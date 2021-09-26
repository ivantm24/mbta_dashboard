from datetime import datetime

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView

from departureapp.models import Stop
from services.mbta import MbtaService

EMPTY = '-'


def station_board(request, stop_id):
    stop = get_object_or_404(Stop, pk=stop_id)
    context = {'station_name': stop.name, 'description': stop.description}
    mbta_service = MbtaService(settings.MBTA_HOST)
    predictions = mbta_service.get_predictions(stop_id)['data']

    object_list = []
    for p in predictions:
        attributes = p['attributes']

        # set display time
        schedule_time = None
        schedule_data = p['relationships']['schedule']['data']
        if schedule_data is not None:
            schedule_time = schedule_data['attributes']['departure_time']
        if attributes['departure_time'] is not None:
            display_time = attributes['departure_time']
        else:
            display_time = schedule_time
        if display_time is None:
            continue
        else:
            departure_date = datetime.strptime(display_time, "%Y-%m-%dT%H:%M:%S%z")
            display_time = departure_date.strftime("%I:%M %p")

        # set display destination
        display_destination = EMPTY
        trip_data = p['relationships']['trip']['data']
        if trip_data is not None:
            trip_attr = trip_data['attributes']
            if 'headsign' in trip_attr:
                display_destination = trip_attr['headsign']

        # set train
        vehicle_attr = None
        vehicle_data = p['relationships']['vehicle']['data']
        if vehicle_data is not None:
            vehicle_attr = vehicle_data['attributes']
        display_train = EMPTY
        if vehicle_data is not None and vehicle_attr is not None:
            display_train = vehicle_attr['label']

        # set display_status
        display_status = attributes['status']
        if display_status is None:
            display_status = EMPTY

        # set track
        display_track = None
        stop_data = p['relationships']['stop']['data']
        if stop_data is not None:
            stop_attr = stop_data['attributes']
            display_track = stop_attr['platform_code']
            if display_track is None:
                display_track = stop_attr['platform_name']
        if display_track is None:
            display_track = EMPTY

        station = {
            'carrier': 'mbta',
            'time': display_time,
            'destination': display_destination,
            'train': display_train,
            'track': display_track,
            'status': display_status,
            'departure_date': departure_date
        }
        object_list.append(station)
        object_list = sorted(object_list, key=lambda k: k['departure_date'])
    context['object_list'] = object_list
    return render(request, 'departureapp/station_board.html', context)


class SearchStationView(ListView):
    model = Stop
    template_name = 'departureapp/search_stops.html'
    ordering = ['name', 'description', 'id']

    def get_context_data(self, *args, object_list=None, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        query = self.request.GET.get('q')
        if query is not None:
            data['q'] = query
        return data

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query is None:
            return {}
        object_list = Stop.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        return object_list


def reload_stations(request):
    mbta_service = MbtaService(settings.MBTA_HOST)
    stops = mbta_service.get_stops()
    total = 0
    ok_count = 0
    fk_dict = {}
    for s in stops['data']:
        total += 1
        stop_id = s['id']
        attributes = s['attributes']
        name = attributes['name']
        description = attributes['description']
        platform_name = attributes['platform_name']
        municipality = attributes['municipality']
        latitude = attributes['latitude']
        longitude = attributes['longitude']
        relationships = s['relationships']
        parent_node = None
        if relationships['parent_station']['data'] is not None:
            parent_id = relationships['parent_station']['data']['id']
            try:
                parent_node = Stop.objects.get(id=parent_id)
            except Stop.DoesNotExist:
                fk_dict[stop_id] = parent_id
        Stop.objects.update_or_create(
            id=stop_id,
            defaults={
                "name": name,
                "description": description,
                "platform_name": platform_name,
                "municipality": municipality,
                "latitude": latitude,
                "longitude": longitude,
                "parent_stop": parent_node
            }
        )
        ok_count += 1

    total_retries = 0
    bad_retries = 0
    for stop_id, parent_id in fk_dict.items():
        parent_stop = None
        try:
            parent_stop = Stop.objects.get(id=parent_id)
        except Stop.DoesNotExist:
            bad_retries += 1
        Stop.objects.update(id=stop_id, defaults={"parent_stop": parent_stop})
        total_retries += 1

    return JsonResponse(
        {'ok_count': ok_count, 'total': total, 'total_retries': total_retries, 'bad_retries': bad_retries}
    )
