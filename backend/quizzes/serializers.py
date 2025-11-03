from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import City, Quiz

class QuizSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class CitySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = City
        geo_field = 'geometry'
        fields = ('id', 'name', 'slug')
