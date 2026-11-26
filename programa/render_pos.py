"""Imagen (línea gráfica ER) del PosDespacho diario vs programa semanal."""
from render import (esc, n0, n1, MESES, TECH_NAME, HEAD, ASSETS, CANAL,
                    BLUE, GOLD, NAVY, GRID, DIV)
from parse_pds import pct

# Formato para celular (pedido 2026-11-26): grises más oscuros, letra más grande e imagen más alta
# (1080 x ~2200, llena la pantalla del teléfono). Solo aplica a la imagen del posdespacho.
G2, G3, CTX = '#2E3848', '#465166', '#7C8699'
TRACK = '#DFE3EA'


def var_html(p, size=22):
    if p is None: return f'<span style="color:{G3};font-size:{size}px">nuevo</span>'
    if abs(p) < 0.05: return f'<span style="color:{G3};font-size:{size}px">= 0.0%</span>'
    up = p > 0
    return f'<span style="color:{BLUE if up else G2};font-size:{size}px;font-weight:600">{"▲" if up else "▼"} {"+" if up else "−"}{abs(p):.1f}%</span>'


def kpi(label, value, unit, var):
    return f"""<div style="border-top:4px solid {NAVY};padding-top:14px;display:flex;flex-direction:column;gap:8px">
 <div class="mono" style="font-size:18px;letter-spacing:.04em;color:{G2};min-height:46px;line-height:1.25">{esc(label)}</div>
 <div class="mono" style="font-size:44px;font-weight:600;line-height:1">{value}</div>
 <div class="mono" style="font-size:20px;color:{G2};font-weight:500">{unit}</div>
 <div class="mono" style="font-size:19px;line-height:1.35">{var}</div></div>"""


def sec(t):
    return f'<div class="mono" style="font-size:21px;font-weight:600;letter-spacing:.1em;color:{BLUE};margin-bottom:18px">{t}</div>'


def frame(label, title, subtitle, body, source):
    return HEAD.format(title=esc(title)) + f"""
<div id="page" style="width:1080px;min-height:2340px;box-sizing:border-box;background:#fff;color:{NAVY};font-family:'Space Grotesk',sans-serif;display:flex;flex-direction:column">
<div style="display:flex;height:14px"><div style="flex:3;background:{BLUE}"></div><div style="flex:1;background:{GOLD}"></div></div>
<div style="flex:1;padding:48px 56px 38px;display:flex;flex-direction:column;gap:34px">
 <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:28px">
  <div style="display:flex;flex-direction:column;gap:14px">
   <div class="mono" style="font-size:21px;font-weight:500;letter-spacing:.1em;color:{BLUE}">{esc(label)}</div>
   <h1 style="margin:0;font-weight:700;font-size:58px;line-height:1.08;letter-spacing:-.02em">{esc(title)}</h1>
   <div style="font-size:25px;color:{G2}">{esc(subtitle)}</div>
  </div>
  <img src="{ASSETS.as_uri()}/logo_er.png" style="width:112px;height:112px;margin-top:4px;flex-shrink:0">
 </div>
 {body}
 <div style="margin-top:auto;display:flex;justify-content:space-between;align-items:center;gap:20px;border-top:2px solid {DIV};padding-top:18px" class="mono">
  <div style="font-size:18px;color:{G2}">FUENTE · {esc(source)}</div>
  <div style="display:flex;align-items:center;gap:10px;white-space:nowrap;font-family:'Space Grotesk';font-size:21px;font-weight:600;color:{NAVY}">
   <img src="{ASSETS.as_uri()}/logo_er.png" style="width:36px;height:36px">{CANAL}</div>
 </div>
</div></div></body></html>"""

DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
TECH_NAME_POS = {**TECH_NAME, 'MEX': 'Importación oportunidad México'}


def fecha_larga(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month-1]} {d.year}"


def signo(x, dec=0):
    f = f"{abs(x):,.{dec}f}"
    return ('+' if x >= 0 else '−') + f


