"""Control diario de zafra de los ingenios (bloques de cogeneración).

Fuentes (todo lo que ya descarga el bot):
  - Energía y potencia horaria: hoja "Carga Horaria" del posdespacho diario (data/posdespacho/AAAA/PDaaaammdd.xlsx).
  - Costo variable (CVG): hoja CVG del programa semanal vigente ese día (original + redespachos).
  - Salidas y fallas: hoja Indisponibilidades del posdespacho y párrafos del RSO que nombran a un ingenio.
  - Potencia máxima: data/zafra/pmax.json (valores del predespacho diario; se usa el último valor con fecha <= día).
  - Estado de zafra de cada bloque: data/zafra/estado.json (inicio / fin). Se arrancó con la Hoja4 del Directorio
    y el bot lo va actualizando con el mismo criterio:
      * inicia zafra el primer día con CVG bajo (< 30 US$/MWh) y generación > 0;
      * termina el día en que el CVG sube (día anterior < 30, día actual >= 40 y > 3 veces el anterior).
"""
import re, json, datetime as dt
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
ZDIR = ROOT / 'data' / 'zafra'
POS = ROOT / 'data' / 'posdespacho'

CVG_BAJO, CVG_ALTO = 30.0, 40.0
BAJA_ALERTA = 0.15          # baja de energía >= 15 % contra el día anterior
FP_ALERTA = 0.50            # factor de planta del día menor a 50 %


def cargar_json(nombre):
    return json.loads((ZDIR / nombre).read_text(encoding='utf-8'))


def guardar_json(nombre, obj):
    (ZDIR / nombre).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def _d(s):
    return dt.date.fromisoformat(s) if s else None


# ------------------------------------------------------------------ posdespacho
def pos_path(d):
    return POS / str(d.year) / f'PD{d:%Y%m%d}.xlsx'


def carga_horaria(d, bloques):
    """{bloque: (energía MWh del día, potencia máxima horaria MW)} desde la hoja Carga Horaria."""
    f = pos_path(d)
    if not f.exists():
        return None
    ws = openpyxl.load_workbook(f, read_only=True, data_only=True)['Carga Horaria']
    rows = list(ws.iter_rows(values_only=True))
    h = next(i for i, r in enumerate(rows) if r and 'CHX-H' in r)
    hdr = [str(c).strip() if c else None for c in rows[h]]
    out = {}
    for b in bloques:
        if b not in hdr:
            out[b] = (0.0, 0.0); continue
        j = hdr.index(b)
        e = rows[h + 1][j] or 0.0
        vals = [r[j] for r in rows[h + 2:] if r and isinstance(r[0], (int, float)) and isinstance(r[j], (int, float))]
        out[b] = (float(e), max(vals) if vals else 0.0)
    return out


def _bloque_de_unidad(u, bloques):
    if u in bloques:
        return u
    if u.endswith('1') and u[:-1] in bloques:      # GSL-C1 -> GSL-C, LUN-B1 -> LUN-B, SAA-B1 -> SAA-B ...
        return u[:-1]
    return None


def _dtm(f, h):
    if not isinstance(f, (dt.date, dt.datetime)):
        return None
    f = f.date() if isinstance(f, dt.datetime) else f
    t = h if isinstance(h, dt.time) else dt.time(0, 0)
    return dt.datetime.combine(f, t)


def salidas(d, bloques, desde_temporada):
    """Salidas forzadas, disparos y mantenimientos de los bloques que tocan el día d (sin degradaciones)."""
    f = pos_path(d)
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    ws = next((wb[s] for s in wb.sheetnames if s.lower().startswith('indisp')), None)
    if ws is None:
        return []
    ini, fin = dt.datetime.combine(d, dt.time(0)), dt.datetime.combine(d + dt.timedelta(days=1), dt.time(0))
    out, vistos = [], set()
    for r in ws.iter_rows(min_row=4, values_only=True):
        if not r or not isinstance(r[0], str):
            continue
        b = _bloque_de_unidad(r[0].strip(), bloques)
        mot = str(r[1] or '').strip()
        if not b or 'degrad' in mot.lower():
            continue
        sale, entra = _dtm(r[2], r[3]), _dtm(r[4], r[5])
        if sale is None or sale >= fin or (entra is not None and entra <= ini):
            continue
        if sale.date() < desde_temporada and entra is None:
            continue                                   # indisponibles de hace años (CON-B, EPI-B ...)
        obs = re.sub(r'\s+', ' ', str(r[7] or '')).strip()
        obs = re.split(r'\tAMM-|\s{2,}', obs)[0]
        k = (b, sale, entra, mot)
        if k in vistos:
            continue
        vistos.add(k)
        tipo = ('Disparo' if 'disparo' in obs.lower() else
                'Mantenimiento' if 'manten' in mot.lower() else
                'Falla al ser convocado' if 'falla al ser' in obs.lower() else 'Salida forzada')
        out.append({'bloque': b, 'unidad': r[0].strip(), 'tipo': tipo, 'motivo': mot,
                    'sale': sale, 'entra': entra, 'obs': obs[:160]})
    out.sort(key=lambda x: x['sale'])
    return out


