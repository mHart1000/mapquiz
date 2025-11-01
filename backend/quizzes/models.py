from django.db import models

class Quiz(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    geometry = models.MultiPolygonField(srid=4326)


    def __str__(self):
        return self.name
