"""Imagen (línea gráfica ER) del PosDespacho diario vs programa semanal."""
from render import (frame, kpi, var_html, esc, n0, n1, MESES, TECH_NAME,
                    BLUE, GOLD, NAVY, G2, G3, GRID, DIV, CTX)
from parse_pds import pct

DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
TECH_NAME_POS = {**TECH_NAME, 'MEX': 'Importación oportunidad México'}


def fecha_larga(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month-1]} {d.year}"


def signo(x, dec=0):
    f = f"{abs(x):,.{dec}f}"
    return ('+' if x >= 0 else '−') + f


def poe_chart(poe, W=936, H=210):
    if not poe: return ''
    vals = [p['poe'] for p in poe]
    lo, hi = 0, max(vals) * 1.18
    X0, X1, Y0, Y1 = 46, W - 10, 18, H - 30
    sx = lambda i: X0 + (X1 - X0) * (i + 0.5) / len(vals)
    sy = lambda v: Y1 - (Y1 - Y0) * (v - lo) / (hi - lo)
    step = 50 if hi > 150 else 25
    g = []
    for t in range(0, int(hi) + 1, step):
        g.append(f'<line x1="{X0}" y1="{sy(t):.1f}" x2="{X1}" y2="{sy(t):.1f}" stroke="{GRID}"/>'
                 f'<text x="{X0-8}" y="{sy(t)+5:.1f}" text-anchor="end" font-size="13" fill="{G3}" font-family="IBM Plex Mono">{t}</text>')
    bw = (X1 - X0) / len(vals) * 0.72
    imax = vals.index(max(vals)); imin = vals.index(min(vals))
    for i, v in enumerate(vals):
        col = GOLD if i == imax else (BLUE if i == imin else '#9DBEF8')
        g.append(f'<rect x="{sx(i)-bw/2:.1f}" y="{sy(v):.1f}" width="{bw:.1f}" height="{Y1-sy(v):.1f}" fill="{col}"/>')
    avg = sum(vals) / len(vals)
    g.append(f'<line x1="{X0}" y1="{sy(avg):.1f}" x2="{X1}" y2="{sy(avg):.1f}" stroke="{NAVY}" stroke-dasharray="5 4" stroke-width="1.5"/>')
    g.append(f'<rect x="{X0+4}" y="{sy(avg)-22:.1f}" width="118" height="18" fill="#fff"/>'
             f'<text x="{X0+8}" y="{sy(avg)-8:.1f}" font-size="13" fill="{NAVY}" font-family="IBM Plex Mono">prom. {avg:.2f}</text>')
    pm, pn = poe[imax], poe[imin]
    ax = min(max(sx(imax), X0 + 120), X1 - 120)
    g.append(f'<text x="{ax:.1f}" y="{sy(vals[imax])-8:.1f}" text-anchor="middle" font-size="13" font-weight="600" fill="{NAVY}" font-family="IBM Plex Mono">{vals[imax]:.2f} · {esc(pm["gen"])}</text>')
    ay = sy(vals[imin]) - 8
    nx = min(max(sx(imin), X0 + 120), X1 - 120)
    g.append(f'<text x="{nx:.1f}" y="{ay:.1f}" text-anchor="middle" font-size="13" font-weight="600" fill="{BLUE}" font-family="IBM Plex Mono">{vals[imin]:.2f} · {esc(pn["gen"])}</text>')
    for i in range(0, len(vals), 3):
        g.append(f'<text x="{sx(i):.1f}" y="{H-8}" text-anchor="middle" font-size="12" fill="{G3}" font-family="IBM Plex Mono">{poe[i]["de"][:2]}h</text>')
    g.append(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="{NAVY}" stroke-width="2"/>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(g)}</svg>'


def diverging(rows, label_key, maxabs, show_vals=True):
    """Barras divergentes: positivas (real > programado) en azul a la derecha, negativas en gris a la izquierda."""
    out = ''
    for r in rows:
        d = r['diff']; w = abs(d) / maxabs * 50 if maxabs else 0
        p = pct(r['real'], r['prog']) if r['prog'] > 0.5 else None
        ptxt = f"{signo(p,1)}%" if p is not None else '—'
        bar = (f'<div style="position:absolute;left:50%;width:{w:.1f}%;height:10px;background:{BLUE}"></div>' if d > 0 else
               f'<div style="position:absolute;right:50%;width:{w:.1f}%;height:10px;background:{CTX}"></div>')
        out += f"""<div style="margin-bottom:11px">
<div style="display:flex;justify-content:space-between;font-size:15px;gap:10px"><span>{esc(r[label_key])}</span>
<span class="mono" style="font-weight:600;color:{BLUE if d>0 else G2};white-space:nowrap">{signo(d,0)} MWh <span style="font-weight:400;font-size:12px">{ptxt}</span></span></div>
<div style="position:relative;height:10px;background:{GRID};margin-top:4px">{bar}<div style="position:absolute;left:50%;top:-3px;width:2px;height:16px;background:{NAVY}"></div></div>
{f'<div class="mono" style="font-size:12px;color:{G3};margin-top:3px">real {n0(r["real"])} · prog {n0(r["prog"])}</div>' if show_vals else ''}
</div>"""
    return out


