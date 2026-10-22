"""Genera las imágenes (línea gráfica ER) del predespacho semanal y del redespacho."""
import math, html, asyncio, pathlib, datetime as dt
from parse_pds import *

BLUE, GOLD, NAVY, G2, G3, GRID, DIV, CTX = '#0A63F9', '#F2B931', '#0B1B36', '#5B6577', '#8A94A6', '#E6E9EE', '#D5DAE1', '#A3ACBB'
TECH_COLOR = {'HIDRO': '#0A63F9', 'CHIXOY': '#0B3FA0', 'SOLAR': '#6C9DF5', 'EOLICA': '#B9D0FA', 'GEO': '#3A7DF2',
              'VAPOR': '#0B1B36', 'MOTORES': '#5B6577', 'COGEN': '#A3ACBB', 'CARIBE': '#D5DAE1', 'GAS': '#8A94A6', 'MEX': '#E6E9EE'}
TECH_NAME = {k: v[1] for k, v in TECH_LABEL.items()}
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
CANAL = 'Información Mercado Eléctrico de Guatemala'
ASSETS = pathlib.Path(__file__).parent / 'assets'

def fdate(d, year=False):
    return f"{d.day} {MESES[d.month-1]}" + (f" {d.year}" if year else '')

def period(days):
    a, b = days[0], days[-1]
    if a == b: return f"{a.day} de {MESES[a.month-1]} {a.year}"
    if a.month == b.month: return f"{a.day} al {b.day} {MESES[b.month-1]} {b.year}"
    return f"{fdate(a)} al {fdate(b)} {b.year}"

def n0(x): return f"{x:,.0f}"
def n1(x): return f"{x:,.1f}"
def money(x):
    return f"US${x/1e6:,.2f} M" if abs(x) >= 1e6 else f"US${x/1e3:,.0f} k" if abs(x) >= 1e4 else f"US${x:,.0f}"

def var_html(p, size=15, invert=False):
    """Variación % con flecha. Sube = azul, baja = gris (sin rojos en la línea ER)."""
    if p is None: return f'<span style="color:{G3};font-size:{size}px">nuevo</span>'
    if abs(p) < 0.05: return f'<span style="color:{G3};font-size:{size}px">= 0.0%</span>'
    up = p > 0
    col = BLUE if up else G2
    return f'<span style="color:{col};font-size:{size}px;font-weight:600">{"▲" if up else "▼"} {"+" if up else "−"}{abs(p):.1f}%</span>'

def esc(s): return html.escape(str(s))

HEAD = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{{title}}</title><style>
@font-face{{{{font-family:'Space Grotesk';src:url({ASSETS.as_uri()}/fonts/SpaceGrotesk.ttf);font-weight:300 700}}}}
@font-face{{{{font-family:'IBM Plex Mono';src:url({ASSETS.as_uri()}/fonts/IBMPlexMono-Regular.ttf);font-weight:400}}}}
@font-face{{{{font-family:'IBM Plex Mono';src:url({ASSETS.as_uri()}/fonts/IBMPlexMono-Medium.ttf);font-weight:500}}}}
@font-face{{{{font-family:'IBM Plex Mono';src:url({ASSETS.as_uri()}/fonts/IBMPlexMono-SemiBold.ttf);font-weight:600}}}}
body{{{{margin:0}}}} .mono{{{{font-family:'IBM Plex Mono',monospace}}}}
.sec{{{{font-family:'IBM Plex Mono',monospace;font-size:14px;font-weight:600;letter-spacing:.12em;color:{BLUE};margin-bottom:12px}}}}
table{{{{border-collapse:collapse}}}}
</style></head><body>"""

def frame(label, title, subtitle, body, source, height):
    return HEAD.format(title=esc(title)) + f"""
