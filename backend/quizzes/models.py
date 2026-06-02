from django.contrib.gis.db import models
from django.utils.text import slugify

class Quiz(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    geometry = models.MultiPolygonField(srid=4326, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(City, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Neighborhood(models.Model):
    city = models.ForeignKey(City, related_name='neighborhoods', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    geometry = models.MultiPolygonField(srid=4326)

    class Meta:
        # slug is unique within a city, not globally
        constraints = [
            models.UniqueConstraint(fields=['city', 'slug'], name='unique_neighborhood_slug_per_city'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Neighborhood, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.city.name})'
