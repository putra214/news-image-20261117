#!/usr/bin/env python3
"""Build news-image v8 from v7 page.html — LESS DENSE, more air.

v8 layout (1024x1024), 30 stories (was 36):
  banner "30 STORIES" (unchanged masthead)
  10 BERITA TERBESAR — 5x2 grid, illustration 84->100px, country map 52->46px,
      bigger fonts, trimmed 1-2 line bodies, wider gaps
  MORE STORIES 11-18 — 8 cards in a 4x2 grid (was 6x2 of 12), wider cards,
      taller panels, bigger fonts
  FENOMENA 27-30 — 4 panels (Leonid, Aurora, Ioto, NZ quake)
  BOTTOM: world map with TRUE-coordinate markers (renumbered 1-30, Voyager #25
      has no point) + ALSO ON 19-26 (8 one-liners, incl. Voyager + Brazil)
  footer (unchanged)
Dropped: Pattinson/Bond (19), William rickshaw (21), NSA (25), UN Turk (28),
Environment (29), Yemen-Saudis (30). All facts from NEWS.md; no new stories.
"""
import json, re

TMP7 = '/home/hatch/workspace/tmp-v7'
TMP8 = '/home/hatch/workspace/tmp-v8'
WORK = '/home/hatch/workspace/custom-connectors/custom.makefun/news-image-20261117/work'
SRC = WORK + '/page.html'
OUT = WORK + '/page.html'

MAPS = json.load(open(TMP7 + '/maps.json'))
MARKERS = json.load(open(TMP8 + '/markers.json'))['svg']

# Reuse v7's illustration art + top-10 data (exec only those two literals).
v7 = open(TMP7 + '/v7_build.py', encoding='utf-8').read()
ns = {}
exec(v7[v7.index('ART = {}'):v7.index('# (num, color')], ns)
ART = ns['ART']
t0 = v7.index('TOP10 = [')
exec(v7[t0:v7.index(']\n', t0) + 1], ns)
TOP10 = ns['TOP10']
assert len(ART) == 10 and len(TOP10) == 10

# Trimmed bodies (shorter, 1-2 lines at 9.5px in a ~183px card).
TRIM = {
    1: 'A road span fell into the sea after drones and missiles struck overnight.',
    2: 'Third attack in days; Bahrain intercepted it; US jets hit Qeshm.',
    3: 'First three-way meeting, set for Thursday at APEC.',
    4: 'Draft in Antalya divides on fossil fuels and $120bn adaptation cash.',
    5: 'WHO counts 11,000+ cases and about 5,400 deaths in three months.',
    6: 'Wall Street falls a fourth day; Nvidia revenue $115.8bn.',
    7: 'Thousands protest a postponed wage meeting; 500 factories shut.',
    8: 'Pre-dawn raid in Istanbul; state trustee takes over the channel.',
    9: '610 km east of Chennai; landfall 20 Nov, winds 120&ndash;130 km/h.',
    10: 'Government forces pull back; rebels about 60 km from Aden.',
}
TOP10 = [(n, c, k, h, TRIM[n], a, m) for (n, c, k, h, p, a, m) in TOP10]

html = open(SRC, encoding='utf-8').read()