<div id="page" style="width:1080px;min-height:1080px;box-sizing:border-box;background:#fff;color:{NAVY};font-family:'Space Grotesk',sans-serif;display:flex;flex-direction:column">
<div style="display:flex;height:10px"><div style="flex:3;background:{BLUE}"></div><div style="flex:1;background:{GOLD}"></div></div>
<div style="flex:1;padding:48px 72px 40px;display:flex;flex-direction:column;gap:28px">
 <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:32px">
  <div style="display:flex;flex-direction:column;gap:12px">
   <div class="mono" style="font-size:17px;font-weight:500;letter-spacing:.12em;color:{BLUE}">{esc(label)}</div>
   <h1 style="margin:0;font-weight:700;font-size:46px;line-height:1.08;letter-spacing:-.02em;max-width:780px">{esc(title)}</h1>
   <div style="font-size:20px;color:{G2}">{esc(subtitle)}</div>
  </div>
  <img src="{ASSETS.as_uri()}/logo_er.png" style="width:96px;height:96px;margin-top:4px;flex-shrink:0">
 </div>
 {body}
 <div style="margin-top:12px;display:flex;justify-content:space-between;align-items:center;gap:24px;border-top:1px solid {DIV};padding-top:14px" class="mono">
  <div style="font-size:15px;color:{G2}">FUENTE · {esc(source)}</div>
  <div style="display:flex;align-items:center;gap:10px;white-space:nowrap;font-family:'Space Grotesk';font-size:18px;font-weight:600;color:{NAVY}">
   <img src="{ASSETS.as_uri()}/logo_er.png" style="width:30px;height:30px">{CANAL}</div>
 </div>
</div></div></body></html>"""


def kpi(label, value, unit, var, note=''):
    return f"""<div style="flex:1;border-top:3px solid {NAVY};padding-top:12px;display:flex;flex-direction:column;gap:6px">
 <div class="mono" style="font-size:13px;letter-spacing:.08em;color:{G2}">{esc(label)}</div>
 <div class="mono" style="font-size:34px;font-weight:600;line-height:1">{value}<span style="font-size:17px;color:{G2};font-weight:500"> {unit}</span></div>
 <div class="mono">{var}{f' <span style="color:{G3};font-size:13px">{note}</span>' if note else ''}</div></div>"""


def donut(parts, total, center_top, center_bottom, size=280):
    cx = cy = size / 2; R, r = size / 2 - 4, size / 2 - 52
    a0, out = -math.pi / 2, []
    for key, v in parts:
        if v <= 0: continue
        a1 = a0 + 2 * math.pi * v / total
        large = 1 if a1 - a0 > math.pi else 0
        p = lambda ang, rad: (cx + rad * math.cos(ang), cy + rad * math.sin(ang))
        x0, y0 = p(a0, R); x1, y1 = p(a1, R); x2, y2 = p(a1, r); x3, y3 = p(a0, r)
        out.append(f'<path d="M{x0:.2f},{y0:.2f} A{R},{R} 0 {large} 1 {x1:.2f},{y1:.2f} L{x2:.2f},{y2:.2f} A{r},{r} 0 {large} 0 {x3:.2f},{y3:.2f} Z" fill="{TECH_COLOR[key]}" stroke="#fff" stroke-width="2"/>')
        a0 = a1
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">{''.join(out)}
<text x="{cx}" y="{cy-6}" text-anchor="middle" font-family="IBM Plex Mono" font-size="30" font-weight="600" fill="{NAVY}">{center_top}</text>
<text x="{cx}" y="{cy+22}" text-anchor="middle" font-family="IBM Plex Mono" font-size="14" fill="{G2}">{center_bottom}</text></svg>"""


