"""Hoja diaria de control de zafra (uso interno). Estilo propio: oscuro, verde caña y ámbar."""
import html
from render import ASSETS

BG, PANEL, LINE, TXT, MUT, DIM = '#0F1A14', '#16251C', '#27392E', '#EEF3EA', '#93A598', '#5E7064'
CANA, CANA2, AMBAR, ROJO, AGUA = '#7CC36E', '#3E6B37', '#F0B429', '#EF5B4B', '#8FD3C1'
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']


def esc(s): return html.escape(str(s))
def fh(x): return f"{x.day:02d}-{MESES[x.month-1]} {x:%H:%M}"
def n0(x): return f"{x:,.0f}"


def fecha_larga(d):
    return f"{DIAS[d.weekday()]} {d.day} de {['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'][d.month-1]} {d.year}"


HEAD = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Zafra</title><style>
@font-face{{font-family:'Space Grotesk';src:url({ASSETS.as_uri()}/fonts/SpaceGrotesk.ttf);font-weight:300 700}}
@font-face{{font-family:'IBM Plex Mono';src:url({ASSETS.as_uri()}/fonts/IBMPlexMono-Regular.ttf);font-weight:400}}
@font-face{{font-family:'IBM Plex Mono';src:url({ASSETS.as_uri()}/fonts/IBMPlexMono-Medium.ttf);font-weight:500}}
@font-face{{font-family:'IBM Plex Mono';src:url({ASSETS.as_uri()}/fonts/IBMPlexMono-SemiBold.ttf);font-weight:600}}
body{{margin:0;background:{BG}}} .m{{font-family:'IBM Plex Mono',monospace}}
.sec{{font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:600;letter-spacing:.14em;color:{AMBAR};margin-bottom:12px}}
.card{{background:{PANEL};border:1px solid {LINE};border-radius:14px}}
table{{border-collapse:collapse;width:100%}}
th{{font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:500;color:{MUT};text-align:right;padding:0 8px 10px;letter-spacing:.04em;border-bottom:1px solid {LINE}}}
td{{white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:16px;text-align:right;padding:9px 8px;border-bottom:1px solid {LINE};color:{TXT}}}
th:first-child,td:first-child{{text-align:left;padding-left:0}}
</style></head><body>"""


def var_txt(v, dec=0):
    if v is None:
        return f'<span style="color:{DIM}">—</span>'
    if abs(v) < 0.0005:
        return f'<span style="color:{MUT}">= 0%</span>'
    col = CANA if v > 0 else (ROJO if v <= -0.15 else AMBAR)
    return f'<span style="color:{col};font-weight:600">{"▲" if v > 0 else "▼"} {abs(v)*100:.{dec}f}%</span>'


def fp_bar(fp):
    if fp is None:
        return '—'
    w = max(0, min(fp, 1.2)) / 1.2 * 92
    col = CANA if fp >= 0.75 else (AMBAR if fp >= 0.5 else ROJO)
    return (f'<div style="display:flex;align-items:center;gap:8px;justify-content:flex-end">'
            f'<div style="width:92px;height:8px;background:{LINE};border-radius:4px;position:relative">'
            f'<div style="position:absolute;left:0;top:0;height:8px;width:{w:.0f}px;background:{col};border-radius:4px"></div>'
            f'<div style="position:absolute;left:{92/1.2:.0f}px;top:-3px;width:1px;height:14px;background:{MUT}"></div></div>'
            f'<span style="color:{col};font-weight:600;min-width:52px">{fp*100:.0f}%</span></div>')


def kpi(label, valor, unidad, nota, color=TXT):
    return f"""<div class="card" style="flex:1;padding:18px 20px;display:flex;flex-direction:column;gap:8px">
 <div class="m" style="font-size:12px;letter-spacing:.1em;color:{MUT}">{esc(label)}</div>
 <div class="m" style="font-size:34px;font-weight:600;line-height:1;color:{color}">{valor}<span style="font-size:16px;color:{MUT};font-weight:500"> {unidad}</span></div>
 <div class="m" style="font-size:14px;color:{MUT}">{nota}</div></div>"""


ICONO = {'zafra': ('●', CANA), 'alta': ('■', ROJO), 'baja': ('▼', ROJO), 'fp': ('◆', AMBAR), 'cvg': ('$', AGUA)}


def alertas_html(al):
    if not al:
        return f'<div class="m" style="font-size:16px;color:{CANA}">✓ Sin alertas: ningún bloque bajó más de 15 % ni tuvo salidas forzadas.</div>'
    items = ''.join(f'<div style="display:flex;gap:12px;align-items:baseline"><span class="m" style="color:{ICONO[t][1]};font-weight:600;width:14px">{ICONO[t][0]}</span>'
                    f'<span style="font-size:17px;color:{TXT}">{esc(x)}</span></div>' for t, x in al)
    return f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px 28px">{items}</div>'


def tabla(filas):
    h = ('<tr><th>BLOQUE</th><th>CVG US$/MWh</th><th>ENERGÍA MWh</th><th>vs AYER</th><th>Pmax MW</th>'
         '<th>P. REAL MÁX</th><th>FACTOR DE PLANTA</th><th>ACUM. ZAFRA MWh</th><th>DÍAS</th></tr>')
    rows = ''
    for f in filas:
        if f['pendiente']:
            rows += (f'<tr style="opacity:.55"><td><b style="font-family:Space Grotesk;font-size:17px">{esc(f["bloque"])}</b>'
                     f'<div style="font-size:12px;color:{MUT}">{esc(f["nombre"])}</div></td>'
                     f'<td>{f["cvg"]:.2f}</td><td colspan="7" style="white-space:normal;text-align:left;color:{AMBAR}">CVG bajo, todavía sin arrancar (0 MWh)</td></tr>')
            continue
        cvg = '—' if f['cvg'] is None else f'{f["cvg"]:.2f}'
        if f['cvg'] is not None and f['cvg_ant'] is not None and abs(f['cvg'] - f['cvg_ant']) > 0.005:
            cvg = f'<span style="color:{AGUA};font-weight:600">{cvg}</span><div style="font-size:11px;color:{MUT}">antes {f["cvg_ant"]:.2f}</div>'
        nuevo = f'<span style="font-size:11px;color:{CANA};margin-left:6px">NUEVO</span>' if f['dias'] <= 1 else ''
        rows += (f'<tr><td><b style="font-family:Space Grotesk;font-size:17px">{esc(f["bloque"])}</b>{nuevo}'
                 f'<div style="font-size:12px;color:{MUT}">{esc(f["nombre"])} · desde {f["inicio"][8:]}-{MESES[int(f["inicio"][5:7])-1]}</div></td>'
                 f'<td>{cvg}</td><td style="font-weight:600">{n0(f["E"])}</td><td>{var_txt(f["var"])}</td>'
                 f'<td>{f["pmax"]:.1f}</td><td style="color:{MUT}">{f["p_real"]:.1f}</td><td>{fp_bar(f["fp"])}</td>'
                 f'<td>{n0(f["acum"])}</td><td style="color:{MUT}">{f["dias"]}</td></tr>')
    return f'<table>{h}{rows}</table>'


def grafica(serie, W=470, H=230):
    if not serie:
        return ''
    X0, X1, Y0, Y1 = 46, W - 6, 16, H - 28
    mx = max(max(s['plena'] for s in serie), 1) * 1.08
    n = len(serie); bw = (X1 - X0) / n
    sy = lambda v: Y1 - (Y1 - Y0) * v / mx
    g = []
    for t in range(0, int(mx) + 1, 2000 if mx > 6000 else 1000):
        g.append(f'<line x1="{X0}" y1="{sy(t):.1f}" x2="{X1}" y2="{sy(t):.1f}" stroke="{LINE}"/>'
                 f'<text x="{X0-6}" y="{sy(t)+4:.1f}" text-anchor="end" font-size="11" fill="{MUT}" font-family="IBM Plex Mono">{t/1000:.0f}k</text>')
    pts = []
    for i, s in enumerate(serie):
        x = X0 + bw * i + bw * 0.15
        ant = serie[i - 1]['E'] if i else None
        col = ROJO if (ant and s['E'] < ant * 0.9) else (CANA if i == n - 1 else CANA2)
        g.append(f'<rect x="{x:.1f}" y="{sy(s["E"]):.1f}" width="{bw*0.7:.1f}" height="{Y1-sy(s["E"]):.1f}" fill="{col}" rx="2"/>')
        pts.append(f'{X0 + bw * i + bw / 2:.1f},{sy(s["plena"]):.1f}')
        if i % max(1, n // 6) == 0 or i == n - 1:
            g.append(f'<text x="{X0 + bw*i + bw/2:.1f}" y="{H-8}" text-anchor="middle" font-size="11" fill="{MUT}" font-family="IBM Plex Mono">{s["d"].day}</text>')
    g.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{AMBAR}" stroke-width="2" stroke-dasharray="4 3"/>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(g)}</svg>'


def salidas_html(sal, rso):
    if not sal and not rso:
        return f'<div style="font-size:16px;color:{CANA}">✓ Sin salidas ni fallas de los ingenios ese día.</div>'
    out = ''
    for s in sal:
        col = AMBAR if s['tipo'] == 'Mantenimiento' else ROJO
        ent = fh(s['entra']) if s['entra'] else 'sin hora de entrada'
        out += (f'<div style="display:flex;flex-direction:column;gap:2px;padding:8px 0;border-bottom:1px solid {LINE}">'
                f'<div><b class="m" style="color:{col}">{esc(s["bloque"])}</b> <span style="color:{TXT};font-size:16px">{esc(s["tipo"])}</span>'
                f' <span class="m" style="color:{MUT};font-size:13px">{fh(s["sale"])} → {esc(ent)}</span></div>'
                f'<div style="font-size:14px;color:{MUT}">{esc(s["obs"] or s["motivo"])}</div></div>')
    for t in rso[:4]:
        out += (f'<div style="padding:8px 0;border-bottom:1px solid {LINE};font-size:14px;color:{TXT}">'
                f'<span class="m" style="color:{AGUA};font-size:12px">RSO · </span>{esc(t[:220])}</div>')
    return out


def build_zafra(r, temporada):
    d, t = r['d'], r['tot']
    fp_dia = t['E'] / t['plena_dia'] if t['plena_dia'] else 0
    fp_acum = t['acum'] / t['plena_acum'] if t['plena_acum'] else 0
    var = (t['E'] - t['E_ant']) / t['E_ant'] if t['E_ant'] else None
    var_s = var_txt(var, 1) + ' vs ayer' if var is not None else ''
    pend = ', '.join(f['bloque'] for f in r['pendientes'])
    ini = t['inicio']
    k = (kpi('ENERGÍA DEL DÍA', n0(t['E']), 'MWh', var_s)
         + kpi('FACTOR DE PLANTA DEL DÍA', f'{fp_dia*100:.1f}', '%', f'plena carga {n0(t["plena_dia"])} MWh',
               CANA if fp_dia >= .75 else AMBAR if fp_dia >= .5 else ROJO)
         + kpi('ACUMULADO EN ZAFRA', f'{t["acum"]/1000:,.2f}', 'GWh', f'{fp_acum*100:.1f} % de plena carga · {t["dias"]} días')
         + kpi('BLOQUES EN ZAFRA', str(t['n_zafra']), '', f'pendiente: {esc(pend)}' if pend else 'ninguno pendiente'))
    body = f"""
