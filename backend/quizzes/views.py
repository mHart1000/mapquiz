import random

from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Quiz, City, Neighborhood
from .serializers import QuizSerializer, CitySerializer, NeighborhoodSerializer

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

class NeighborhoodList(generics.ListAPIView):
    """FeatureCollection of a city's neighborhoods (id + geometry only)."""
    serializer_class = NeighborhoodSerializer

    def get_queryset(self):
        return Neighborhood.objects.filter(city__slug=self.kwargs['slug'])

class QuizQuestion(APIView):
    """Pick a random neighborhood and return its name as the prompt."""
    def get(self, request, slug):
        names = list(
            Neighborhood.objects.filter(city__slug=slug).values_list('name', flat=True)
        )
        if not names:
            return Response({'detail': 'No neighborhoods for this city.'}, status=404)
        return Response({'target_name': random.choice(names)})

class QuizAnswer(APIView):
    """Validate a clicked neighborhood against the target name."""
    def post(self, request, slug):
        target_name = request.data.get('target_name')
        clicked_id = request.data.get('clicked_id')
        target = get_object_or_404(
            Neighborhood, city__slug=slug, name=target_name
        )
        return Response({
            'correct': clicked_id is not None and int(clicked_id) == target.id,
            'correct_id': target.id,
        })