# ---------------------------------------------------------------- CSS (in place)
css_edits = [
    # sections: more breathing room between sections
    ("  .sec { position: relative; border-top: 2px solid #16130f; margin-top: 4px; padding-top: 5px; }",
     "  .sec { position: relative; border-top: 2px solid #16130f; margin-top: 6px; padding-top: 6px; }"),
    # top-10: taller illustration, slightly shorter country map, bigger type
    ("  .top10grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; row-gap: 8px; }",
     "  .top10grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; row-gap: 10px; }"),
    ("  .topcard { border-top: 2px solid #c9c0ad; padding-top: 3px; }",
     "  .topcard { border-top: 2px solid #c9c0ad; padding-top: 5px; }"),
    ("  .topcard .band svg { height: 84px; }",
     "  .topcard .band svg { height: 96px; }"),
    ("  .topcard .cmap svg { display: block; width: 100%; height: 52px; border: 1px solid #b9b2a2; box-shadow: 0 1px 2px rgba(0,0,0,.2); }",
     "  .topcard .cmap svg { display: block; width: 100%; height: 46px; border: 1px solid #b9b2a2; box-shadow: 0 1px 2px rgba(0,0,0,.2); }"),
    ("  .topcard .bk { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 10px; font-weight: bold; letter-spacing: 1.1px; margin-top: 3px; }",
     "  .topcard .bk { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 10.5px; font-weight: bold; letter-spacing: 1.1px; margin-top: 3px; }"),
    ("  .topcard h4 { font-size: 12px; line-height: 1.08; font-weight: bold; margin: 1px 0 1px; }",
     "  .topcard h4 { font-size: 13px; line-height: 1.08; font-weight: bold; margin: 1px 0 1px; }"),
    ("  .topcard p { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 9px; line-height: 1.2; color: #2b2823; }",
     "  .topcard p { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 9.5px; line-height: 1.25; color: #2b2823; }"),
    # more stories: 4 columns, wider cards, taller panels, bigger type
    ("  .moregrid { display: grid; grid-template-columns: repeat(6, 1fr); column-gap: 10px; row-gap: 5px; }",
     "  .moregrid { display: grid; grid-template-columns: repeat(4, 1fr); column-gap: 14px; row-gap: 8px; }"),
    ("  .moregrid .card .band svg { height: 30px; }",
     "  .moregrid .card .band svg { height: 32px; }"),
    ("  .moregrid .card h4 { font-size: 11px; }",
     "  .moregrid .card h4 { font-size: 12.5px; }"),
    ("  .moregrid .card p { font-size: 8.5px; line-height: 1.2; }",
     "  .moregrid .card p { font-size: 9.5px; line-height: 1.25; }"),
    # fenomena: wider gaps, slightly taller panels
    ("  .fengrid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }",
     "  .fengrid4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }"),
    ("  .fenpanel .band svg { height: 32px; }",
     "  .fenpanel .band svg { height: 34px; }"),
    ("  .fenpanel h4 { font-size: 12px; line-height: 1.1; font-weight: bold; margin: 1px 0 1px; }",
     "  .fenpanel h4 { font-size: 13px; line-height: 1.1; font-weight: bold; margin: 1px 0 1px; }"),
    ("  .fenpanel p { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 9.5px; line-height: 1.22; color: #2b2823; }",
     "  .fenpanel p { font-family: 'Liberation Sans', 'DejaVu Sans', Arial, sans-serif; font-size: 10px; line-height: 1.25; color: #2b2823; }"),
    # bottom + footer: a little more air
    ("  .bottom { display: flex; gap: 14px; margin-top: 4px; border-top: 2px solid #16130f; padding-top: 4px; }",
     "  .bottom { display: flex; gap: 14px; margin-top: 8px; border-top: 2px solid #16130f; padding-top: 6px; }"),
    ("  .mapcol svg { display: block; width: 400px; height: 94px; background: #e2eaf0; border: 1px solid #b9b2a2; box-shadow: 0 1px 2px rgba(0,0,0,.18); }",
     "  .mapcol svg { display: block; width: 400px; height: 88px; background: #e2eaf0; border: 1px solid #b9b2a2; box-shadow: 0 1px 2px rgba(0,0,0,.18); }"),
    ("  .alsocol .item { display: flex; gap: 6px; margin-bottom: 3px; align-items: flex-start; }",
     "  .alsocol .item { display: flex; gap: 6px; margin-bottom: 4px; align-items: flex-start; }"),
    ("  .alsocol .item p { font-size: 10.5px; line-height: 1.2; }",
     "  .alsocol .item p { font-size: 11px; line-height: 1.2; }"),
    ("  .footer { margin-top: 2px; border-top: 1px solid #a89e8c; padding-top: 2px; font-size: 11px; color: #4a443c; text-align: center; }",
     "  .footer { margin-top: 4px; border-top: 1px solid #a89e8c; padding-top: 2px; font-size: 11px; color: #4a443c; text-align: center; }"),
]
for old, new in css_edits:
    assert old in html, 'CSS not found: ' + old[:70]
    html = html.replace(old, new, 1)
print('css edits:', len(css_edits))

# banner count
assert '36 STORIES' in html
html = html.replace('36 STORIES', '30 STORIES', 1)

# ---------------------------------------------------------------- helpers
def section(html, start_marker, end_marker):
    i = html.index(start_marker)
    j = html.index(end_marker, i)
    return html[i:j]

def find_cards(region, cls, indent):
    # depth-counting extractor: robust to mixed indent (Voyager card's close
    # sits at 6 spaces, regular cards at 4). Returns each block verbatim.
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

