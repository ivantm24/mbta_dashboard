from django.db import models


class Stop(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # 48 longest id
    name = models.CharField(max_length=120)  # 75 longest
    description = models.CharField(max_length=200, null=True)  # 114 longest
    platform_name = models.CharField(max_length=60, null=True)  # 36 longest
    municipality = models.CharField(max_length=40)  # 21 longest
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    parent_stop = models.ForeignKey("self", null=True, on_delete=models.CASCADE)

