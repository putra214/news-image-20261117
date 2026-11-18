#!/usr/bin/env python3
"""Build news-image v11 from v10 page.html — 30 -> 36 stories.

Restores the 6 stories cut in v8 as ALSO ON one-liners (27-32):
  27 Bond (Pattinson named the next James Bond) — London
  28 Royals (William e-rickshaw ride in Mumbai) — Mumbai
  29 NSA (network degraded in maintenance) — Fort Meade
  30 UN (Turk warns on Rwanda plan risks) — Geneva
  31 Environment (chemicals reach the unborn) — Nairobi/UNEP
  32 Yemen (Saudis replace commander) — Riyadh
FENOMENA 27-30 -> 33-36; banner "30 STORIES" -> "36 STORIES";
world map 29 -> 35 markers (Voyager #25 still has no point).
All facts from NEWS.md; no new stories.

Layout budget (v10 measured: bottom 859-986, footer 989-1016, scroll 1024):
  ALSO ON grows 4 -> 7 items/column, so icons shrink 20->16px, item
  margin 4->2px, font 11->10.5px (item 24px -> 18px; alsocol ~144px).
  The +17px is paid back by small trims above (sec margins, MORE/FEN
  band heights, bottom + footer gaps) so the footer still ends ~1016.
"""
import json, re

TMP11 = '/home/hatch/workspace/tmp-v11'
WORK = '/home/hatch/workspace/custom-connectors/custom.makefun/news-image-20261117/work'
SRC = WORK + '/page.html'
OUT = WORK + '/page.html'

MARKERS = json.load(open(TMP11 + '/markers.json'))['svg']

html = open(SRC, encoding='utf-8').read()
assert '30 STORIES' in html

# ---------------------------------------------------------------- CSS (in place)
css_edits = [
    # sections: shave 1px margin + 1px padding each (3 sections = 6px)
    ("  .sec { position: relative; border-top: 2px solid #16130f; margin-top: 4px; padding-top: 5px; }",
     "  .sec { position: relative; border-top: 2px solid #16130f; margin-top: 3px; padding-top: 3px; }"),
    # top-10: shave 2px off illustration + country map (invisible, 4px)
    ("  .topcard .band svg { height: 96px; }",
     "  .topcard .band svg { height: 94px; }"),
    ("  .topcard .cmap svg { display: block; width: 100%; height: 46px; border: 1px solid #b9b2a2; box-shadow: 0 1px 2px rgba(0,0,0,.2); }",
     "  .topcard .cmap svg { display: block; width: 100%; height: 44px; border: 1px solid #b9b2a2; box-shadow: 0 1px 2px rgba(0,0,0,.2); }"),
    # MORE: slightly shorter art strip + tighter row gap (3px)
    ("  .moregrid .card .band svg { height: 32px; }",
     "  .moregrid .card .band svg { height: 28px; }"),
    ("  .moregrid { display: grid; grid-template-columns: repeat(4, 1fr); column-gap: 14px; row-gap: 6px; }",
     "  .moregrid { display: grid; grid-template-columns: repeat(4, 1fr); column-gap: 14px; row-gap: 4px; }"),
    # FENOMENA: slightly shorter art strip (2px)
    ("  .fenpanel .band svg { height: 34px; }",
     "  .fenpanel .band svg { height: 30px; }"),
    # bottom: tighter top margin/padding (4px)
    ("  .bottom { display: flex; gap: 14px; margin-top: 6px; border-top: 2px solid #16130f; padding-top: 5px; }",
     "  .bottom { display: flex; gap: 14px; margin-top: 3px; border-top: 2px solid #16130f; padding-top: 4px; }"),
    # ALSO ON items: smaller icons + tighter rows so 7/column fit
    ("  .alsocol .item { display: flex; gap: 6px; margin-bottom: 4px; align-items: flex-start; }",
     "  .alsocol .item { display: flex; gap: 6px; margin-bottom: 1px; align-items: flex-start; }"),
    ("  .alsocol .item p { font-size: 11px; line-height: 1.2; }",
     "  .alsocol .item p { font-size: 10.5px; line-height: 1.2; }"),
    ("  .alsocol .item svg { flex: none; width: 20px; height: 20px; border: 1px solid #b9b2a2; background: #efe8d6; }",
     "  .alsocol .item svg { flex: none; width: 16px; height: 16px; border: 1px solid #b9b2a2; background: #efe8d6; }"),
    ("  .bottom h3.sec2 { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 13px; font-weight: bold; letter-spacing: 2px; margin-bottom: 3px; }",
     "  .bottom h3.sec2 { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 13px; font-weight: bold; letter-spacing: 2px; margin-bottom: 2px; }"),
    # footer: 2px tighter
    ("  .footer { margin-top: 3px; border-top: 1px solid #a89e8c; padding-top: 2px; font-size: 11px; color: #4a443c; text-align: center; }",
     "  .footer { margin-top: 2px; border-top: 1px solid #a89e8c; padding-top: 1px; font-size: 11px; color: #4a443c; text-align: center; }"),
]
for old, new in css_edits:
    assert old in html, 'CSS not found: ' + old[:70]
    html = html.replace(old, new, 1)
