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
.sec{{font-family:'IBM Plex Mono',monospace;font-size:19px;font-weight:600;letter-spacing:.14em;color:{AMBAR};margin-bottom:14px}}
.card{{background:{PANEL};border:1px solid {LINE};border-radius:14px}}
table{{border-collapse:collapse;width:100%}}
th{{font-family:'IBM Plex Mono',monospace;font-size:15px;font-weight:500;color:{MUT};text-align:right;vertical-align:bottom;padding:0 6px 12px;letter-spacing:.04em;border-bottom:1px solid {LINE}}}
td{{white-space:nowrap;font-family:'IBM Plex Mono',monospace;font-size:22px;text-align:right;vertical-align:middle;padding:12px 6px;border-bottom:1px solid {LINE};color:{TXT}}}
th:first-child,td:first-child{{text-align:left;padding-left:0}}
</style></head><body>"""


def var_txt(v, dec=0):
    if v is None:
        return f'<span style="color:{DIM}">—</span>'
    if abs(v) < 0.5 * 10 ** -(dec + 2):
        return f'<span style="color:{MUT}">= 0%</span>'
    col = CANA if v > 0 else (ROJO if v <= -0.15 else AMBAR)
    return f'<span style="color:{col};font-weight:600">{"▲" if v > 0 else "▼"} {abs(v)*100:.{dec}f}%</span>'


def fp_bar(fp):
    if fp is None:
        return '—'
    w = max(0, min(fp, 1.2)) / 1.2 * 72
    col = CANA if fp >= 0.75 else (AMBAR if fp >= 0.5 else ROJO)
    return (f'<div style="display:flex;align-items:center;gap:8px;justify-content:flex-end">'
            f'<div style="width:72px;height:10px;background:{LINE};border-radius:4px;position:relative">'
            f'<div style="position:absolute;left:0;top:0;height:10px;width:{w:.0f}px;background:{col};border-radius:4px"></div>'
            f'<div style="position:absolute;left:{72/1.2:.0f}px;top:-4px;width:2px;height:18px;background:{MUT}"></div></div>'
            f'<span style="color:{col};font-weight:600;min-width:62px">{fp*100:.0f}%</span></div>')


def kpi(label, valor, unidad, nota, color=TXT):
    return f"""<div class="card" style="flex:1;padding:20px 20px;display:flex;flex-direction:column;gap:10px">
 <div class="m" style="font-size:16px;letter-spacing:.06em;color:{MUT}">{esc(label)}</div>
 <div class="m" style="font-size:46px;font-weight:600;line-height:1;color:{color}">{valor}<span style="font-size:20px;color:{MUT};font-weight:500"> {unidad}</span></div>
 <div class="m" style="font-size:18px;color:{MUT};line-height:1.3">{nota}</div></div>"""


ICONO = {'zafra': ('●', CANA), 'alta': ('■', ROJO), 'baja': ('▼', ROJO), 'fp': ('◆', AMBAR), 'cvg': ('$', AGUA)}


def alertas_html(al):
    if not al:
        return f'<div class="m" style="font-size:23px;color:{CANA}">✓ Sin alertas: ningún bloque bajó más de 15 % ni tuvo salidas forzadas.</div>'
    items = ''.join(f'<div style="display:flex;gap:12px;align-items:baseline"><span class="m" style="color:{ICONO[t][1]};font-weight:600;width:20px;font-size:21px">{ICONO[t][0]}</span>'
                    f'<span style="font-size:23px;line-height:1.3;color:{TXT}">{esc(x)}</span></div>' for t, x in al)
    return f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px 28px">{items}</div>'


def tabla(filas):
    h = ('<tr><th>BLOQUE</th><th>CVG<br>US$/MWh</th><th>ENERGÍA<br>MWh</th><th>vs<br>AYER</th><th>Pmax<br>MW</th>'
         '<th>P. REAL<br>MÁX MW</th><th>FACTOR<br>DE PLANTA</th><th>ACUM.<br>ZAFRA MWh</th><th>DÍAS</th></tr>')
    rows = ''
    for f in filas:
        if f['pendiente']:
            rows += (f'<tr style="opacity:.6"><td><b style="font-family:Space Grotesk;font-size:24px">{esc(f["bloque"])}</b>'
                     f'<div style="font-size:15px;color:{MUT}">{esc(f["nombre"])}</div></td>'
                     f'<td>{f["cvg"]:.2f}</td><td colspan="7" style="white-space:normal;text-align:left;font-size:21px;color:{AMBAR}">CVG bajo, todavía sin arrancar (0 MWh)</td></tr>')
            continue
        cvg = '—' if f['cvg'] is None else f'{f["cvg"]:.2f}'
        if f['cvg'] is not None and f['cvg_ant'] is not None and abs(f['cvg'] - f['cvg_ant']) > 0.005:
            cvg = f'<span style="color:{AGUA};font-weight:600">{cvg}</span><div style="font-size:15px;color:{MUT}">antes {f["cvg_ant"]:.2f}</div>'
        nuevo = f'<span style="font-size:14px;color:{CANA};margin-left:6px">NUEVO</span>' if f['dias'] <= 1 else ''
        rows += (f'<tr><td><b style="font-family:Space Grotesk;font-size:24px">{esc(f["bloque"])}</b>{nuevo}'
                 f'<div style="font-size:15px;color:{MUT}">{esc(f["nombre"])}</div></td>'
                 f'<td>{cvg}</td><td style="font-weight:600">{n0(f["E"])}</td><td>{var_txt(f["var"])}</td>'
                 f'<td>{f["pmax"]:.1f}</td><td style="color:{MUT}">{f["p_real"]:.1f}</td><td>{fp_bar(f["fp"])}</td>'
                 f'<td>{n0(f["acum"])}</td><td style="color:{MUT}">{f["dias"]}<div style="font-size:14px">desde {f["inicio"][8:]}-{MESES[int(f["inicio"][5:7])-1]}</div></td></tr>')
    return f'<table>{h}{rows}</table>'


def grafica(serie, W=470, H=300):
    if not serie:
        return ''
    X0, X1, Y0, Y1 = 56, W - 6, 16, H - 34
    mx = max(max(s['plena'] for s in serie), 1) * 1.08
    n = len(serie); bw = (X1 - X0) / n
    sy = lambda v: Y1 - (Y1 - Y0) * v / mx
    g = []
    for t in range(0, int(mx) + 1, 2000 if mx > 6000 else 1000):
        g.append(f'<line x1="{X0}" y1="{sy(t):.1f}" x2="{X1}" y2="{sy(t):.1f}" stroke="{LINE}"/>'
                 f'<text x="{X0-6}" y="{sy(t)+4:.1f}" text-anchor="end" font-size="16" fill="{MUT}" font-family="IBM Plex Mono">{t/1000:.0f}k</text>')
    pts = []
    for i, s in enumerate(serie):
        x = X0 + bw * i + bw * 0.15
        ant = serie[i - 1]['E'] if i else None
        col = ROJO if (ant and s['E'] < ant * 0.9) else (CANA if i == n - 1 else CANA2)
        g.append(f'<rect x="{x:.1f}" y="{sy(s["E"]):.1f}" width="{bw*0.7:.1f}" height="{Y1-sy(s["E"]):.1f}" fill="{col}" rx="2"/>')
        pts.append(f'{X0 + bw * i + bw / 2:.1f},{sy(s["plena"]):.1f}')
        paso = max(1, n // 6)
        if (i % paso == 0 and n - 1 - i >= max(2, paso // 2)) or i == n - 1:
            g.append(f'<text x="{X0 + bw*i + bw/2:.1f}" y="{H-8}" text-anchor="middle" font-size="16" fill="{MUT}" font-family="IBM Plex Mono">{s["d"].day}</text>')
    g.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{AMBAR}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(g)}</svg>'


def salidas_html(sal, rso):
    if not sal and not rso:
        return f'<div style="font-size:22px;color:{CANA}">✓ Sin salidas ni fallas de los ingenios ese día.</div>'
    out = ''
    for s in sal:
        col = AMBAR if s['tipo'] == 'Mantenimiento' else ROJO
        ent = fh(s['entra']) if s['entra'] else 'sin hora de entrada'
        out += (f'<div style="display:flex;flex-direction:column;gap:4px;padding:10px 0;border-bottom:1px solid {LINE}">'
                f'<div><b class="m" style="color:{col};font-size:22px">{esc(s["bloque"])}</b> <span style="color:{TXT};font-size:22px">{esc(s["tipo"])}</span></div>'
                f'<div class="m" style="color:{MUT};font-size:17px">{fh(s["sale"])} → {esc(ent)}</div>'
                f'<div style="font-size:19px;line-height:1.3;color:{MUT}">{esc(s["obs"] or s["motivo"])}</div></div>')
    for t in rso[:4]:
        out += (f'<div style="padding:8px 0;border-bottom:1px solid {LINE};font-size:19px;line-height:1.3;color:{TXT}">'
                f' <span class="m" style="color:{AGUA};font-size:15px">RSO · </span>{esc(t[:220])}</div>')
    return out


def _cabeza(label, titulo, sub):
    return f"""
 <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:20px">
  <div style="display:flex;flex-direction:column;gap:8px">
   <div class="m" style="font-size:19px;letter-spacing:.14em;color:{AMBAR}">{label}</div>
   <div style="font-size:48px;font-weight:700;letter-spacing:-.02em;line-height:1.08">{titulo}</div>
   <div style="font-size:22px;color:{MUT}">{sub}</div>
  </div>
  <div class="m" style="font-size:15px;color:{CANA};border:2px solid {CANA2};border-radius:22px;padding:6px 14px;letter-spacing:.1em;white-space:nowrap;margin-top:2px">USO INTERNO</div>
 </div>
 <div style="height:5px;background:linear-gradient(90deg,{CANA} 0 70%,{AMBAR} 70% 100%);border-radius:3px"></div>"""


def _pagina(contenido, pie):
    return HEAD + f"""
