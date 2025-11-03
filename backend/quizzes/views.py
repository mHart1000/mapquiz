from rest_framework import viewsets, generics
from django.core.serializers import serialize
from django.http import HttpResponse
from .models import Quiz, City
from .serializers import QuizSerializer, CitySerializer

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class CityList(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class CityDetail(generics.RetrieveAPIView):
    lookup_field = 'slug'
    queryset = City.objects.all()
    serializer_class = CitySerializer