def h4_of(block):
    m = re.search(r'<h4>(.*?)</h4>', block, re.S)
    return m.group(1) if m else ''

def badge_of(block):
    m = re.search(r'<span class="num"[^>]*>(\d+)</span>', block)
    return int(m.group(1)) if m else None

def renum_badge(block, new_n):
    return re.sub(r'(<span class="num"[^>]*>)\d+(</span>)',
                  lambda m: m.group(1) + str(new_n) + m.group(2), block, count=1)

# ---------------------------------------------------------------- top 10 (regenerated, trimmed bodies)
def topcard(t):
    n, col, bk, h, p, art, mkey = t
    return ('      <div class="topcard" style="border-top-color:' + col + '">\n'
            '        <div class="band">' + ART[art] + '<span class="num" style="background:' + col + '">' + str(n) + '</span></div>\n'
            '        <div class="cmap">' + MAPS[mkey] + '</div>\n'
            '        <div class="bk" style="color:' + col + '">' + bk + '</div><h4>' + h + '</h4><p>' + p + '</p>\n'
            '      </div>')

top10_html = ('<!-- 10 BERITA TERBESAR -->\n  <div class="sec">\n'
              '    <div class="tag">10 BERITA TERBESAR <span>&middot; 1&ndash;10</span></div>\n'
              '    <div class="top10grid">\n' +
              '\n'.join(topcard(t) for t in TOP10) +
              '\n    </div>\n  </div>\n')

# ---------------------------------------------------------------- MORE STORIES 11-18 (keep 8 of v7's 12)
cards = find_cards(section(html, '<!-- MORE STORIES 11-22 -->', '<!-- FENOMENA -->'), 'card', '    ')
assert len(cards) == 12
keep_more = {
    'Five EU states plan Rwanda return hub',
    'Singapore seeks trusted AI chip access',
    'Japan scrambles jets over Russian planes',
    'UK sanctions eight firms over settlements',
    'Pentagon fails audit for ninth year',
    'White House curbs testimony to Congress',
    'Thirteen U.S. babies born with measles',
    'President to resign in bribery row',
}
more = []
for c in cards:
    h = h4_of(c)
    if h in keep_more:
        more.append(c)
    else:
        print('more card dropped:', h)
assert len(more) == 8, len(more)
more.sort(key=lambda b: badge_of(b))
assert [badge_of(b) for b in more] == list(range(11, 19))
more_html = ('<!-- MORE STORIES 11-18 -->\n  <div class="sec">\n'
             '    <div class="tag">MORE STORIES <span>&middot; 11&ndash;18</span></div>\n'
             '    <div class="moregrid">\n' +
             '\n'.join('    ' + b for b in more) +
             '\n    </div>\n  </div>\n')

# ---------------------------------------------------------------- FENOMENA 27-30
fens = find_cards(section(html, '<!-- FENOMENA -->', '<!-- BOTTOM: MAP + ALSO ON -->'), 'fenpanel', '      ')
assert len(fens) == 4
fen_new = {}
for f in fens:
    h = h4_of(f)
    if 'Leonid' in h:
        fen_new[27] = renum_badge(f, 27)
    elif 'Aurora' in h:
        fen_new[28] = renum_badge(f, 28)
    elif 'Eruption' in h or 'hectares' in h:
        fen_new[29] = renum_badge(f, 29)
    elif 'quak' in h.lower() or 'Arthur' in h:
        fen_new[30] = renum_badge(f, 30)
    else:
        raise SystemExit('unknown fen panel: ' + h)
assert sorted(fen_new) == [27, 28, 29, 30]
# stretch fen band art to the new height (viewBox 185x36, no preserveAspectRatio)
fen_blocks = []
for n in (27, 28, 29, 30):
    b = fen_new[n]
    b = b.replace('<svg viewBox="0 0 185 36"', '<svg viewBox="0 0 185 36" preserveAspectRatio="none"', 1)
    fen_blocks.append(b)
fen_html = ('<!-- FENOMENA -->\n  <div class="sec">\n'
            '    <div class="tag">FENOMENA &middot; NATURE &amp; SKY <span>&middot; 27&ndash;30</span></div>\n'
            '    <div class="fengrid4">\n' +
            '\n'.join('      ' + f for f in fen_blocks) +
            '\n    </div>\n  </div>\n')

