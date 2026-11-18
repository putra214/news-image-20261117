#!/usr/bin/env python3
"""Recompute world-map numbered markers for v8 (30 stories) from TRUE lat/lon.

Same equirectangular projection as the dot map (viewBox 0 6 440 160):
    x = (lon + 180) * 440 / 360
    y = (90 - lat) * 160 / 180
Collision handling identical to gen_markers.py (v7): badges r=6, min
distance 13 px, pushed minimally with leader line + dot at the true point.

v8 numbering: 1-10 top 10 (same as v7), 11-18 MORE, 19-26 ALSO ON,
27-30 FENOMENA. Voyager 1 is #25 (no point, space). Leonid is #27 and
keeps the old grey "global" spot (206, 12).
Output: /home/hatch/workspace/tmp-v8/markers.json {svg, report}.
"""
import json, math

# new number -> (lat, lon, region colour, name)
STORIES = {
    1:  (45.3, 36.5, '#2b5ea7', 'Kerch'),
    2:  (26.2, 50.6, '#d07a1f', 'Bahrain'),
    3:  (22.5, 114.1, '#c0392b', 'Shenzhen'),
    4:  (36.9, 30.7, '#2b5ea7', 'Antalya'),
    5:  (-2.9, 23.7, '#2e8b57', 'DR Congo'),
    6:  (40.7, -74.0, '#7d4fa3', 'New York'),
    7:  (23.8, 90.4, '#c0392b', 'Dhaka'),
    8:  (41.0, 29.0, '#2b5ea7', 'Istanbul'),
    9:  (15.0, 88.0, '#c0392b', 'Bay of Bengal'),
    10: (12.8, 45.0, '#d07a1f', 'Aden'),
    11: (-1.9, 29.9, '#2e8b57', 'Kigali'),
    12: (1.35, 103.8, '#c0392b', 'Singapore'),
    13: (35.7, 139.7, '#c0392b', 'Tokyo'),
    14: (51.5, -0.1, '#2b5ea7', 'London'),
    15: (38.9, -77.0, '#7d4fa3', 'Pentagon/DC'),
    16: (38.9, -77.0, '#7d4fa3', 'White House/DC'),
    17: (33.75, -84.4, '#7d4fa3', 'Atlanta/CDC'),
    18: (47.9, 106.9, '#c0392b', 'Ulaanbaatar'),
    19: (25.3, 51.5, '#d07a1f', 'Doha'),
    20: (40.7, -74.0, '#7d4fa3', 'New York/JPMorgan'),
    21: (47.5, 19.0, '#2b5ea7', 'Budapest'),
    22: (31.5, 34.5, '#d07a1f', 'Gaza'),
    23: (26.5, 56.5, '#d07a1f', 'Strait of Hormuz'),
    24: (55.4, 86.1, '#c0392b', 'Kemerovo'),
    # 25 Voyager: no point (space)
    26: (-22.9, -43.2, '#7d4fa3', 'Rio de Janeiro'),
    # 27 Leonid: fixed global spot, see below
    28: (60.0, -120.0, '#7d4fa3', 'Aurora/N Canada'),
    29: (24.8, 141.3, '#c0392b', 'Ioto'),
    30: (-42.9, 171.6, '#2a9d8f', "Arthur's Pass NZ"),
}
LEONID_SPOT = (206.0, 12.0)

MIN_DIST = 13.0


def proj(lat, lon):
    return (lon + 180) * 440 / 360, (90 - lat) * 160 / 180


placed = {}
true_pos = {}
report = []

for n in sorted(STORIES):
    lat, lon, col, name = STORIES[n]
    tx, ty = proj(lat, lon)
    true_pos[n] = (tx, ty)
    x, y = tx, ty
    for _ in range(40):
        clash = None
        for m, (px, py) in placed.items():
            d = math.hypot(x - px, y - py)
            if d < MIN_DIST:
                clash = (m, px, py, d)
                break
        if not clash:
            break
        m, px, py, d = clash
        dx, dy = x - px, y - py
        if d < 0.01:
            dx, dy = 1.0, 0.3
        L = math.hypot(dx, dy)
        push = MIN_DIST - d + 0.6
        x += dx / L * push
        y += dy / L * push
        x = min(max(x, 8), 432)
        y = min(max(y, 12), 158)
    placed[n] = (x, y)
    moved = math.hypot(x - tx, y - ty)
    report.append({'n': n, 'name': name, 'lat': lat, 'lon': lon,
                   'true': [round(tx, 1), round(ty, 1)],
                   'badge': [round(x, 1), round(y, 1)],
                   'moved': round(moved, 1)})
    print(f'#{n:2d} {name:22s} true ({tx:6.1f},{ty:5.1f}) badge ({x:6.1f},{y:5.1f})'
          + (f'  MOVED {moved:.1f}px -> leader line' if moved > 0.5 else ''))

placed[27] = LEONID_SPOT
report.append({'n': 27, 'name': 'Leonid (global)', 'lat': None, 'lon': None,
               'true': None, 'badge': [206.0, 12.0], 'moved': 0})

lines, dots, badges = [], [], []
for n in sorted(placed):
    x, y = placed[n]
    col = '#55524a' if n == 27 else STORIES[n][2]
    tx, ty = true_pos.get(n, (x, y))
    if math.hypot(x - tx, y - ty) > 0.5:
        lines.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="#4a443c" stroke-width="1"/>')
        dots.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="2.2" fill="{col}" stroke="#fff" stroke-width="0.7"/>')
    badges.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{col}" stroke="#fff" stroke-width="1.2"/>'
        f'<text x="{x:.1f}" y="{y + 2.6:.1f}" fill="#fff">{n}</text>')

svg = ('<g font-family="Liberation Sans, DejaVu Sans, sans-serif" font-size="7.5" '
       'font-weight="bold" fill="#fff" text-anchor="middle">\n'
       '<g stroke="#4a443c" stroke-width="1" opacity=".8" fill="none">\n' +
       '\n'.join(lines) + '\n</g>\n' +
       '\n'.join(dots) + '\n<g>\n' + '\n'.join(badges) + '\n</g>\n</g>')
json.dump({'svg': svg, 'report': report}, open('/home/hatch/workspace/tmp-v8/markers.json', 'w'))
print('\nwrote markers.json; leader lines:', len(lines),
      '; badges exactly on true point:', sum(1 for r in report if r['moved'] <= 0.5))