_NOMBRES_RSO = r'MAGDALENA|PANTALE[OÓ]N|LA UNI[OÓ]N|SANTA ANA|MADRE TIERRA|TULUL[AÁ]|TRINIDAD|PALO GORDO|SANTA LUC[IÍ]A|EL PILAR|CONCEPCI[OÓ]N|ZAFRA'


def rso_ingenios(d, bloques):
    """Párrafos del RSO que mencionan un bloque de ingenio o la zafra."""
    from lector_posdespacho import leer_rso
    pref = sorted({b.split('-')[0] for b in bloques})
    rx = re.compile(r'\b(' + '|'.join(pref) + r')-[BC]\d*\b|' + _NOMBRES_RSO, re.I)
    try:
        ev = leer_rso(pos_path(d))
    except Exception as e:                            # el RSO no debe tumbar la imagen
        print('  RSO no leído:', e); return []
    return [e['texto'] for e in ev if rx.search(e['texto'])]


# ------------------------------------------------------------------ CVG del programa semanal
_cache_prog = {}


def cvg_dia(d, bloques):
    import sys
    sys.path.insert(0, str(ROOT / 'scripts'))
    from posdespacho import programa_vigente
    dom = d - dt.timedelta(days=(d.weekday() + 1) % 7)
    if dom not in _cache_prog:
        _cache_prog[dom] = programa_vigente(d)
    prog = _cache_prog[dom]
    out = {}
    if not prog:
        return out
    for b in bloques:
        hits = [c for c in prog['cvg'] if c['nemo'] == b and c['ini'] <= d <= c['fin']]
        if hits:
            out[b] = max(hits, key=lambda c: c.get('prio', 0))['cvg']
    return out


def pmax_dia(pmax, b, d):
    serie = pmax.get(b) or {}
    vals = [(k, v) for k, v in serie.items() if k <= d.isoformat()]
    return max(vals)[1] if vals else (min(serie.items())[1] if serie else None)


# ------------------------------------------------------------------ estado de zafra
def en_zafra(est, b, d):
    e = est['bloques'].get(b, {})
    i, f = _d(e.get('inicio')), _d(e.get('fin'))
    return bool(i and i <= d and (f is None or d < f))


def actualizar_estado(est, d, cvg, ch, cvg_ant):
    """Aplica el criterio de inicio / fin para el día d. Devuelve la lista de cambios."""
    cambios = []
    for b, e in est['bloques'].items():
        if e.get('fijo'):                              # Retiro del Mercado / Indisponible: no se toca
            continue
        c, ca = cvg.get(b), cvg_ant.get(b)
        gen = (ch.get(b) or (0, 0))[0]
        if en_zafra(est, b, d):
            if c is not None and ca is not None and ca < CVG_BAJO and c >= CVG_ALTO and c > 3 * ca:
                e['fin'] = d.isoformat()
                cambios.append({'bloque': b, 'que': 'termina', 'det': f'CVG {ca:.2f} → {c:.2f}'})
        elif (not e.get('inicio') or e.get('fin')) and c is not None and c < CVG_BAJO:
            if gen > 0:
                e['inicio'], e['fin'] = d.isoformat(), None
                det = f'CVG {ca:.2f} → {c:.2f}' if ca is not None and ca != c else f'CVG {c:.2f}'
                cambios.append({'bloque': b, 'que': 'inicia', 'det': f'{det}, generó {gen:,.0f} MWh'})
            else:
                e['pendiente'] = True
    for b, e in est['bloques'].items():
        if en_zafra(est, b, d):
            e.pop('pendiente', None)
    return cambios


