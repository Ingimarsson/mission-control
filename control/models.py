from django.db import models

class Track(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default=0)
    distance = models.FloatField(default=0)
    size = models.IntegerField(default=0)
    points = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Data(models.Model):
    id = models.AutoField(primary_key=True)
    track = models.ForeignKey(Track, models.SET_NULL, null=True, blank=True)
    driver = models.CharField(max_length=255, default='')
    comment = models.CharField(max_length=255, default='')
    duration = models.IntegerField(default=0)
    distance = models.FloatField(default=0)
    filesize = models.FloatField(default=0)
    filename = models.CharField(max_length=255, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

