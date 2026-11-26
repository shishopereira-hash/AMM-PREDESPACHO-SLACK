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
.sec{{font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:600;letter-spacing:.14em;color:{AMBAR};margin-bottom:16px}}
.card{{background:{PANEL};border:1px solid {LINE};border-radius:18px}}
table{{border-collapse:collapse;width:100%}}
th{{font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:500;color:{MUT};text-align:right;vertical-align:bottom;padding:0 8px 14px;letter-spacing:.04em;border-bottom:1px solid {LINE}}}
td{{white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:26px;text-align:right;vertical-align:middle;padding:18px 8px;border-bottom:1px solid {LINE};color:{TXT}}}
th:first-child,td:first-child{{text-align:left;padding-left:0}}
</style></head><body>"""


def var_txt(v, dec=0):
    if v is None:
        return f'<span style="color:{DIM}">—</span>'
    if abs(v) < 0.5 * 10 ** -(dec + 2):
        return f'<span style="color:{MUT}">= 0%</span>'
    col = CANA if v > 0 else (ROJO if v <= -0.15 else AMBAR)
    return f'<span style="color:{col};font-weight:600">{"▲" if v > 0 else "▼"} {abs(v)*100:.{dec}f}%</span>'


def fp_cell(fp):
    if fp is None:
        return '—'
    w = max(0, min(fp, 1.2)) / 1.2 * 150
    col = CANA if fp >= 0.75 else (AMBAR if fp >= 0.5 else ROJO)
    return (f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px">'
            f'<span style="color:{col};font-weight:600;font-size:30px">{fp*100:.0f}%</span>'
            f'<div style="width:150px;height:12px;background:{LINE};border-radius:6px;position:relative">'
            f'<div style="position:absolute;left:0;top:0;height:12px;width:{w:.0f}px;background:{col};border-radius:6px"></div>'
            f'<div style="position:absolute;left:{150/1.2:.0f}px;top:-4px;width:2px;height:20px;background:{MUT}"></div></div></div>')


def kpi(label, valor, unidad, nota, color=TXT):
    return f"""<div class="card" style="padding:24px 26px;display:flex;flex-direction:column;gap:10px">
 <div class="m" style="font-size:20px;letter-spacing:.08em;color:{MUT}">{esc(label)}</div>
 <div class="m" style="font-size:60px;font-weight:600;line-height:1;color:{color}">{valor}<span style="font-size:26px;color:{MUT};font-weight:500"> {unidad}</span></div>
 <div class="m" style="font-size:22px;color:{MUT}">{nota}</div></div>"""


ICONO = {'zafra': ('●', CANA), 'alta': ('■', ROJO), 'baja': ('▼', ROJO), 'fp': ('◆', AMBAR), 'cvg': ('$', AGUA)}


def alertas_html(al):
    if not al:
        return f'<div style="font-size:28px;color:{CANA}">✓ Sin alertas: ningún bloque bajó más de 15 % ni tuvo salidas forzadas.</div>'
    return ''.join(f'<div style="display:flex;gap:16px;align-items:baseline;padding:6px 0"><span class="m" style="color:{ICONO[t][1]};font-weight:600;width:24px;font-size:26px">{ICONO[t][0]}</span>'
                   f'<span style="font-size:29px;line-height:1.3;color:{TXT}">{esc(x)}</span></div>' for t, x in al)


def tabla(filas):
    h = ('<tr><th>BLOQUE</th><th>ENERGÍA MWh<br>vs ayer</th><th>FACTOR<br>DE PLANTA</th><th>ACUM. ZAFRA<br>MWh · días</th></tr>')
    rows = ''
    for f in filas:
        if f['pendiente']:
            rows += (f'<tr style="opacity:.6"><td><b style="font-family:Space Grotesk;font-size:32px">{esc(f["bloque"])}</b>'
                     f'<div style="font-size:20px;color:{MUT};margin-top:4px">{esc(f["nombre"])} · CVG {f["cvg"]:.2f}</div></td>'
                     f'<td colspan="3" style="white-space:normal;text-align:left;color:{AMBAR};font-size:26px">CVG bajo, todavía sin arrancar (0 MWh)</td></tr>')
            continue
        cvg = '—' if f['cvg'] is None else f'{f["cvg"]:.2f}'
        if f['cvg'] is not None and f['cvg_ant'] is not None and abs(f['cvg'] - f['cvg_ant']) > 0.005:
            cvg = f'<span style="color:{AGUA};font-weight:600">{f["cvg_ant"]:.2f}→{cvg}</span>'
        nuevo = f'<span style="font-size:18px;color:{CANA};margin-left:8px">NUEVO</span>' if f['dias'] <= 1 else ''
        ini = f'{f["inicio"][8:]}-{MESES[int(f["inicio"][5:7])-1]}'
        rows += (f'<tr><td><b style="font-family:Space Grotesk;font-size:32px">{esc(f["bloque"])}</b>{nuevo}'
                 f'<div style="font-size:20px;color:{MUT};margin-top:4px;line-height:1.35">{esc(f["nombre"])} · desde {ini}<br>'
                 f'CVG {cvg} · Pmax {f["pmax"]:.1f} MW · real {f["p_real"]:.1f}</div></td>'
                 f'<td><div style="font-size:32px;font-weight:600">{n0(f["E"])}</div><div style="font-size:24px;margin-top:6px">{var_txt(f["var"])}</div></td>'
                 f'<td>{fp_cell(f["fp"])}</td>'
                 f'<td><div style="font-size:28px">{n0(f["acum"])}</div><div style="font-size:22px;color:{MUT};margin-top:6px">{f["dias"]} días</div></td></tr>')
    return f'<table>{h}{rows}</table>'


def grafica(serie, W=932, H=380):
    if not serie:
        return ''
    X0, X1, Y0, Y1 = 70, W - 6, 20, H - 44
    mx = max(max(s['plena'] for s in serie), 1) * 1.08
    n = len(serie); bw = (X1 - X0) / n
    sy = lambda v: Y1 - (Y1 - Y0) * v / mx
    g = []
    for t in range(0, int(mx) + 1, 2000 if mx > 6000 else 1000):
        g.append(f'<line x1="{X0}" y1="{sy(t):.1f}" x2="{X1}" y2="{sy(t):.1f}" stroke="{LINE}"/>'
                 f'<text x="{X0-10}" y="{sy(t)+7:.1f}" text-anchor="end" font-size="20" fill="{MUT}" font-family="IBM Plex Mono">{t/1000:.0f}k</text>')
    pts = []
    for i, s in enumerate(serie):
        x = X0 + bw * i + bw * 0.15
        ant = serie[i - 1]['E'] if i else None
        col = ROJO if (ant and s['E'] < ant * 0.9) else (CANA if i == n - 1 else CANA2)
        g.append(f'<rect x="{x:.1f}" y="{sy(s["E"]):.1f}" width="{bw*0.7:.1f}" height="{Y1-sy(s["E"]):.1f}" fill="{col}" rx="3"/>')
        pts.append(f'{X0 + bw * i + bw / 2:.1f},{sy(s["plena"]):.1f}')
        if i % max(1, n // 7) == 0 or i == n - 1:
            g.append(f'<text x="{X0 + bw*i + bw/2:.1f}" y="{H-10}" text-anchor="middle" font-size="20" fill="{MUT}" font-family="IBM Plex Mono">{s["d"].day}</text>')
    g.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{AMBAR}" stroke-width="3" stroke-dasharray="7 5"/>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(g)}</svg>'


def salidas_html(sal, rso):
    if not sal and not rso:
        return f'<div style="font-size:28px;color:{CANA}">✓ Sin salidas ni fallas de los ingenios ese día.</div>'
    out = ''
    for s in sal:
        col = AMBAR if s['tipo'] == 'Mantenimiento' else ROJO
        ent = fh(s['entra']) if s['entra'] else 'sin hora de entrada'
        out += (f'<div style="display:flex;flex-direction:column;gap:6px;padding:14px 0;border-bottom:1px solid {LINE}">'
                f'<div><b class="m" style="color:{col};font-size:28px">{esc(s["bloque"])}</b> <span style="color:{TXT};font-size:28px">{esc(s["tipo"])}</span></div>'
                f'<div class="m" style="color:{MUT};font-size:22px">{fh(s["sale"])} → {esc(ent)}</div>'
                f'<div style="font-size:24px;color:{MUT}">{esc(s["obs"] or s["motivo"])}</div></div>')
    for t in rso[:4]:
        out += (f'<div style="padding:14px 0;border-bottom:1px solid {LINE};font-size:24px;line-height:1.35;color:{TXT}">'
                f'<span class="m" style="color:{AGUA};font-size:20px">RSO · </span>{esc(t[:260])}</div>')
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
         + kpi('FACTOR DE PLANTA', f'{fp_dia*100:.1f}', '%', f'plena carga {n0(t["plena_dia"])} MWh',
               CANA if fp_dia >= .75 else AMBAR if fp_dia >= .5 else ROJO)
         + kpi('ACUMULADO ZAFRA', f'{t["acum"]/1000:,.2f}', 'GWh', f'{fp_acum*100:.1f} % plena carga · {t["dias"]} días')
         + kpi('BLOQUES EN ZAFRA', str(t['n_zafra']), '', f'pendiente: {esc(pend)}' if pend else 'ninguno pendiente'))
    hay_rojo = any(a[0] in ('alta', 'baja') for a in r['alertas'])
    body = f"""
