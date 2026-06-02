import json

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.management.base import BaseCommand, CommandError

from quizzes.models import City, Neighborhood


class Command(BaseCommand):
    help = "Load neighborhood polygons from a GeoJSON file and attach them to a City."

    def add_arguments(self, parser):
        parser.add_argument('geojson_path', help='Path to the neighborhood GeoJSON file.')
        parser.add_argument('--city', default='san-diego', help='Slug of the City to attach to.')
        parser.add_argument('--name-field', default='name',
                            help='Feature property holding the neighborhood name.')
        parser.add_argument('--replace', action='store_true',
                            help="Delete the city's existing neighborhoods first.")

    def handle(self, *args, **opts):
        try:
            city = City.objects.get(slug=opts['city'])
        except City.DoesNotExist:
            raise CommandError(f"City with slug '{opts['city']}' not found.")

        with open(opts['geojson_path']) as f:
            data = json.load(f)

        features = data.get('features', [])
        if not features:
            raise CommandError('GeoJSON has no features.')

        if opts['replace']:
            deleted, _ = city.neighborhoods.all().delete()
            self.stdout.write(f'Removed {deleted} existing neighborhood(s).')

        name_field = opts['name_field']
        created = skipped = 0
        for feature in features:
            props = feature.get('properties', {})
            name = props.get(name_field)
            if not name:
                skipped += 1
                continue
            name = ' '.join(name.split())
            if 'not a community plan' in name.lower():  # source placeholder rows
                skipped += 1
                continue
            if name.isupper():  # ALL-CAPS source names -> Title Case for display
                name = name.title()

            geom = GEOSGeometry(json.dumps(feature['geometry']), srid=4326)
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            elif geom.geom_type != 'MultiPolygon':
                skipped += 1
                continue

            Neighborhood.objects.update_or_create(
                city=city, name=name.strip(), defaults={'geometry': geom},
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Loaded {created} neighborhood(s) for {city.name} (skipped {skipped}).'
        ))