# ---------------------------------------------------------------- splice sections
i = html.index('<!-- 10 BERITA TERBESAR -->')
j = html.index('<!-- MORE STORIES 11-22 -->')
html = html[:i] + top10_html + '\n' + html[j:]
i = html.index('<!-- MORE STORIES 11-22 -->')
j = html.index('<!-- FENOMENA -->')
html = html[:i] + more_html + '\n' + html[j:]
i = html.index('<!-- FENOMENA -->')
j = html.index('<!-- BOTTOM: MAP + ALSO ON -->')
html = html[:i] + fen_html + '\n' + html[j:]

# ---------------------------------------------------------------- bottom: world map markers + ALSO ON
mi = html.index('<svg viewBox="0 6 440 160"')
mj = html.index('</svg>', mi)
msvg = html[mi:mj]
gi = msvg.index('<g font-family="Liberation Sans, DejaVu Sans, sans-serif" font-size="7.5"')
new_msvg = msvg[:gi] + MARKERS + '\n'
html = html[:mi] + new_msvg + html[mj:]

# ALSO ON: keep 6 old items, renumber, add Voyager (25) + Brazil (26)
ai = html.index('<div class="alsocol">')
aj = html.index('<!-- FOOTER -->', ai)
als = html[ai:aj]
assert '&middot; 23&ndash;32' in als
als = als.replace('&middot; 23&ndash;32', '&middot; 19&ndash;26', 1)
items = re.findall(r'          <div class="item">.*?</div>', als, re.S)
assert len(items) == 10, len(items)
keep_als = {23: 19, 24: 20, 26: 21, 27: 22, 31: 23, 32: 24}
kept = {}
for it in items:
    n = badge_of(it)
    if n in keep_als:
        kept[keep_als[n]] = renum_badge(it, keep_als[n])
    else:
        print('also-on item dropped:', re.search(r'<p>(.*?)</p>', it, re.S).group(1)[:50])
assert sorted(kept) == [19, 20, 21, 22, 23, 24], sorted(kept)

VOYAGER = ('          <div class="item"><span class="num" style="background:#55524a">25</span>'
           '<svg viewBox="0 0 20 20" aria-label="A star with an orbit ring"><rect width="20" height="20" fill="#1d2b45"/>'
           '<ellipse cx="10" cy="10" rx="8" ry="3" fill="none" stroke="#ffd97a" stroke-width="1" transform="rotate(-20 10 10)"/>'
           '<polygon points="10,4 11.2,8 15,8 12,10.2 13,14 10,11.8 7,14 8,10.2 5,8 8.8,8" fill="#ffd97a"/></svg>'
           '<p><b>Voyager 1:</b> nears one light-day from Earth.</p></div>')
BRAZIL = ('          <div class="item"><span class="num" style="background:#2e8b57">26</span>'
          '<svg viewBox="0 0 20 20" aria-label="A football"><rect width="20" height="20" fill="#eef0ea"/>'
          '<circle cx="10" cy="10" r="8" fill="#fff" stroke="#2b2b2b" stroke-width="1"/>'
          '<polygon points="10,7 12.5,8.8 11.5,12 8.5,12 7.5,8.8" fill="#2b2b2b"/>'
          '<g stroke="#2b2b2b" stroke-width="0.8"><line x1="10" y1="7" x2="10" y2="3.5"/><line x1="12.5" y1="8.8" x2="16" y2="8"/>'
          '<line x1="11.5" y1="12" x2="13.5" y2="15"/><line x1="8.5" y1="12" x2="6.5" y2="15"/><line x1="7.5" y1="8.8" x2="4" y2="8"/></g></svg>'
          '<p><b>Brazil:</b> 7&ndash;0 Singapore; Vin&iacute;cius treble.</p></div>')
kept[25] = VOYAGER
kept[26] = BRAZIL
cols_html = ('      <div class="cols">\n        <div class="col">\n' +
             '\n'.join(kept[n] for n in (19, 20, 21, 22)) +
             '\n        </div>\n        <div class="col">\n' +
             '\n'.join(kept[n] for n in (23, 24, 25, 26)) +
             '\n        </div>\n      </div>')
ci = als.index('      <div class="cols">')
cj = als.index('    </div>\n  </div>', ci)
als = als[:ci] + cols_html + '\n' + als[cj:]
html = html[:ai] + als + html[aj:]

open(OUT, 'w', encoding='utf-8').write(html)
print('written', OUT, len(html), 'bytes')