def poe_chart(poe, W=968, H=330):
    if not poe: return ''
    vals = [p['poe'] for p in poe]
    lo, hi = 0, max(vals) * 1.18
    X0, X1, Y0, Y1 = 84, W - 10, 30, H - 40
    sx = lambda i: X0 + (X1 - X0) * (i + 0.5) / len(vals)
    sy = lambda v: Y1 - (Y1 - Y0) * (v - lo) / (hi - lo)
    step = 50 if hi > 150 else 25
    g = []
    for t in range(0, int(hi) + 1, step):
        g.append(f'<line x1="{X0}" y1="{sy(t):.1f}" x2="{X1}" y2="{sy(t):.1f}" stroke="{GRID}"/>'
                 f'<text x="{X0-8}" y="{sy(t)+5:.1f}" text-anchor="end" font-size="19" fill="{G2}" font-family="IBM Plex Mono">{t}</text>')
    # unidad del eje Y (pedido de Luis Pablo 2026-11-18: el eje debe llevar su dimensional)
    g.append(f'<text transform="translate(18,{(Y0+Y1)/2:.1f}) rotate(-90)" text-anchor="middle" font-size="18" fill="{G2}" font-family="IBM Plex Mono">US$/MWh</text>')
    bw = (X1 - X0) / len(vals) * 0.72
    imax = vals.index(max(vals)); imin = vals.index(min(vals))
    for i, v in enumerate(vals):
        col = GOLD if i == imax else (BLUE if i == imin else '#9DBEF8')
        g.append(f'<rect x="{sx(i)-bw/2:.1f}" y="{sy(v):.1f}" width="{bw:.1f}" height="{Y1-sy(v):.1f}" fill="{col}"/>')
    avg = sum(vals) / len(vals)
    g.append(f'<line x1="{X0}" y1="{sy(avg):.1f}" x2="{X1}" y2="{sy(avg):.1f}" stroke="{NAVY}" stroke-dasharray="7 5" stroke-width="2"/>')
    g.append(f'<rect x="{X0+4}" y="{sy(avg)-30:.1f}" width="170" height="26" fill="#fff"/>'
             f'<text x="{X0+8}" y="{sy(avg)-10:.1f}" font-size="19" fill="{NAVY}" font-family="IBM Plex Mono">prom. {avg:.2f}</text>')
    pm, pn = poe[imax], poe[imin]
    ax = min(max(sx(imax), X0 + 170), X1 - 170)
    g.append(f'<text x="{ax:.1f}" y="{sy(vals[imax])-10:.1f}" text-anchor="middle" font-size="19" font-weight="600" fill="{NAVY}" font-family="IBM Plex Mono">{vals[imax]:.2f} · {esc(pm["gen"])}</text>')
    ay = sy(vals[imin]) - 10
    nx = min(max(sx(imin), X0 + 170), X1 - 170)
    g.append(f'<text x="{nx:.1f}" y="{ay:.1f}" text-anchor="middle" font-size="19" font-weight="600" fill="{BLUE}" font-family="IBM Plex Mono">{vals[imin]:.2f} · {esc(pn["gen"])}</text>')
    for i in range(0, len(vals), 3):
        g.append(f'<text x="{sx(i):.1f}" y="{H-8}" text-anchor="middle" font-size="18" fill="{G2}" font-family="IBM Plex Mono">{poe[i]["de"][:2]}h</text>')
    g.append(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="{NAVY}" stroke-width="2"/>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(g)}</svg>'


