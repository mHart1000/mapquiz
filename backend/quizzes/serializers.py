from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import City, Quiz, Neighborhood

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class CitySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = City
        geo_field = 'geometry'
        fields = ('id', 'name', 'slug')

class NeighborhoodSerializer(GeoFeatureModelSerializer):
    """Anonymized shapes for quiz rendering: id + geometry only, name omitted
    so the answer mapping never ships to the client."""
    class Meta:
        model = Neighborhood
        geo_field = 'geometry'
        fields = ('id',)
