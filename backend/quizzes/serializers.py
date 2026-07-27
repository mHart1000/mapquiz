from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
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
    shape = GeometrySerializerMethodField()

    class Meta:
        model = Neighborhood
        geo_field = 'shape'
        fields = ('id',)

    def get_shape(self, obj):
        return getattr(obj, 'simplified', None) or obj.geometry
