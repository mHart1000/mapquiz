import json
import re
from collections import OrderedDict

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.core.management.base import BaseCommand, CommandError

from quizzes.models import City, Neighborhood

ROMAN = re.compile(r'^[IVXLCDM]+$')
VOWELS = set('AEIOUY')


def title_token(token):
    if ROMAN.match(token) or not (set(token) & VOWELS):
        return token
    return token.title()


def normalize_name(raw, strip_prefixes=()):
    name = ' '.join(raw.split())
    for prefix in strip_prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
            break
    if name.isupper():
        name = ' '.join(title_token(t) for t in name.split(' '))
    return name


def shared_prefixes(raw_names):
    """Colon-delimited groupings the source uses on more than one feature."""
    counts = {}
    for raw in raw_names:
        head, sep, tail = raw.partition(':')
        if sep and tail.strip():
            counts[head + ':'] = counts.get(head + ':', 0) + 1
    return {p for p, n in counts.items() if n > 1}


def detect_name_field(features):
    """Pick the property that best behaves like a display name."""
    best, best_score = None, 0.0
    for key in features[0].get('properties', {}):
        values = [f.get('properties', {}).get(key) for f in features]
        strings = [v.strip() for v in values if isinstance(v, str) and v.strip()]
        if len(strings) < 0.8 * len(features):
            continue
        if sum(s.lower().startswith('http') for s in strings) > 0.5 * len(strings):
            continue
        score = len(set(strings)) / len(strings)
        if 'name' in key.lower():
            score += 0.5
        if score > best_score:
            best, best_score = key, score
    return best


class Command(BaseCommand):
    help = "Load neighborhood polygons from a GeoJSON file and attach them to a City."

    def add_arguments(self, parser):
        parser.add_argument('geojson_path', help='Path to the neighborhood GeoJSON file.')
        parser.add_argument('--city', default='san-diego', help='Slug of the City to attach to.')
        parser.add_argument('--name-field', default=None,
                            help='Feature property holding the name. Auto-detected when omitted.')
        parser.add_argument('--skip-name', action='append', default=[], metavar='NAME',
                            help='Source name to drop entirely. Repeatable.')
        parser.add_argument('--rename', action='append', default=[], metavar='OLD=NEW',
                            help='Override the display name for a source name. Repeatable.')
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

        name_field = opts['name_field'] or detect_name_field(features)
        if not name_field:
            raise CommandError(
                'Could not detect a name property; pass --name-field explicitly. '
                f'Available: {", ".join(features[0].get("properties", {}))}'
            )
        if not opts['name_field']:
            self.stdout.write(f"Using '{name_field}' as the name property.")

        renames = {}
        for pair in opts['rename']:
            old, sep, new = pair.partition('=')
            if not sep:
                raise CommandError(f'--rename expects OLD=NEW, got {pair!r}')
            renames[old.strip()] = new.strip()

        skips = {s.strip() for s in opts['skip_name']}
        raw_names = [
            ' '.join(f.get('properties', {})[name_field].split())
            for f in features
            if isinstance(f.get('properties', {}).get(name_field), str)
        ]
        prefixes = shared_prefixes(raw_names)

        # Same-named features are parts of one place (rivers, freeways split them),
        # so collect every piece before writing a single multi-part shape.
        pieces = OrderedDict()
        skipped = unnamed = 0
        for feature in features:
            raw = feature.get('properties', {}).get(name_field)
            if not isinstance(raw, str) or not raw.strip():
                unnamed += 1
                continue
            raw = ' '.join(raw.split())
            if raw in skips:
                skipped += 1
                continue

            geom = GEOSGeometry(json.dumps(feature['geometry']), srid=4326)
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            elif geom.geom_type != 'MultiPolygon':
                skipped += 1
                continue

            name = renames.get(raw) or normalize_name(raw, prefixes)
            pieces.setdefault(name, []).append(geom)

        if not pieces:
            raise CommandError(
                f"No features had a usable '{name_field}' value — nothing was loaded."
            )

        if opts['replace']:
            deleted, _ = city.neighborhoods.all().delete()
            self.stdout.write(f'Removed {deleted} existing neighborhood(s).')

        merged = 0
        for name, geoms in pieces.items():
            geom = geoms[0]
            for extra in geoms[1:]:
                geom = geom.union(extra)
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            if len(geoms) > 1:
                merged += 1
            Neighborhood.objects.update_or_create(
                city=city, name=name, defaults={'geometry': geom},
            )

        for unused in skips.difference(raw_names):
            self.stderr.write(self.style.WARNING(f'--skip-name {unused!r} matched nothing.'))
        for unused in set(renames).difference(raw_names):
            self.stderr.write(self.style.WARNING(f'--rename {unused!r} matched nothing.'))

        self.stdout.write(self.style.SUCCESS(
            f'Loaded {len(pieces)} neighborhood(s) for {city.name} '
            f'from {len(features)} feature(s) — {merged} merged, '
            f'{skipped} skipped, {unnamed} unnamed.'
        ))