# ====================== PREDESPACHO ======================
def build_pre(cur, prev, cur_file, prev_file):
    s, p = summary(cur), summary(prev)
    d_dem, d_peak, d_cost = pct(s['dem'], p['dem']), pct(s['peak'], p['peak']), pct(s['total_cost'], p['total_cost'])
    title = (f"Semana {s['week']}: {'más' if d_dem >= 0 else 'menos'} demanda y un costo operativo "
             f"{abs(d_cost):.1f}% {'menor' if d_cost < 0 else 'mayor'}")
    subtitle = f"Predespacho semanal · {period(s['days'])} · variaciones vs semana {p['week']}"
    mp = s['mant']
    kpis = ''.join([
        kpi('DEMANDA SNI', n1(s['dem']/1000), 'GWh', var_html(pct(s['dem'], p['dem']))),
        kpi('PICO DE POTENCIA', n0(s['peak']), 'MW', var_html(d_peak)),
        kpi('COSTO OPERATIVO', f"{s['total_cost']/1e6:,.2f}", 'M US$', var_html(d_cost)),
        kpi('MANTENIMIENTOS PROG.', str(mp.get('P', [0, 0])[0]), '', f'<span style="color:{G2};font-size:15px">{n1(mp.get("P",[0,0])[1])} MW</span>'),
    ])
    # Mix
    order = sorted([t for t in MIX_ORDER if s['mix'].get(t, 0) > 0.5], key=lambda t: -s['mix'][t])
    tot = s['gen_total']
    rows = ''
    for t in order:
        v = s['mix'][t]; pv = p['mix'].get(t, 0)
        rows += f"""<tr style="border-bottom:1px solid {GRID}">
<td style="padding:6px 0;width:18px"><div style="width:12px;height:12px;background:{TECH_COLOR[t]}"></div></td>
<td style="padding:6px 8px;font-size:17px">{TECH_NAME[t]}</td>
<td class="mono" style="text-align:right;font-size:16px;font-weight:600">{n1(v/1000)}</td>
<td class="mono" style="text-align:right;font-size:15px;color:{G2};padding-left:14px">{v/tot*100:.1f}%</td>
<td class="mono" style="text-align:right;padding-left:14px;white-space:nowrap">{var_html(pct(v, pv) if pv else None, 14)}</td></tr>"""
    mix_html = f"""<div><div class="sec">MIX DE GENERACIÓN PROGRAMADO</div>
<div style="display:flex;gap:36px;align-items:center">
{donut([(t, s['mix'][t]) for t in order], tot, n1(tot/1000), 'GWh generación')}
<table style="flex:1"><tr class="mono" style="font-size:12px;color:{G3};letter-spacing:.06em">
<td></td><td style="padding:0 8px 4px">TECNOLOGÍA</td><td style="text-align:right">GWh</td><td style="text-align:right">PART.</td><td style="text-align:right">VS SEM. {p['week']}</td></tr>{rows}</table>
</div></div>"""
    # Top 5 costo
    mx = s['top_cost'][0]['cost']
    bars = ''
    for i, pl in enumerate(s['top_cost']):
        w = pl['cost'] / mx * 100
        bars += f"""<div style="margin-bottom:12px">
<div style="display:flex;justify-content:space-between;font-size:16px;margin-bottom:4px"><span><b class="mono" style="color:{G3}">{i+1}</b>&nbsp; {esc(pl['name'])}</span>
<span class="mono" style="font-weight:600">{money(pl['cost'])} <span style="color:{G2};font-weight:400;font-size:13px">{pl['cost']/s['total_cost']*100:.1f}%</span></span></div>
<div style="height:10px;background:{GRID}"><div style="width:{w:.1f}%;height:10px;background:{GOLD if i == 0 else BLUE}"></div></div>
<div class="mono" style="font-size:12px;color:{G3};margin-top:3px">{n0(pl['energy'])} MWh</div></div>"""
    cov = f"Costo = energía × CVG. Cubre {s['coverage']*100:.1f}% de la generación" + (f"; sin CVG: {', '.join(s['no_cvg'])}" if s['no_cvg'] else '')
    top_html = f"""<div style="flex:1.15"><div class="sec">TOP 5 PLANTAS POR COSTO OPERATIVO</div>{bars}
<div class="mono" style="font-size:12px;color:{G3};line-height:1.4">{esc(cov)}.</div></div>"""
    # Chixoy + mantenimientos
    chx = f"""<div class="sec">CHIXOY</div>
<div style="display:flex;gap:28px;margin-bottom:26px">
 <div><div class="mono" style="font-size:13px;color:{G2}">ENERGÍA SEMANAL</div><div class="mono" style="font-size:28px;font-weight:600">{n0(s['chixoy_e'])}<span style="font-size:15px;color:{G2}"> MWh</span></div>{var_html(pct(s['chixoy_e'], p['chixoy_e']),14)}</div>
 <div><div class="mono" style="font-size:13px;color:{G2}">VALOR DEL AGUA</div><div class="mono" style="font-size:28px;font-weight:600">{s['chixoy_wv']:.2f}<span style="font-size:15px;color:{G2}"> US$/MWh</span></div>{var_html(pct(s['chixoy_wv'], p['chixoy_wv']),14)}</div>
</div>"""
    tm = ''.join(f"""<div style="display:flex;justify-content:space-between;font-size:15px;padding:4px 0;border-bottom:1px solid {GRID}">
<span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;margin-right:12px">{esc(x['equipo'])}</span><span class="mono" style="font-weight:600;white-space:nowrap">{n1(x['mw'])} MW</span></div>""" for x in s['top_mant'])
    c = lambda k: mp.get(k, [0, 0.0])
    mant = f"""<div class="sec">MANTENIMIENTOS</div>
<div class="mono" style="font-size:14px;color:{G2};margin-bottom:8px;line-height:1.5">
<div><b style="color:{NAVY}">{c('P')[0]}</b> programados · {n1(c('P')[1])} MW</div><div><b style="color:{NAVY}">{c('NP')[0]}</b> no programados · {n1(c('NP')[1])} MW</div><div><b style="color:{NAVY}">{c('C')[0]}</b> cancelados · {n1(c('C')[1])} MW</div></div>
<div class="mono" style="font-size:12px;color:{G3};letter-spacing:.06em;margin:6px 0 2px">MAYOR IMPACTO (PROGRAMADOS)</div>{tm}"""
    body = f"""<div style="display:flex;gap:24px">{kpis}</div>
{mix_html}
<div style="display:flex;gap:48px">{top_html}<div style="flex:1">{chx}{mant}</div></div>"""
    source = f"AMM · Programación semanal, sem. {s['week']}"
    return frame('MERCADO MAYORISTA · PREDESPACHO SEMANAL', title, subtitle, body, source, 1500), s, p


