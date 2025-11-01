from rest_framework import viewsets
from .models import Quiz
from .serializers import QuizSerializer
from django.core.serializers import serialize
from django.http import HttpResponse
from .models import City


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

def city_list(request):
    geojson = serialize('geojson', City.objects.all())
    return HttpResponse(geojson, content_type='application/json')