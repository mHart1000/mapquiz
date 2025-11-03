from rest_framework import viewsets, generics
from django.core.serializers import serialize
from django.http import HttpResponse
from .models import Quiz, City
from .serializers import QuizSerializer, CitySerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

def city_list(request):
    geojson = serialize('geojson', City.objects.all())
    return HttpResponse(geojson, content_type='application/json')

class CityDetail(generics.RetrieveAPIView):
    lookup_field = 'slug'
    queryset = City.objects.all()
    serializer_class = CitySerializer