print('css edits:', len(css_edits))

# banner count
html = html.replace('30 STORIES', '36 STORIES', 1)

# ---------------------------------------------------------------- helpers
def badge_of(block):
    m = re.search(r'<span class="num"[^>]*>(\d+)</span>', block)
    return int(m.group(1)) if m else None

def renum_badge(block, new_n):
    return re.sub(r'(<span class="num"[^>]*>)\d+(</span>)',
                  lambda m: m.group(1) + str(new_n) + m.group(2), block, count=1)

def h4_of(block):
    m = re.search(r'<h4>(.*?)</h4>', block, re.S)
    return m.group(1) if m else ''

def find_cards(region, cls):
    out = []
    pat = '<div class="' + cls + '"'
    pos = 0
    while True:
        s = region.find(pat, pos)
        if s < 0:
            break
        depth = 0
        i = s
        while True:
            o = region.find('<div', i)
            c = region.find('</div>', i)
            if c < 0:
                raise SystemExit('unbalanced div in ' + cls)
            if o >= 0 and o < c:
                depth += 1
                i = o + 4
            else:
                depth -= 1
                i = c + 6
                if depth == 0:
                    out.append(region[s:i])
                    break
        pos = i
    return out

# ---------------------------------------------------------------- FENOMENA 27-30 -> 33-36
fi = html.index('<!-- FENOMENA -->')
fj = html.index('<!-- BOTTOM: MAP + ALSO ON -->', fi)
fen_region = html[fi:fj]
assert '&middot; 27&ndash;30' in fen_region
fen_region = fen_region.replace('&middot; 27&ndash;30', '&middot; 33&ndash;36', 1)
fens = find_cards(fen_region, 'fenpanel')
assert len(fens) == 4, len(fens)
fen_new = {}
for f in fens:
    h = h4_of(f)
    if 'Leonid' in h:
        fen_new[33] = renum_badge(f, 33)
    elif 'Aurora' in h:
        fen_new[34] = renum_badge(f, 34)
    elif 'Eruption' in h or 'hectares' in h:
        fen_new[35] = renum_badge(f, 35)
    elif 'quak' in h.lower():
        fen_new[36] = renum_badge(f, 36)
    else:
        raise SystemExit('unknown fen panel: ' + h)
assert sorted(fen_new) == [33, 34, 35, 36]
for n, block in fen_new.items():
    old = [f for f in fens if badge_of(f) == n - 6][0]
    fen_region = fen_region.replace(old, block, 1)
html = html[:fi] + fen_region + html[fj:]
print('fenomena renumbered 27-30 -> 33-36')

# ---------------------------------------------------------------- bottom: world map markers
mi = html.index('<svg viewBox="0 6 440 160"')
mj = html.index('</svg>', mi)
msvg = html[mi:mj]
gi = msvg.index('<g font-family="Liberation Sans, DejaVu Sans, sans-serif" font-size="7.5"')
new_msvg = msvg[:gi] + MARKERS + '\n'
html = html[:mi] + new_msvg + html[mj:]
print('map markers replaced (35 badges)')

# ---------------------------------------------------------------- ALSO ON 19-26 -> 19-32
ai = html.index('<div class="alsocol">')
aj = html.index('<!-- FOOTER -->', ai)
als = html[ai:aj]
assert '&middot; 19&ndash;26' in als
als = als.replace('&middot; 19&ndash;26', '&middot; 19&ndash;32', 1)
items = re.findall(r'          <div class="item">.*?</div>', als, re.S)
assert len(items) == 8, len(items)
kept = {}
for it in items:
    n = badge_of(it)
    kept[n] = it
assert sorted(kept) == list(range(19, 27)), sorted(kept)

def item(n, color, icon_svg, label, text):
    return (f'          <div class="item"><span class="num" style="background:{color}">{n}</span>'
            f'{icon_svg}<p><b>{label}:</b> {text}</p></div>')