# ------------------------------------------------------------------ armado del día
def dias_con_posdespacho(desde, hasta):
    d, out = desde, []
    while d <= hasta:
        if pos_path(d).exists():
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def armar(d, est, pmax, info, cambios=None):
    """Todos los datos del día d para la imagen y el mensaje."""
    bloques = list(est['bloques'])
    temporada = _d(est['temporada_desde'])
    ini_zafra = min((_d(e['inicio']) for e in est['bloques'].values() if e.get('inicio')), default=d)
    dias = dias_con_posdespacho(ini_zafra, d)
    hist = {}                                           # día -> {bloque: (E, Pmáx real)}
    for x in dias:
        hist[x] = carga_horaria(x, bloques)
    ant = dias[-2] if len(dias) >= 2 else None
    cvg_hoy = cvg_dia(d, bloques)
    cvg_ant = cvg_dia(ant, bloques) if ant else {}

    filas = []
    for b in bloques:
        e = est['bloques'][b]
        z_hoy = en_zafra(est, b, d)
        if not z_hoy and not e.get('pendiente'):
            continue
        E, pr = hist[d].get(b, (0, 0))
        Ea = hist[ant].get(b, (0, 0))[0] if ant else None
        z_ant = ant is not None and en_zafra(est, b, ant)
        pm = pmax_dia(pmax, b, d)
        acum = sum(hist[x][b][0] for x in dias if en_zafra(est, b, x))
        plena = sum((pmax_dia(pmax, b, x) or 0) * 24 for x in dias if en_zafra(est, b, x))
        ndias = sum(1 for x in dias if en_zafra(est, b, x))
        var = (E - Ea) / Ea if (Ea and Ea > 0 and z_ant) else None
        fp = E / (pm * 24) if pm else None
        filas.append({'bloque': b, 'nombre': info.get(b, {}).get('nombre', b), 'ingenio': info.get(b, {}).get('ingenio', ''),
                      'zafra': z_hoy, 'pendiente': bool(e.get('pendiente')) and not z_hoy, 'inicio': e.get('inicio'),
                      'cvg': cvg_hoy.get(b), 'cvg_ant': cvg_ant.get(b), 'E': E, 'E_ant': Ea, 'var': var,
                      'pmax': pm, 'p_real': pr, 'fp': fp, 'acum': acum if z_hoy else 0, 'plena': plena if z_hoy else 0,
                      'dias': ndias})
    filas.sort(key=lambda f: (not f['zafra'], f['ingenio'], f['bloque']))

    # serie diaria (total de los bloques en zafra cada día)
    serie = []
    for x in dias:
        Ex = sum(hist[x][b][0] for b in bloques if en_zafra(est, b, x))
        Px = sum((pmax_dia(pmax, b, x) or 0) * 24 for b in bloques if en_zafra(est, b, x))
        serie.append({'d': x, 'E': Ex, 'plena': Px})

    zf = [f for f in filas if f['zafra']]
    tot = {'E': sum(f['E'] for f in zf), 'plena_dia': sum((f['pmax'] or 0) * 24 for f in zf),
           'acum': sum(s['E'] for s in serie), 'plena_acum': sum(s['plena'] for s in serie),
           'dias': sum(1 for s in serie if s['E'] > 0), 'n_zafra': len(zf),
           'E_ant': serie[-2]['E'] if len(serie) >= 2 else None, 'inicio': ini_zafra}

    sal = [s for s in salidas(d, bloques, temporada) if s['bloque'] in {f['bloque'] for f in filas}]
    rso = rso_ingenios(d, bloques)

    # alertas
    alertas = []
    for c in (cambios or []):
        alertas.append(('zafra', f"{c['bloque']} {'inicia' if c['que'] == 'inicia' else 'termina'} zafra · {c['det']}"))
    if tot['E_ant'] and tot['E'] < tot['E_ant'] * (1 - 0.10):
        alertas.append(('baja', f"La energía total de zafra bajó {100*(1-tot['E']/tot['E_ant']):.1f} % contra el día anterior"))
    for f in zf:
        if f['E'] <= 0:
            alertas.append(('alta', f"{f['bloque']} no generó en todo el día"))
        elif f['var'] is not None and f['var'] <= -BAJA_ALERTA:
            alertas.append(('baja', f"{f['bloque']} bajó {abs(f['var'])*100:.0f} % ({f['E_ant']:,.0f} → {f['E']:,.0f} MWh)"))
        elif f['fp'] is not None and f['fp'] < FP_ALERTA:
            alertas.append(('fp', f"{f['bloque']} con factor de planta de {f['fp']*100:.0f} %"))
        if f['cvg'] is not None and f['cvg_ant'] is not None and abs(f['cvg'] - f['cvg_ant']) > 0.005:
            alertas.append(('cvg', f"{f['bloque']} cambió su CVG: {f['cvg_ant']:.2f} → {f['cvg']:.2f} US$/MWh"))
    for s in sal:
        if s['tipo'] != 'Mantenimiento' and s['sale'].date() == d:
            alertas.append(('alta', f"{s['bloque']} · {s['tipo'].lower()} {s['sale']:%H:%M}"
                                    f"{'–' + s['entra'].strftime('%H:%M') if s['entra'] and s['entra'].date() == d else ''}"))
    orden = {'zafra': 0, 'alta': 1, 'baja': 2, 'fp': 3, 'cvg': 4}
    alertas.sort(key=lambda a: orden[a[0]])
    pend = [f for f in filas if f['pendiente']]
    return {'d': d, 'filas': filas, 'tot': tot, 'serie': serie, 'salidas': sal, 'rso': rso,
            'alertas': alertas, 'pendientes': pend, 'dia_n': len(serie)}