<div id="page" style="width:1080px;box-sizing:border-box;background:{BG};color:{TXT};font-family:'Space Grotesk',sans-serif;padding:40px 36px 30px;display:flex;flex-direction:column;gap:22px">
{contenido}
 <div style="font-size:15px;color:{DIM};line-height:1.35" class="m">{pie}</div>
</div></body></html>"""


def build_zafra(r, temporada):
    """Devuelve 2 páginas (HTML): resumen y control por bloque. Formato ancho, legible en el celular."""
    d, t = r['d'], r['tot']
    fp_dia = t['E'] / t['plena_dia'] if t['plena_dia'] else 0
    fp_acum = t['acum'] / t['plena_acum'] if t['plena_acum'] else 0
    var = (t['E'] - t['E_ant']) / t['E_ant'] if t['E_ant'] else None
    var_s = var_txt(var, 1) + ' vs ayer' if var is not None else ''
    pend = ', '.join(f['bloque'] for f in r['pendientes'])
    ini = t['inicio']
    fecha = fecha_larga(d)
    k = (kpi('ENERGÍA DEL DÍA', n0(t['E']), 'MWh', var_s)
         + kpi('FACTOR DE PLANTA', f'{fp_dia*100:.1f}', '%', f'plena carga<br>{n0(t["plena_dia"])} MWh',
               CANA if fp_dia >= .75 else AMBAR if fp_dia >= .5 else ROJO)
         + kpi('ACUMULADO ZAFRA', f'{t["acum"]/1000:,.2f}', 'GWh', f'{fp_acum*100:.1f} % plena carga<br>{t["dias"]} días')
         + kpi('BLOQUES EN ZAFRA', str(t['n_zafra']), '', f'pendiente:<br>{esc(pend)}' if pend else 'ninguno pendiente'))
    hay_rojo = any(a[0] in ('alta', 'baja') for a in r['alertas'])
    p1 = _pagina(_cabeza(f'CONTROL DIARIO · ZAFRA {esc(temporada)} · 1/2', f'Ingenios<br>{fecha}',
                         f"Día {r['dia_n']} de zafra · inició el {ini.day} de {MESES[ini.month-1]}") + f"""
 <div style="display:flex;gap:12px">{k}</div>
 <div class="card" style="padding:20px 24px;border-color:{'#6b2f27' if hay_rojo else LINE}">
  <div class="sec">ALERTAS DEL DÍA</div>{alertas_html(r['alertas'])}</div>
 <div style="display:flex;gap:12px">
  <div class="card" style="flex:1;padding:20px 22px"><div class="sec">SALIDAS Y FALLAS</div>{salidas_html(r['salidas'], r['rso'])}</div>
  <div class="card" style="flex:1;padding:20px 22px"><div class="sec">ENERGÍA DIARIA EN ZAFRA</div>{grafica(r['serie'])}
   <div class="m" style="font-size:15px;color:{MUT};display:flex;gap:14px;flex-wrap:wrap"><span><span style="color:{CANA}">■</span> energía MWh</span><span><span style="color:{ROJO}">■</span> baja ≥ 10 %</span><span><span style="color:{AMBAR}">- -</span> plena carga</span></div></div>
 </div>""", 'FUENTE · AMM: posdespacho diario (carga horaria, indisponibilidades, RSO) y programa semanal vigente (CVG)')
    p2 = _pagina(_cabeza(f'CONTROL DIARIO · ZAFRA {esc(temporada)} · 2/2', 'Control por bloque',
                         f"{fecha} · día {r['dia_n']} de zafra") + f"""
 <div class="card" style="padding:18px 20px">{tabla(r['filas'])}</div>""",
                 'Factor de planta = energía ÷ (Pmax × 24 h); la raya marca 100 %. Rojo: baja ≥ 15 % vs ayer o FP &lt; 50 %. '
                 'Pmax del predespacho diario; P. real máx = máximo de la carga horaria. Días y fecha de inicio de zafra de cada bloque.')
    return [p1, p2]


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