<div id="page" style="width:1080px;box-sizing:border-box;background:{BG};color:{TXT};font-family:'Space Grotesk',sans-serif;padding:48px 44px 36px;display:flex;flex-direction:column;gap:28px">
 <div style="display:flex;flex-direction:column;gap:12px">
  <div style="display:flex;justify-content:space-between;align-items:center">
   <div class="m" style="font-size:22px;letter-spacing:.14em;color:{AMBAR}">CONTROL DIARIO · ZAFRA {esc(temporada)}</div>
   <div class="m" style="font-size:18px;color:{CANA};border:2px solid {CANA2};border-radius:24px;padding:6px 16px;letter-spacing:.1em">USO INTERNO</div>
  </div>
  <div style="font-size:58px;font-weight:700;letter-spacing:-.02em;line-height:1.05">Ingenios<br>{fecha_larga(d)}</div>
  <div style="font-size:26px;color:{MUT}">Día {r['dia_n']} de zafra · inició el {ini.day} de {MESES[ini.month-1]}</div>
 </div>
 <div style="height:6px;background:linear-gradient(90deg,{CANA} 0 70%,{AMBAR} 70% 100%);border-radius:3px"></div>
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px">{k}</div>
 <div class="card" style="padding:26px 28px;border-color:{'#6b2f27' if hay_rojo else LINE}">
  <div class="sec">ALERTAS DEL DÍA</div>{alertas_html(r['alertas'])}</div>
 <div class="card" style="padding:26px 28px">
  <div class="sec">CONTROL POR BLOQUE</div>{tabla(r['filas'])}
  <div style="font-size:20px;color:{MUT};margin-top:14px;line-height:1.4">Factor de planta = energía ÷ (Pmax × 24 h); la raya marca 100 %. Rojo: baja ≥ 15 % vs ayer o FP &lt; 50 %. CVG en US$/MWh.</div></div>
 <div class="card" style="padding:26px 28px"><div class="sec">SALIDAS Y FALLAS</div>{salidas_html(r['salidas'], r['rso'])}</div>
 <div class="card" style="padding:26px 28px"><div class="sec">ENERGÍA DIARIA EN ZAFRA</div>{grafica(r['serie'])}
  <div class="m" style="font-size:20px;color:{MUT};display:flex;gap:28px;margin-top:8px"><span><span style="color:{CANA}">■</span> energía MWh</span><span><span style="color:{ROJO}">■</span> baja ≥ 10 %</span><span><span style="color:{AMBAR}">- -</span> plena carga</span></div></div>
 <div style="font-size:19px;color:{DIM};line-height:1.4">Fuente: AMM — posdespacho diario (carga horaria, indisponibilidades, RSO) y programa semanal vigente (CVG). Pmax del predespacho diario.</div>
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