def build_pos(c):
    d = c['date']
    dp = pct(c['dem_real'], c['dem_prog'])
    title = (f"{DIAS[d.weekday()].capitalize()} {d.day} {MESES[d.month-1]}: demanda "
             f"{abs(dp):.1f}% {'bajo' if dp < 0 else 'sobre'} lo programado")
    subtitle = f"PosDespacho vs programa semanal (sem. {c['week']}) · {fecha_larga(d)}"

    kp = ''.join([
        kpi('GENERACIÓN TOTAL REAL', n0(c['total_gen']), 'MWh', ''),
        kpi('DEMANDA SNI', n0(c['dem_real']), 'MWh',
            f'<span style="font-size:13px;color:{G2}">prog {n0(c["dem_prog"])} · </span>{var_html(dp, 13)}'),
        kpi('DEMANDA MÁXIMA', n0(c['dmax']) if c['dmax'] else '—', 'MW',
            f'<span style="font-size:14px;color:{G2}">a las {c["dmax_hora"] or "—"}</span>'),
        kpi('POE PROMEDIO', f"{c['poe_prom']:.2f}" if c['poe_prom'] else '—', 'US$/MWh', ''),
    ])
    poe = f"""<div><div class="sec">PRECIO DE OPORTUNIDAD (POE) POR HORA · US$/MWh</div>{poe_chart(c['poe'])}</div>"""

    trows = [{**r, 'name': TECH_NAME_POS.get(r['tech'], r['tech'])} for r in c['pos3'] + c['neg3']]
    allr = trows + ([{**c['chx_row'], 'name': 'Chixoy'}] if c['chx_row'] else [])
    mx = max((abs(r['diff']) for r in allr), default=1)
    tech = f"""<div style="flex:1"><div class="sec">POR TECNOLOGÍA · REAL VS PROGRAMADO</div>
{diverging(trows, 'name', mx)}
{f'<div style="border-top:1px dashed {DIV};padding-top:10px;margin-top:4px">' + diverging([{**c["chx_row"], "name": "Chixoy"}], "name", mx) + '</div>' if c['chx_row'] else ''}
</div>"""

    ch = c['chixoy']; cr = c['chx_row']
    chx = f"""<div style="flex:0.8"><div class="sec">CHIXOY</div>
<div class="mono" style="display:flex;flex-direction:column;gap:18px">
 <div><div style="font-size:13px;color:{G2}">COTA DEL EMBALSE</div><div style="font-size:30px;font-weight:600">{ch.get('cota', 0):,.2f}<span style="font-size:15px;color:{G2}"> msnm</span></div></div>
 <div><div style="font-size:13px;color:{G2}">CAUDAL ENTRANTE</div><div style="font-size:30px;font-weight:600">{ch.get('q_prom') or ch.get('q_ent') or 0:,.1f}<span style="font-size:15px;color:{G2}"> m³/s</span></div>
  <div style="font-size:13px;color:{G2}">máx {ch.get('q_max', 0):,.1f} · mín {ch.get('q_min', 0):,.1f}</div></div>
 {f'<div><div style="font-size:13px;color:{G2}">ENERGÍA REAL VS PROG.</div><div style="font-size:22px;font-weight:600">{n0(cr["real"])} <span style="color:{G3}">/</span> {n0(cr["prog"])}<span style="font-size:14px;color:{G2}"> MWh</span></div>{var_html(pct(cr["real"], cr["prog"]), 14)}</div>' if cr else ''}
</div></div>"""

    mxp = max((abs(r['diff']) for r in c['top_plants']), default=1)
    plants = f"""<div><div class="sec">TOP 5 DIFERENCIAS POR PLANTA · REAL VS PROGRAMADO</div>
<div style="display:grid;grid-template-columns:1fr 1fr;column-gap:48px">{diverging(c['top_plants'], 'name', mxp)}</div>
<div class="mono" style="font-size:12px;color:{G3}">Cascadas, bloques y unidades sumados como una sola planta (p. ej. Renace I–IV, INDE, Xacbal + Delta).</div></div>"""

    body = f"""<div style="display:flex;gap:24px">{kp}</div>{poe}
<div style="display:flex;gap:48px">{tech}{chx}</div>{plants}"""
    return frame('MERCADO MAYORISTA · POSDESPACHO DIARIO', title, subtitle, body,
                 f"AMM · PosDespacho {d:%d/%m/%Y} · sem. {c['week']}", 1500)


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
