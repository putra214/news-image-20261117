#!/usr/bin/env python3
"""Generate 10 small country maps for the v7 top-10 cards.

Source: Natural Earth 110m admin_0_countries (public domain), already downloaded
to ~/workspace/tmp-v7/ne110m_countries.geojson. Bahrain is absent from the
110m file (too small), so it is drawn as a simplified island outline at its
true location.

Each map: equirectangular crop to a bbox with aspect ~3.65 (matches the
190x52 panel), context land in light tan, target country in red, location
dot + ring, country label in a white pill. Output: maps.json with SVG strings.
"""
import json, math

GEO = '/home/hatch/workspace/tmp-v7/ne110m_countries.geojson'
OUT = '/home/hatch/workspace/tmp-v7/maps.json'

data = json.load(open(GEO))
by_admin = {}
for f in data['features']:
    by_admin[f['properties']['ADMIN']] = f['geometry']

# (key, ADMIN name in NE, bbox lon_min, lon_max, lat_min, lat_max,
#  dot (lon, lat), label)
MAPS = [
    ('kerch',   'Ukraine',                    20, 50, 41.0, 49.2, (36.5, 45.3), 'UKRAINE'),
    ('bahrain', None,                         46, 58, 24.2, 27.5, (50.6, 26.2), 'BAHRAIN'),
    ('shenzhen','China',                      74, 136, 18.0, 35.0, (114.1, 22.5), 'CHINA'),
    ('antalya', 'Turkey',                     24, 46, 34.5, 40.5, (30.7, 36.9), 'TURKEY'),
    ('ebola',   'Democratic Republic of the Congo', 6, 57, -13.0, 1.0, (23.7, -2.9), 'DR CONGO'),
    ('dow',     'United States of America',   -130, -55, 22.0, 42.5, (-74.0, 40.7), 'USA'),
    ('dhaka',   'Bangladesh',                 85, 100.3, 20.0, 24.2, (90.4, 23.8), 'BANGLADESH'),
    ('istanbul','Turkey',                     24, 46, 36.0, 42.0, (29.0, 41.0), 'TURKEY'),
    ('akvan',   'India',                      74.5, 100.0, 8.5, 15.5, (88.0, 15.0), 'BAY OF BENGAL'),
    ('aden',    'Yemen',                      38, 58, 11.0, 16.5, (45.0, 12.8), 'YEMEN'),
]

W, H = 190, 52

# Simplified Bahrain island outline (true location, ~50.4-50.65E, 26.0-26.35N).
# The island is tiny at this scale, so it is exaggerated ~2.5x around its
# centre (standard practice for small islands) to stay visible.
_BHR = [(50.42, 26.08), (50.52, 26.02), (50.62, 26.06), (50.65, 26.16),
        (50.60, 26.28), (50.52, 26.34), (50.45, 26.30), (50.40, 26.18)]
_BHC = (50.52, 26.18)
BAHRAIN_POLY = [(_BHC[0] + (lo - _BHC[0]) * 2.5, _BHC[1] + (la - _BHC[1]) * 2.5)
                for lo, la in _BHR]


def project(lon, lat, bbox):
    lon0, lon1, lat0, lat1 = bbox
    x = (lon - lon0) / (lon1 - lon0) * W
    y = (lat1 - lat) / (lat1 - lat0) * H
    return x, y


def ring_coords(coords, bbox):
    """Project a ring of (lon, lat); drop points far outside the panel (with margin)."""
    pts = []
    for lon, lat in coords:
        x, y = project(lon, lat, bbox)
        # clamp to the panel (with a small margin): a cropped map must not
        # contain geometry far outside the viewport
        x = max(-2.0, min(W + 2.0, x))
        y = max(-2.0, min(H + 2.0, y))
        pts.append((x, y))
    return pts


def simplify(pts, tol=0.9):
    """Drop points closer than tol px to the last kept point (keeps file small)."""
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) > tol or abs(p[1] - out[-1][1]) > tol:
            out.append(p)
    if len(out) > 1 and out[0] != out[-1]:
        out.append(out[0])
    return out


def path_from_rings(rings, bbox):
    d = []
    for ring in rings:
        pts = simplify(ring_coords(ring, bbox))
        if len(pts) < 3:
            continue
        d.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z')
    return ' '.join(d)


def geom_rings(geom):
    if geom['type'] == 'Polygon':
        return geom['coordinates']
    if geom['type'] == 'MultiPolygon':
        out = []
        for poly in geom['coordinates']:
            out.extend(poly)
        return out
    return []


def rings_intersect_bbox(rings, bbox):
    lon0, lon1, lat0, lat1 = bbox
    for ring in rings:
        for lon, lat in ring:
            if lon0 - 2 <= lon <= lon1 + 2 and lat0 - 2 <= lat <= lat1 + 2:
                return True
    return False


result = {}
for key, admin, lon0, lon1, lat0, lat1, dot, label in MAPS:
    bbox = (lon0, lon1, lat0, lat1)
    parts = [f'<rect width="{W}" height="{H}" fill="#dfe9f2"/>']
    # context land: every country touching the bbox, light tan
    for name, geom in by_admin.items():
        rings = geom_rings(geom)
        if not rings_intersect_bbox(rings, bbox):
            continue
        d = path_from_rings(rings, bbox)
        if d:
            parts.append(f'<path d="{d}" fill="#cfc8b8"/>')
    # target country highlight
    if admin is None:  # Bahrain: manual island outline
        pts = simplify(ring_coords(BAHRAIN_POLY, bbox), 0.4)
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'
        parts.append(f'<path d="{d}" fill="#c0392b" stroke="#7a1f14" stroke-width="0.8"/>')
    else:
        d = path_from_rings(geom_rings(by_admin[admin]), bbox)
        parts.append(f'<path d="{d}" fill="#c0392b" stroke="#7a1f14" stroke-width="0.8"/>')
    # location dot + ring
    dx, dy = project(dot[0], dot[1], bbox)
    parts.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="4.6" fill="none" stroke="#16130f" stroke-width="1.3"/>')
    parts.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="2.3" fill="#c0392b" stroke="#fff" stroke-width="0.9"/>')
    # label pill (top-left)
    lw = 6 + len(label) * 5.4
    parts.append(f'<rect x="3" y="3" width="{lw:.0f}" height="10" rx="2" fill="#fff" opacity="0.88"/>')
    parts.append(f'<text x="6" y="10.5" font-family="Liberation Sans, DejaVu Sans, sans-serif" font-size="7" font-weight="bold" letter-spacing="0.6" fill="#2b2823">{label}</text>')
    svg = ('<svg viewBox="0 0 190 52" preserveAspectRatio="none" '
           f'aria-label="Map of {label}, location marked">{"".join(parts)}</svg>')
    result[key] = svg
    print(f'{key}: dot at ({dx:.1f},{dy:.1f}) label {label} svg {len(svg)} bytes')

json.dump(result, open(OUT, 'w'), ensure_ascii=False)
print('wrote', OUT)