def diverging(rows, label_key, maxabs, show_vals=True, compacto=False):
    """Barras divergentes: positivas (real > programado) en azul a la derecha, negativas en gris a la izquierda."""
    out = ''
    for r in rows:
        d = r['diff']; w = abs(d) / maxabs * 50 if maxabs else 0
        p = pct(r['real'], r['prog']) if r['prog'] > 0.5 else None
        ptxt = f"{signo(p,1)}%" if p is not None else '—'
        bar = (f'<div style="position:absolute;left:50%;width:{w:.1f}%;height:14px;background:{BLUE}"></div>' if d > 0 else
               f'<div style="position:absolute;right:50%;width:{w:.1f}%;height:14px;background:{CTX}"></div>')
        out += f"""<div style="margin-bottom:14px">
<div style="display:flex;justify-content:space-between;align-items:baseline;font-size:{21 if compacto else 23}px;gap:10px"><span style="{'white-space:nowrap;overflow:hidden;text-overflow:ellipsis' if compacto else ''}">{esc(r[label_key])}</span>
<span class="mono" style="font-weight:600;font-size:{21 if compacto else 23}px;color:{BLUE if d>0 else G2};white-space:nowrap">{signo(d,0)} MWh{'' if compacto else f' <span style="font-weight:500;font-size:19px">{ptxt}</span>'}</span></div>
<div style="position:relative;height:14px;background:{TRACK};margin-top:6px">{bar}<div style="position:absolute;left:50%;top:-4px;width:3px;height:22px;background:{NAVY}"></div></div>
{f'<div class="mono" style="font-size:{17 if compacto else 19}px;color:{G2};margin-top:5px;display:flex;justify-content:space-between"><span>real {n0(r["real"])} · prog {n0(r["prog"])}</span>' + (f'<span style="color:{BLUE if d>0 else G2};font-weight:500">{ptxt}</span>' if compacto else '') + '</div>' if show_vals else ''}
</div>"""
    return out


def build_pos(c):
    d = c['date']
    dp = pct(c['dem_real'], c['dem_prog'])
    dia = f"{DIAS[d.weekday()].capitalize()} {d.day} {MESES[d.month-1]}"
    if abs(dp) < 0.1:      # diferencia prácticamente nula: no se muestra el porcentaje
        title = f"{dia}: demanda igual a lo programado"
    else:
        title = f"{dia}: demanda {abs(dp):.1f}% {'bajo' if dp < 0 else 'sobre'} lo programado"
    subtitle = f"PosDespacho vs programa semanal (sem. {c['week']}) · {fecha_larga(d)}"

    kp = ''.join([
        kpi('GENERACIÓN TOTAL REAL', n0(c['total_gen']), 'MWh', ''),
        kpi('DEMANDA SNI', n0(c['dem_real']), 'MWh',
            f'<span style="color:{G2}">prog {n0(c["dem_prog"])}</span><br>{var_html(dp, 20)}'),
        kpi('DEMANDA MÁXIMA', n0(c['dmax']) if c['dmax'] else '—', 'MW',
            f'<span style="color:{G2}">a las {c["dmax_hora"] or "—"}</span>'),
        kpi('POE PROMEDIO', f"{c['poe_prom']:.2f}" if c['poe_prom'] else '—', 'US$/MWh', ''),
    ])
    kp = f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:26px">{kp}</div>'
    poe = f"""<div>{sec('PRECIO DE OPORTUNIDAD (POE) POR HORA · US$/MWh')}{poe_chart(c['poe'])}</div>"""

    trows = [{**r, 'name': TECH_NAME_POS.get(r['tech'], r['tech'])} for r in c['pos3'] + c['neg3']]
    allr = trows + ([{**c['chx_row'], 'name': 'Chixoy'}] if c['chx_row'] else [])
    mx = max((abs(r['diff']) for r in allr), default=1)
    tech = f"""<div>{sec('POR TECNOLOGÍA · REAL VS PROGRAMADO')}
{diverging(trows, 'name', mx)}
{f'<div style="border-top:2px dashed {DIV};padding-top:16px;margin-top:4px">' + diverging([{**c["chx_row"], "name": "Chixoy"}], "name", mx) + '</div>' if c['chx_row'] else ''}
</div>"""

    ch = c['chixoy']; cr = c['chx_row']
    lab = f'font-size:19px;letter-spacing:.04em;color:{G2}'
    chx = f"""<div>{sec('CHIXOY')}
<div class="mono" style="display:grid;grid-template-columns:1fr 1fr 1.25fr;gap:24px">
 <div><div style="{lab}">COTA DEL EMBALSE</div><div style="font-size:42px;font-weight:600;margin-top:8px">{ch.get('cota', 0):,.2f}<span style="font-size:20px;color:{G2}"> msnm</span></div></div>
 <div><div style="{lab}">CAUDAL ENTRANTE</div><div style="font-size:42px;font-weight:600;margin-top:8px">{ch.get('q_prom') or ch.get('q_ent') or 0:,.1f}<span style="font-size:20px;color:{G2}"> m³/s</span></div>
  <div style="font-size:19px;color:{G2};margin-top:6px">máx {ch.get('q_max', 0):,.1f} · mín {ch.get('q_min', 0):,.1f}</div></div>
 {f'<div><div style="{lab}">ENERGÍA REAL VS PROG.</div><div style="font-size:34px;font-weight:600;margin-top:8px">{n0(cr["real"])} <span style="color:{G3}">/</span> {n0(cr["prog"])}<span style="font-size:20px;color:{G2}"> MWh</span></div><div style="margin-top:6px">{var_html(pct(cr["real"], cr["prog"]))}</div></div>' if cr else ''}
</div></div>"""

    mxp = max((abs(r['diff']) for r in c['top_plants']), default=1)
    plants = f"""<div>{sec('TOP 5 DIFERENCIAS POR PLANTA · REAL VS PROGRAMADO')}
<div style="display:grid;grid-template-columns:1fr 1fr;column-gap:40px">{diverging(c['top_plants'], 'name', mxp, compacto=True)}</div>
<div class="mono" style="font-size:18px;color:{G2};line-height:1.35">Cascadas, bloques y unidades sumados como una sola planta (p. ej. Renace I–IV, INDE, Xacbal + Delta).</div></div>"""

    body = f"""{kp}{poe}{tech}{chx}{plants}"""
    return frame('MERCADO MAYORISTA · POSDESPACHO DIARIO', title, subtitle, body,
                 f"AMM · PosDespacho {d:%d/%m/%Y} · sem. {c['week']}")


