from django.conf import settings
from django.db.models import Q
from django.shortcuts import render

from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView

from departureapp.models import Stop
from services.mbta import MbtaService


def index(request):
    context = {}
    return render(request, 'departureapp/index.html', context)


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
