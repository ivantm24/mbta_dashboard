from django.core.cache import cache as django_cache

LAST_MODIFIED_KEY = 'mbta:{0}:LAST_MODIFIED'
RESPONSE_KEY = 'mbta:{0}'


def get_last_modified(path) -> str:
    val = django_cache.get(LAST_MODIFIED_KEY.format(path))
    return val


def set_last_modified(path, last_modified: str):
    django_cache.set(LAST_MODIFIED_KEY.format(path), last_modified)


def get_response(path):
    val = django_cache.get(RESPONSE_KEY.format(path))
    return val


def set_response(path, data):
    django_cache.set(RESPONSE_KEY.format(path), data)