def texto_pos(c):
    d = c['date']
    def lt(r, name):
        p = pct(r['real'], r['prog']) if r['prog'] > 0.5 else None
        return (f"{'📈' if r['diff'] > 0 else '📉'} {name}: {n0(r['real'])} vs {n0(r['prog'])} MWh "
                f"({signo(r['diff'])} MWh / {signo(p,1)+'%' if p is not None else '—'})")
    L = [f"📊 *PosDespacho vs Programa Semanal — {DIAS[d.weekday()].upper()} {d:%d/%m/%Y}*", '',
         f"• Generación Total real: {n1(c['total_gen'])} MWh",
         f"• Demanda SNI: {n1(c['dem_real'])} MWh real vs {n1(c['dem_prog'])} MWh programada ({signo(c['dem_real']-c['dem_prog'],1)})",
         f"• Demanda máxima: {c['dmax']:,.2f} MW a las {c['dmax_hora']}" if c['dmax'] else '',
         f"• POE: promedio {c['poe_prom']:.2f} US$/MWh · máx {c['poe_max']['poe']:.2f} ({c['poe_max']['gen']}) · mín {c['poe_min']['poe']:.2f} ({c['poe_min']['gen']})",
         f"• Chixoy: cota {c['chixoy'].get('cota', 0):,.2f} msnm · caudal entrante {c['chixoy'].get('q_prom', 0):.1f} m³/s (máx {c['chixoy'].get('q_max', 0):.1f} · mín {c['chixoy'].get('q_min', 0):.1f})",
         '', '*Por tecnología — mayores desviaciones (Real vs. Programado, MWh)*']
    L += [lt(r, TECH_NAME_POS.get(r['tech'], r['tech'])) for r in c['pos3']]
    L += ['']
    L += [lt(r, TECH_NAME_POS.get(r['tech'], r['tech'])) for r in c['neg3']]
    if c['chx_row']: L += [lt(c['chx_row'], 'Chixoy')]
    L += ['', '*Top 5 diferencias por planta*']
    for r in c['top_plants']:
        p = pct(r['real'], r['prog']) if r['prog'] > 0.5 else None
        L.append(f"{'📈' if r['diff'] > 0 else '📉'} {r['name']}: real {n1(r['real'])} / prog {n1(r['prog'])} MWh "
                 f"({signo(r['diff'],1)} MWh / {signo(p,1)+'%' if p is not None else '—'})")
    return '\n'.join(x for x in L if x is not None)
