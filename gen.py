# Paired horizontal bar charts (master vs this PR) as standalone SVG pages.
import sys
THEMES = {
  'light': dict(bg='#ffffff', ink='#1f2328', ink2='#59636e', grid='#e3e6ea', base='#a3a8ae', pr='#2a78d6'),
  'dark':  dict(bg='#0d1117', ink='#e6edf3', ink2='#9198a1', grid='#2a3038', base='#6e7681', pr='#3987e5'),
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

def chart(title, subtitle, unit, rows, t, width=760, label_w=190, note=None, suffix='× faster'):
    bar_h, gap_in, row_gap = 16, 4, 22
    top = 92; left = label_w + 16; right = 150
    plot_w = width - left - right
    vmax = max(max(a, b) for _, a, b in rows)
    step = nice_step(vmax)
    vtop = step * -(-vmax // step)
    sx = lambda v: left + plot_w * v / vtop
    rh = 2 * bar_h + gap_in
    height = top + len(rows) * (rh + row_gap) + 40 + (22 if note else 0)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}">',
         f'<rect width="100%" height="100%" fill="{t["bg"]}"/>',
         f'<text x="24" y="34" font-size="17" font-weight="600" fill="{t["ink"]}">{title}</text>',
         f'<text x="24" y="56" font-size="13" fill="{t["ink2"]}">{subtitle}</text>']
    # legend
    lx = 24
    for name, col in (('master', t['base']), ('this PR', t['pr'])):
        o.append(f'<rect x="{lx}" y="68" width="12" height="12" rx="2" fill="{col}"/>')
        o.append(f'<text x="{lx+18}" y="78.5" font-size="12.5" fill="{t["ink2"]}">{name}</text>')
        lx += 18 + 7.5 * len(name) + 22
    axis_y = top + len(rows) * (rh + row_gap) - row_gap + 10
    v = 0
    while v <= vtop:
        x = sx(v)
        o.append(f'<line x1="{x:.1f}" y1="{top-6}" x2="{x:.1f}" y2="{axis_y}" stroke="{t["grid"]}" stroke-width="1"/>')
        o.append(f'<text x="{x:.1f}" y="{axis_y+16}" font-size="11.5" fill="{t["ink2"]}" text-anchor="middle">{fmt(v)}</text>')
        v += step
    o.append(f'<text x="{left + plot_w/2:.1f}" y="{axis_y+34}" font-size="11.5" fill="{t["ink2"]}" text-anchor="middle">{unit}</text>')
    y = top
    for label, a, b in rows:
        o.append(f'<text x="{label_w}" y="{y + rh/2 + 4.5:.1f}" font-size="13" fill="{t["ink"]}" text-anchor="end">{label}</text>')
        for i, (val, col) in enumerate(((a, t['base']), (b, t['pr']))):
            yy = y + i * (bar_h + gap_in)
            w = max(sx(val) - left, 2)
            o.append(f'<path d="{bar_path(left, yy, w, bar_h, 4)}" fill="{col}"/>')
            o.append(f'<text x="{left + w + 6:.1f}" y="{yy + bar_h - 3.5:.1f}" font-size="12" fill="{t["ink2"]}">{fmt(val)}</text>')
        f = a / b
        o.append(f'<text x="{width - 24}" y="{y + rh/2 + 5:.1f}" font-size="14" font-weight="600" fill="{t["ink"]}" text-anchor="end">{f:.1f}{suffix}</text>' if f >= 1 else '')
        y += rh + row_gap
    if note:
        o.append(f'<text x="24" y="{height - 14}" font-size="11.5" fill="{t["ink2"]}">{note}</text>')
    o.append('</svg>')
    return '\n'.join(o), width, height

def bar_path(x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    return (f'M{x:.1f},{y:.1f} H{x + w - r:.1f} Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f} '
            f'V{y + h - r:.1f} Q{x + w:.1f},{y + h:.1f} {x + w - r:.1f},{y + h:.1f} H{x:.1f} Z')

def nice_step(vmax):
    for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000):
        if vmax / s <= 6: return s
    return 10000

def fmt(v):
    return f'{v:,.0f}' if v >= 10 or v == int(v) else f'{v:.1f}'

CHARTS = {
  'hsc2hs': dict(
    title='hsc2hs-heavy libraries, ghc914-sh',
    subtitle='Minutes per build on Hydra, x86_64-linux jobs: master evals 2944–2995 vs eval 3014',
    unit='minutes',
    rows=[('unix · ghcjs', 123, 26), ('ghc-internal · ghcjs', 97, 54),
          ('ghc-internal · wasm32', 59, 35), ('unix · wasm32', 26, 11)]),
  'dedup': dict(
    title='Slice deduplication (#2606), ghc914-sh x86_64-linux jobs',
    subtitle='Components present in both evals: master eval 2969 vs eval 3014',
    unit='build-hours',
    rows=[('build-hours', 522, 145)],
    suffix='× fewer hours',
    note='7,275 → 3,236 component derivations; about 256 of the hours saved are copies no longer built'),
}
for name, c in CHARTS.items():
    for theme, t in THEMES.items():
        svg, w, h = chart(c['title'], c['subtitle'], c['unit'], c['rows'], t, note=c.get('note'), suffix=c.get('suffix', '× faster'))
        open(f'{name}-{theme}.svg', 'w').write(svg)
        open(f'{name}-{theme}.html', 'w').write(
            f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;background:{t["bg"]}}}</style>{svg}')
        print(name, theme, w, h)