ICONS = {
    'bond': ('<svg viewBox="0 0 20 20" aria-label="The number 007 on a dark card">'
             '<rect width="20" height="20" fill="#16130f"/>'
             '<text x="10" y="14" text-anchor="middle" font-family="Liberation Sans, DejaVu Sans, sans-serif" '
             'font-size="8" font-weight="bold" fill="#c9a227">007</text></svg>'),
    'crown': ('<svg viewBox="0 0 20 20" aria-label="A gold crown">'
              '<rect width="20" height="20" fill="#eef0ea"/>'
              '<polygon points="3,15 3,7 7,10.5 10,4 13,10.5 17,7 17,15" fill="#c9a227" stroke="#7a6a4f" stroke-width="0.8"/>'
              '<rect x="3" y="15" width="14" height="2" fill="#7a6a4f"/></svg>'),
    'shield': ('<svg viewBox="0 0 20 20" aria-label="A blue shield with a keyhole">'
               '<rect width="20" height="20" fill="#eef0ea"/>'
               '<path d="M10,2 L16,4.5 V10 C16,14 13.5,17 10,18 C6.5,17 4,14 4,10 V4.5 Z" fill="#2b5ea7"/>'
               '<circle cx="10" cy="9" r="2" fill="#fff"/><rect x="9.2" y="9" width="1.6" height="4" fill="#fff"/></svg>'),
    'globe': ('<svg viewBox="0 0 20 20" aria-label="A blue globe">'
              '<rect width="20" height="20" fill="#2b5ea7"/>'
              '<circle cx="10" cy="10" r="7" fill="none" stroke="#fff" stroke-width="1.2"/>'
              '<ellipse cx="10" cy="10" rx="3" ry="7" fill="none" stroke="#fff" stroke-width="0.8"/>'
              '<line x1="3" y1="10" x2="17" y2="10" stroke="#fff" stroke-width="0.8"/></svg>'),
    'leaf': ('<svg viewBox="0 0 20 20" aria-label="A green leaf">'
             '<rect width="20" height="20" fill="#eef0ea"/>'
             '<path d="M16,4 C8,4 4,9 4,15 C10,15 16,11 16,4 Z" fill="#2e8b57"/>'
             '<line x1="6.5" y1="14.5" x2="14" y2="7" stroke="#fff" stroke-width="1"/></svg>'),
    'chevron': ('<svg viewBox="0 0 20 20" aria-label="Two orange chevrons">'
                '<rect width="20" height="20" fill="#eef0ea"/>'
                '<polygon points="4,4 10,9 16,4 16,8 10,13 4,8" fill="#d07a1f"/>'
                '<polygon points="4,11 10,16 16,11 16,14 10,18 4,14" fill="#d07a1f" opacity=".75"/></svg>'),
}

kept[27] = item(27, '#2b5ea7', ICONS['bond'], 'Bond',
                'Pattinson named the next James Bond.')
kept[28] = item(28, '#c0392b', ICONS['crown'], 'Royals',
                "William&rsquo;s e-rickshaw ride in Mumbai.")
kept[29] = item(29, '#7d4fa3', ICONS['shield'], 'NSA',
                'network degraded in maintenance.')
kept[30] = item(30, '#2b5ea7', ICONS['globe'], 'UN',
                'T&uuml;rk warns on Rwanda plan risks.')
kept[31] = item(31, '#2e8b57', ICONS['leaf'], 'Environment',
                'chemicals reach the unborn.')
kept[32] = item(32, '#d07a1f', ICONS['chevron'], 'Yemen',
                'Saudis replace commander.')

cols_html = ('      <div class="cols">\n        <div class="col">\n' +
             '\n'.join(kept[n] for n in (19, 20, 21, 22, 27, 28, 29)) +
             '\n        </div>\n        <div class="col">\n' +
             '\n'.join(kept[n] for n in (23, 24, 25, 26, 30, 31, 32)) +
             '\n        </div>\n      </div>')
ci = als.index('      <div class="cols">')
cj = als.index('    </div>\n  </div>', ci)
als = als[:ci] + cols_html + '\n' + als[cj:]
html = html[:ai] + als + html[aj:]

open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, len(html), 'bytes')

# ---------------------------------------------------------------- verification: numbering
badges = [int(x) for x in re.findall(r'<span class="num"[^>]*>(\d+)</span>', html)]
print('body badges:', sorted(badges) == list(range(1, 37)), 'count', len(badges),
      'missing', sorted(set(range(1, 37)) - set(badges)))
map_badges = [int(x) for x in re.findall(r'<text x="[\d.]+" y="[\d.]+" fill="#fff">(\d+)</text>', html)]
print('map badges:', sorted(map_badges), 'count', len(map_badges))