# ====================== REDESPACHO ======================
def build_rep(old, new, old_file, new_file):
    days = new['days']
    po = {x['name']: x for x in plant_costs(old, days)}
    pn = {x['name']: x for x in plant_costs(new, days)}
    co = sum(x['cost'] or 0 for x in po.values()); cn = sum(x['cost'] or 0 for x in pn.values())
    dc = cn - co; dcp = pct(cn, co)
    mo, mn = mix(old, days), mix(new, days)
    wvo, wvn = chixoy_water_value(old, days), chixoy_water_value(new, days)
    wvo = sum(wvo)/len(wvo); wvn = sum(wvn)/len(wvn)
    notes = [o for o in new['obs'] if o not in old['obs']] or new['obs'][:1]
    a_, b_ = days[0], days[-1]
    if len(days) == 1: dlabel = f"{a_.day}\u00a0de\u00a0{MESES[a_.month-1]}"
    elif a_.month == b_.month: dlabel = f"{a_.day} al {b_.day}\u00a0de\u00a0{MESES[b_.month-1]}"
    else: dlabel = f"{fdate(a_)} al {fdate(b_)}"
    title = f"Redespacho sem. {new['week']}: el costo {'del' if len(days)==1 else 'del'} {dlabel} {'baja' if dc < 0 else 'sube'} {abs(dcp):.1f}%"
    prev_lbl = 'predespacho original' if not old['is_rep'] else f"redespacho ({old['rev']})"
    subtitle = f"Redespacho ({new['rev']}) vigente {period(days)} · comparado con el {prev_lbl}"

    note_html = ''.join(f'<li style="margin-bottom:6px">{esc(n)}</li>' for n in notes)
    nota = f"""<div style="border-left:4px solid {GOLD};padding:2px 0 2px 18px">
<div class="sec" style="margin-bottom:6px">NOTA AMM · MOTIVO DEL REDESPACHO</div>
<ul style="margin:0;padding-left:18px;font-size:16px;line-height:1.4;color:{NAVY}">{note_html}</ul></div>"""

    cost = f"""<div style="display:flex;gap:40px;align-items:flex-end">
<div><div class="sec" style="margin-bottom:4px">COSTO OPERATIVO · DÍAS AFECTADOS</div>
<div class="mono" style="font-size:44px;font-weight:600;line-height:1.1"><span style="color:{CTX}">{co/1e6:,.2f}</span> <span style="color:{G3};font-size:30px">→</span> <span style="color:{BLUE}">{cn/1e6:,.2f}</span><span style="font-size:18px;color:{G2}"> M US$</span></div></div>
<div class="mono" style="padding-bottom:6px"><div style="font-size:30px;font-weight:600;color:{GOLD if dc<0 else NAVY}">{'−' if dc<0 else '+'}{money(abs(dc))}</div>
<div style="font-size:15px;color:{G2}">{'−' if dc<0 else '+'}{abs(dcp):.1f}% vs {prev_lbl}</div></div></div>"""

    # Dumbbell por tecnología
    techs = sorted([t for t in MIX_ORDER if mo.get(t, 0) > 0.5 or mn.get(t, 0) > 0.5], key=lambda t: -max(mo.get(t, 0), mn.get(t, 0)))
    W, X0, X1, RH = 470, 190, 400, 34
    vmax = max(max(mo.get(t, 0), mn.get(t, 0)) for t in techs) * 1.05
    sx = lambda v: X0 + (X1 - X0) * v / vmax
    g = []
    for i, t in enumerate(techs):
        y = 34 + i * RH; a, b = mo.get(t, 0), mn.get(t, 0); d = b - a
        g.append(f'<text x="0" y="{y+5}" font-size="14" fill="{NAVY}" font-family="Space Grotesk">{TECH_NAME[t]}</text>')
        g.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="{GRID}"/>')
        if abs(d) > 0.5:
            g.append(f'<line x1="{sx(a):.1f}" y1="{y}" x2="{sx(b):.1f}" y2="{y}" stroke="#9DBEF8" stroke-width="4"/>')
        g.append(f'<circle cx="{sx(a):.1f}" cy="{y}" r="6" fill="{CTX}"/>')
        g.append(f'<circle cx="{sx(b):.1f}" cy="{y}" r="7" fill="{BLUE if abs(d)>0.5 else CTX}"/>')
        col = BLUE if d > 0.5 else (G2 if d < -0.5 else G3)
        txt = f"{'+' if d>=0 else '−'}{n0(abs(d))}" if abs(d) > 0.5 else '= 0'
        g.append(f'<text x="{W}" y="{y+5}" text-anchor="end" font-size="14" font-weight="600" fill="{col}" font-family="IBM Plex Mono">{txt}</text>')
    hh = 34 + len(techs) * RH
    legend = (f'<circle cx="{X0+4}" cy="10" r="6" fill="{CTX}"/><text x="{X0+16}" y="15" font-size="13" fill="{G2}" font-family="IBM Plex Mono">antes</text>'
              f'<circle cx="{X0+84}" cy="10" r="7" fill="{BLUE}"/><text x="{X0+96}" y="15" font-size="13" fill="{NAVY}" font-family="IBM Plex Mono">redespacho</text>'
              f'<text x="{W}" y="15" text-anchor="end" font-size="12" fill="{G3}" font-family="IBM Plex Mono">Δ MWh</text>')
    dumb = f"""<div style="flex:1"><div class="sec">CAMBIO EN EL MIX · MWh</div>
<svg width="{W}" height="{hh}" viewBox="0 0 {W} {hh}">{legend}{''.join(g)}</svg></div>"""

    # Cambios por planta
    ch = [(n, po[n]['energy'], pn[n]['energy']) for n in pn if n in po and pn[n]['tech'] in MIX_ORDER]
    ch = sorted([c for c in ch if abs(c[2]-c[1]) > 0.5], key=lambda c: -abs(c[2]-c[1]))[:8]
    dmax = max(abs(b-a) for _, a, b in ch) if ch else 1
    prow = ''
    for n, a, b in ch:
        d = b - a; w = abs(d) / dmax * 100
        if b < 0.5: tag = '<span style="color:' + G2 + '">se apaga</span>'
        elif a < 0.5: tag = '<span style="color:' + BLUE + '">entra</span>'
        else: tag = f'{n0(a)} → {n0(b)}'
        prow += f"""<div style="margin-bottom:9px"><div style="display:flex;justify-content:space-between;font-size:15px">
<span>{esc(n)}</span><span class="mono" style="font-weight:600;color:{BLUE if d>0 else G2}">{'+' if d>0 else '−'}{n0(abs(d))}</span></div>
<div style="display:flex;align-items:center;gap:8px"><div style="flex:1;height:8px;background:{GRID}"><div style="width:{w:.1f}%;height:8px;background:{BLUE if d>0 else CTX}"></div></div>
<span class="mono" style="font-size:12px;color:{G3};white-space:nowrap">{tag}</span></div></div>"""
    plants = f"""<div style="flex:1"><div class="sec">PRINCIPALES CAMBIOS POR PLANTA · MWh</div>{prow}</div>"""

    cxo, cxn = po['CHIXOY'], pn['CHIXOY']
    chx = f"""<div><div class="sec">CHIXOY · DÍAS AFECTADOS</div>
<div style="display:flex;gap:44px" class="mono">
 <div><div style="font-size:13px;color:{G2}">ENERGÍA</div><div style="font-size:24px;font-weight:600">{n0(cxo['energy'])} → <span style="color:{BLUE}">{n0(cxn['energy'])}</span><span style="font-size:14px;color:{G2}"> MWh</span></div>{var_html(pct(cxn['energy'], cxo['energy']),14)}</div>
 <div><div style="font-size:13px;color:{G2}">VALOR DEL AGUA</div><div style="font-size:24px;font-weight:600">{wvo:.2f} → <span style="color:{BLUE}">{wvn:.2f}</span><span style="font-size:14px;color:{G2}"> US$/MWh</span></div>{var_html(pct(wvn, wvo),14)}</div>
 <div><div style="font-size:13px;color:{G2}">COSTO</div><div style="font-size:24px;font-weight:600">{money(cxo['cost'])} → <span style="color:{BLUE}">{money(cxn['cost'])}</span></div>{var_html(pct(cxn['cost'], cxo['cost']),14)}</div>
</div></div>"""

    body = f"""{nota}{cost}<div style="display:flex;gap:56px">{dumb}{plants}</div>{chx}"""
    source = f"AMM · Ajuste a la programación semanal ({new['rev']})"
    res = {'co': co, 'cn': cn, 'mo': mo, 'mn': mn, 'wvo': wvo, 'wvn': wvn, 'changes': ch, 'notes': notes}
    return frame('MERCADO MAYORISTA · REDESPACHO SEMANAL', title, subtitle, body, source, 1500), res


async def to_png(html_path, png_path, height=1500):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': height}, device_scale_factor=2)
        await pg.goto(pathlib.Path(html_path).resolve().as_uri())
        await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
        # altura real del contenido para detectar desbordes
        over = await pg.evaluate("Math.ceil(document.getElementById('page').getBoundingClientRect().height)")
        await pg.set_viewport_size({'width': 1080, 'height': over})
        await pg.screenshot(path=str(png_path), clip={'x': 0, 'y': 0, 'width': 1080, 'height': over})
        await b.close()
        return over