<div id="page" style="width:1080px;box-sizing:border-box;background:{BG};color:{TXT};font-family:'Space Grotesk',sans-serif;padding:40px 44px 30px;display:flex;flex-direction:column;gap:22px">
 <div style="display:flex;justify-content:space-between;align-items:flex-end">
  <div style="display:flex;flex-direction:column;gap:8px">
   <div class="m" style="font-size:15px;letter-spacing:.16em;color:{AMBAR}">CONTROL DIARIO · ZAFRA {esc(temporada)}</div>
   <div style="font-size:42px;font-weight:700;letter-spacing:-.02em;line-height:1.05">Ingenios · {fecha_larga(d)}</div>
   <div style="font-size:18px;color:{MUT}">Día {r['dia_n']} de zafra · inició el {ini.day} de {MESES[ini.month-1]} · energía real del posdespacho AMM</div>
  </div>
  <div class="m" style="font-size:12px;color:{CANA};border:1px solid {CANA2};border-radius:20px;padding:6px 14px;letter-spacing:.1em">USO INTERNO</div>
 </div>
 <div style="height:4px;background:linear-gradient(90deg,{CANA} 0 70%,{AMBAR} 70% 100%);border-radius:2px"></div>
 <div style="display:flex;gap:14px">{k}</div>
 <div class="card" style="padding:18px 22px;border-color:{'#5a2a24' if any(a[0] in ('alta','baja') for a in r['alertas']) else LINE}">
  <div class="sec">ALERTAS DEL DÍA</div>{alertas_html(r['alertas'])}</div>
 <div class="card" style="padding:18px 22px">
  <div class="sec">CONTROL POR BLOQUE</div>{tabla(r['filas'])}
  <div class="m" style="font-size:12px;color:{MUT};margin-top:10px">Factor de planta = energía ÷ (Pmax × 24 h); la raya marca 100 %. Rojo: baja ≥ 15 % vs ayer o FP &lt; 50 %.</div></div>
 <div style="display:flex;gap:14px">
  <div class="card" style="flex:1.05;padding:18px 22px"><div class="sec">SALIDAS Y FALLAS</div>{salidas_html(r['salidas'], r['rso'])}</div>
  <div class="card" style="flex:1;padding:18px 22px"><div class="sec">ENERGÍA DIARIA EN ZAFRA</div>{grafica(r['serie'])}
   <div class="m" style="font-size:12px;color:{MUT};display:flex;gap:16px"><span><span style="color:{CANA}">■</span> energía MWh</span><span><span style="color:{ROJO}">■</span> baja ≥ 10 %</span><span><span style="color:{AMBAR}">- -</span> plena carga</span></div></div>
 </div>
 <div class="m" style="font-size:12px;color:{DIM};display:flex;justify-content:space-between">
  <span>FUENTE · AMM: posdespacho diario (carga horaria, indisponibilidades, RSO) y programa semanal vigente (CVG)</span><span>Pmax: predespacho diario</span></div>
</div></body></html>"""
    return HEAD + body


def texto_zafra(r, temporada):
    d, t = r['d'], r['tot']
    fp_acum = t['acum'] / t['plena_acum'] if t['plena_acum'] else 0
    var = (t['E'] - t['E_ant']) / t['E_ant'] * 100 if t['E_ant'] else None
    s = (f"🌾 *Control de zafra {temporada} · {d.day} {MESES[d.month-1]} {d.year}* (día {r['dia_n']})\n"
         f"• Energía del día: {t['E']:,.0f} MWh" + (f" ({'+' if var >= 0 else '−'}{abs(var):.1f} % vs ayer)" if var is not None else '') + "\n"
         f"• Acumulado en zafra: {t['acum']/1000:,.2f} GWh · {fp_acum*100:.1f} % de plena carga · {t['n_zafra']} bloques\n")
    graves = [x for k, x in r['alertas'] if k in ('zafra', 'alta', 'baja')]
    if graves:
        s += '⚠️ ' + ' · '.join(graves[:6]) + '\n'
    else:
        s += '✅ Sin bajas fuertes ni salidas forzadas.\n'
    return s + '_Fuente: AMM._'
