from django.db import models

# Create your models here.
class Track(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default=0)
    distance = models.FloatField(default=0)
    size = models.IntegerField(default=0)
    points = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
