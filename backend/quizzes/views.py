import random

from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.gis.db.models.functions import GeomOutputGeoFunc

from .models import Quiz, City, Neighborhood
from .serializers import QuizSerializer, CitySerializer, NeighborhoodSerializer

SIMPLIFY_TOLERANCE = 0.00005
MAX_ROUND_SEED = 2 ** 31


class SimplifyPreserveTopology(GeomOutputGeoFunc):
    """Django ships no Simplify wrapper, so call the PostGIS function directly."""
    function = 'ST_SimplifyPreserveTopology'
    arity = 2
    geom_param_pos = (0,)


def round_order(slug, seed):
    """The question order for a round, rebuilt identically on every request.

    order_by('id') is required: without it Postgres makes no row-order promise,
    so the same seed would not reproduce the same shuffle.
    """
    neighborhoods = list(
        Neighborhood.objects.filter(city__slug=slug)
        .order_by('id')
        .values_list('id', 'name')
    )
    return random.Random(seed).sample(neighborhoods, len(neighborhoods))


def read_int(params, key):
    try:
        return int(params[key])
    except (KeyError, TypeError, ValueError):
        return None


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
        return (
            Neighborhood.objects.filter(city__slug=self.kwargs['slug'])
            .annotate(simplified=SimplifyPreserveTopology('geometry', SIMPLIFY_TOLERANCE))
            .order_by('id')
        )

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'public, max-age=3600'
        return response

class QuizRound(APIView):
    """Start a round: a seed plus how many questions it holds."""
    def get(self, request, slug):
        total = Neighborhood.objects.filter(city__slug=slug).count()
        if not total:
            return Response({'detail': 'No neighborhoods for this city.'}, status=404)
        return Response({'round': random.randrange(1, MAX_ROUND_SEED), 'total': total})

class QuizQuestion(APIView):
    """The name to find at a given position in a round."""
    def get(self, request, slug):
        seed = read_int(request.query_params, 'round')
        index = read_int(request.query_params, 'index')
        if seed is None or index is None or index < 0:
            return Response({'detail': 'round and index are required integers.'}, status=400)

        order = round_order(slug, seed)
        if not order:
            return Response({'detail': 'No neighborhoods for this city.'}, status=404)
        if index >= len(order):
            return Response({'done': True, 'total': len(order)})
        return Response({
            'target_name': order[index][1],
            'index': index,
            'total': len(order),
        })

class QuizAnswer(APIView):
    """Score a click against the target the server resolves from the round."""
    def post(self, request, slug):
        seed = read_int(request.data, 'round')
        index = read_int(request.data, 'index')
        clicked_id = read_int(request.data, 'clicked_id')
        if seed is None or index is None or index < 0:
            return Response({'detail': 'round and index are required integers.'}, status=400)

        order = round_order(slug, seed)
        if not order:
            return Response({'detail': 'No neighborhoods for this city.'}, status=404)
        if index >= len(order):
            return Response({'detail': 'index is past the end of this round.'}, status=400)

        target_id, target_name = order[index]
        names = dict(order)
        return Response({
            'correct': clicked_id == target_id,
            'correct_id': target_id,
            'correct_name': target_name,
            'clicked_name': names.get(clicked_id),
        })
