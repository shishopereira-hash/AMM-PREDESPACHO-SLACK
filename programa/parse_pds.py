"""Lectura de la Programación Semanal (PDS) y sus redespachos (PDSREP) de la AMM."""
import re, unicodedata, datetime as dt
from pathlib import Path
import openpyxl

SECTION_HEADERS = {
    'PLANTAS HIDRAULICAS': 'HIDRO', 'PLANTAS EOLICAS': 'EOLICA', 'PLANTAS SOLARES': 'SOLAR',
    'PLANTAS TERMICAS': None, 'TURBINAS DE VAPOR': 'VAPOR', 'GEOTERMICAS': 'GEO',
    'COGENERADORES (T.VAPOR)': 'COGEN', 'MOTORES RECIPROCANTES': 'MOTORES',
    'TURBINAS DE GAS': 'GAS', 'TRANSACCIONES INTERNACIONALES': 'INTER', 'DEMANDA': 'DEM',
}
# Etiquetas para la imagen
TECH_LABEL = {
    'HIDRO': ('💧', 'Hidroeléctricas'), 'CHIXOY': ('💧', 'Chixoy'), 'VAPOR': ('🔥', 'Turbinas de Vapor'),
    'MOTORES': ('🔥', 'Motores reciprocantes'), 'COGEN': ('🌾', 'Ingenios cogeneradores'),
    'SOLAR': ('☀️', 'Solar fotovoltaica'), 'CARIBE': ('🔌', 'Energía del Caribe'),
    'GEO': ('🌋', 'Geotérmicas'), 'EOLICA': ('💨', 'Eólicas'), 'GAS': ('🔥', 'Turbinas de gas'),
    'MEX': ('🔌', 'Importación México'),
}

def norm(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', s).strip().upper()

# Planta (sección, nombre normalizado en hoja ENERGIA) -> Nemo en hoja CVG.
# Las que no están aquí se buscan por nombre; si no se encuentran quedan "sin CVG".
CVG_OVERRIDE = {
    ('HIDRO', 'SAN ISIDRO'): 'SIS-H', ('VAPOR', 'SAN ISIDRO'): 'ISI-B',
    ('HIDRO', 'LA LIBERTAD'): 'LIB-H', ('VAPOR', 'LA LIBERTAD'): 'LLI-C',
    ('HIDRO', 'SANTA TERESA'): 'STS-H', ('HIDRO', 'HIDROELECTRICA SANTA TERESA'): 'HST-H',
    ('HIDRO', 'CANADA'): 'CAN-H', ('HIDRO', 'RECREO'): 'REC-H', ('HIDRO', 'RECREO II'): 'RC2-H',
    ('HIDRO', 'HIDRO XACBAL'): 'XAC-H', ('HIDRO', 'HIDRO XACBAL DELTA'): 'XAD-H',
    ('HIDRO', 'EL MANANTIAL 1'): 'MNL-H', ('HIDRO', 'EL MANANTIAL 2'): 'MNL-H',
    ('HIDRO', 'EL MANANTIAL 3'): 'MNL-H', ('HIDRO', 'EL MANANTIAL 4'): 'MNL-H',
    ('HIDRO', 'HIDROLECTRICA LOS PATOS'): 'HPT-H', ('HIDRO', 'VISION DE AGUILA'): 'VDA-H',
    ('SOLAR', 'HORUS I'): 'HRU-F1', ('SOLAR', 'HORUS II'): 'HRU-F2',
    ('VAPOR', 'ARIZONA VAPOR NO. 1'): 'ARI-V', ('VAPOR', 'GENERADORA DEL ATLANTICO (VAPOR)'): 'GAT-V',
    ('VAPOR', 'JAGUAR ENERGY UNIDAD 1'): 'JEN-C', ('VAPOR', 'JAGUAR ENERGY UNIDAD 2'): 'JEN-C',
    ('VAPOR', 'LAS PALMAS II'): 'LPA-C', ('VAPOR', 'SAN JOSE'): 'SJO-C', ('VAPOR', 'GENERADORA COSTA SUR'): 'GCS-C',
    ('COGEN', 'PANTALEON B1'): 'PNT-B1', ('COGEN', 'PANTALEON B3'): 'PNT-B3',
    ('COGEN', 'SANTA ANA'): 'SAA-B', ('COGEN', 'SANTA ANA B2'): 'SAA-B2',
    ('COGEN', 'MAGDALENA B1'): 'MAG-B1', ('COGEN', 'MAGDALENA B3'): 'MAG-B3', ('COGEN', 'MAGDALENA B4'): 'MAG-B4',
    ('COGEN', 'MAGDALENA B5'): 'MAG-B5', ('COGEN', 'MAGDALENA B6'): 'MAG-B6', ('COGEN', 'MAGDALENA B7'): 'MAG-B7',
    ('COGEN', 'TULULA BLOQUE 1'): 'TUL-B1', ('COGEN', 'TULULA BLOQUE 4'): 'TUL-B4',
    ('COGEN', 'TRINIDAD B3'): 'TND-B3', ('COGEN', 'TRINIDAD B4'): 'TND-B4', ('COGEN', 'TRINIDAD B5'): 'TND-B5',
    ('COGEN', 'LA UNION B1'): 'LUN-B',
    ('COGEN', 'EL PILAR B3'): 'EPI-B3', ('COGEN', 'PALO GORDO B1'): 'PGO-B', ('COGEN', 'PALO GORDO B2'): 'PGO-B2',
    ('MOTORES', 'PQP'): 'PQP-B', ('MOTORES', 'LAS PALMAS BUNKER'): 'LPA-B', ('MOTORES', 'GENOR'): 'GEN-B',
    ('MOTORES', 'TDL B1 ( 6,7,8,12)'): 'TDL-B', ('MOTORES', 'TDL B2 (3,4,9)'): 'TDL-B', ('MOTORES', 'TDL B3 (10,11,13)'): 'TDL-B',
    ('MOTORES', 'ELECTROGENERACION'): 'ELG-B', ('MOTORES', 'TERMICA'): 'TER-B', ('MOTORES', 'TERMICA II'): 'TER-B2',
    ('MOTORES', 'GENERADORA DEL ATLANTICO (BIOGAS)'): 'GAT-B', ('MOTORES', 'BIOGAS DEL VERTEDERO EL TREBOL'): 'BVT-B',
    ('MOTORES', 'OCULTUN'): 'OCT-G', ('MOTORES', 'OOXOL'): 'OXL-G', ('MOTORES', 'ARIZONA'): 'ARI-O',
    ('MOTORES', 'GENOSA'): 'GGO-B', ('MOTORES', 'COENESA'): 'COE-D',
    ('GAS', 'ESCUINTLA GAS 5'): 'ESC-G5', ('GAS', 'TAMPA'): 'TAM-G', ('GAS', 'STEWART & STEVENSON'): 'S&S-D',
    ('GAS', 'ACTUN CAN GAS NATURAL'): 'ACG-G',
    ('INTER', 'ENERGIA DEL CARIBE'): 'EDC-I',
    ('GEO', 'ORZUNIL'): 'ZUN-G', ('GEO', 'ORTITLAN'): 'ORT-G',
}


def _ws_rows(ws, maxc=30):
    return [list(r) for r in ws.iter_rows(max_col=maxc, values_only=True)]


def parse_file(path):
    path = Path(path)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {'file': path.name, 'is_rep': 'PDSREP' in path.name.upper()}
    m = re.match(r'(\d+)_PDS(?:REP)?(\d{8})(?:\((\d+)\))?', path.name, re.I)
    out['week'] = int(m.group(1)); out['file_date'] = dt.datetime.strptime(m.group(2), '%Y%m%d').date()
    out['rev'] = int(m.group(3)) if m.group(3) else 0

    # ---------- ENERGIA ----------
    rows = _ws_rows(wb['ENERGIA'])
    out['period_text'] = next((r[1] for r in rows[:6] if r[1] and ('SEMANA' in str(r[1]) or 'PER' in str(r[1]))), '')
    hdr = next(i for i, r in enumerate(rows) if any(isinstance(v, dt.datetime) for v in r))
    dcols = [(j, v.date()) for j, v in enumerate(rows[hdr]) if isinstance(v, dt.datetime)]
    out['days'] = [d for _, d in dcols]
    plants, section, totals, special = [], None, {}, {}
    for r in rows[hdr + 1:]:
        name = r[1]
        if name is None: continue
        n = norm(name)
        vals = [float(r[j] or 0) for j, _ in dcols]
        if n in SECTION_HEADERS:
            if SECTION_HEADERS[n]: section = SECTION_HEADERS[n]
            if any(r[j] is not None for j, _ in dcols): totals[section or n] = vals
            continue
        if section == 'DEM':
            special[n] = vals; continue
        if not any(r[j] is not None for j, _ in dcols): continue
        tech = section
        if section == 'HIDRO' and n == 'CHIXOY': tech = 'CHIXOY'
        if section == 'INTER':
            if n == 'ENERGIA DEL CARIBE': tech = 'CARIBE'
            elif 'IMPORTACIONES MEXICO' in n: tech = 'MEX'
            else: tech = 'MER:' + n
        plants.append({'name': str(name).strip(), 'n': n, 'section': section, 'tech': tech, 'daily': vals})
    out['plants'] = plants
    def sp(key):
        return next((v for k, v in special.items() if k.startswith(key)), None)
    out['dem_energy'] = sp('DEMANDA DE ENERGIA S.N.I')
    out['dem_power'] = sp('DEM. MAX POTENCIA')
    out['dem_energy_exp'] = sp('DEM. ENERGIA S.N.I. + EXPORTACIONES')
    # Los redespachos de la AMM traen las 7 columnas, con ceros en los días que no cambian:
    # se dejan solo los días con demanda programada (los días vigentes del redespacho).
    if out['dem_energy'] and any(v > 0 for v in out['dem_energy']):
        keep = [i for i, v in enumerate(out['dem_energy']) if v > 0]
        if len(keep) < len(out['days']):
            out['days'] = [out['days'][i] for i in keep]
            for p in plants: p['daily'] = [p['daily'][i] for i in keep]
            for f in ('dem_energy', 'dem_power', 'dem_energy_exp'):
                if out[f]: out[f] = [out[f][i] for i in keep]

    # ---------- CVG ----------
    cvg = []
    for r in _ws_rows(wb['CVG'], 9)[4:]:
        if r[1] and isinstance(r[3], (int, float)) and isinstance(r[4], dt.datetime):
            cvg.append({'nemo': str(r[1]).strip(), 'name': norm(r[2]), 'cvg': float(r[3]),
                        'ini': r[4].date(), 'fin': (r[5].date() if isinstance(r[5], dt.datetime) else r[4].date())})
    out['cvg'] = cvg

    # ---------- Mantenimientos ----------
    mants = []
    for r in _ws_rows(wb['Mantenimientos'], 20):
        if isinstance(r[1], (int, float)) and r[5]:
            mw = r[17] if isinstance(r[17], (int, float)) else 0
            mants.append({'equipo': str(r[3] or '').strip(), 'unidad': str(r[4] or '').strip(),
                          'tipo': str(r[5]).strip().upper(), 'de': r[7], 'a': r[10], 'mw': float(mw),
                          'agente': str(r[2] or '').strip()})
    out['mants'] = mants

    # ---------- Observaciones (sección principal) ----------
    obs = []
    for r in _ws_rows(wb['Observaciones'], 3)[7:]:
        if r[1] and 'INFORMACI' in norm(r[1]): break
        if r[2]: obs.append(str(r[2]).strip())
    out['obs'] = obs
    return out


# ---------------- Cálculos ----------------
def cvg_index(cvg):
    by_nemo, by_name = {}, {}
    for c in cvg:
        by_nemo.setdefault(c['nemo'], []).append(c)
        by_name.setdefault(c['name'], c['nemo'])
    return by_nemo, by_name


def cvg_for(plant, day, by_nemo, by_name):
    nemo = CVG_OVERRIDE.get((plant['section'], plant['n']))
    if nemo is None:
        nemo = by_name.get(plant['n'])
    if nemo is None or nemo not in by_nemo:
        return None
    hits = [c for c in by_nemo[nemo] if c['ini'] <= day <= c['fin']]
    if hits:
        return max(hits, key=lambda c: c.get('prio', 0))['cvg']   # la versión más reciente manda
    return by_nemo[nemo][0]['cvg']


def plant_costs(data, days=None):
    """Costo por planta = Σ energía diaria × CVG vigente ese día."""
    by_nemo, by_name = cvg_index(data['cvg'])
    days = days or data['days']
    idx = [data['days'].index(d) for d in days if d in data['days']]
    res = []
    for p in data['plants']:
        if p['tech'].startswith('MER:'): continue
        e = sum(p['daily'][i] for i in idx)
        cost, matched = 0.0, True
        for i in idx:
            c = cvg_for(p, data['days'][i], by_nemo, by_name)
            if c is None: matched = False; break
            cost += p['daily'][i] * c
        res.append({**p, 'energy': e, 'cost': cost if matched else None})
    return res


MIX_ORDER = ['HIDRO', 'VAPOR', 'MOTORES', 'COGEN', 'SOLAR', 'CARIBE', 'CHIXOY', 'GEO', 'EOLICA', 'GAS', 'MEX']

def mix(data, days=None):
    days = days or data['days']
    idx = [data['days'].index(d) for d in days if d in data['days']]
    m = {}
    for p in data['plants']:
        if p['tech'] in MIX_ORDER:
            m[p['tech']] = m.get(p['tech'], 0) + sum(p['daily'][i] for i in idx)
    return m


def chixoy_water_value(data, days=None):
    by_nemo, _ = cvg_index(data['cvg'])
    days = days or data['days']
    vals = []
    for d in days:
        hits = [c for c in by_nemo.get('CHX-H', []) if c['ini'] <= d <= c['fin']]
        if hits: vals.append(max(hits, key=lambda c: c.get('prio', 0))['cvg'])
    return vals  # una entrada por día


def summary(data):
    pc = plant_costs(data)
    total_cost = sum(p['cost'] for p in pc if p['cost'] is not None)
    gen_total = sum(p['energy'] for p in pc if p['tech'] in MIX_ORDER)
    gen_cov = sum(p['energy'] for p in pc if p['tech'] in MIX_ORDER and p['cost'] is not None)
    no_cvg = [p['name'] for p in pc if p['cost'] is None and p['energy'] > 0.5]
    m = mix(data)
    wv = chixoy_water_value(data)
    chx = next(p for p in pc if p['tech'] == 'CHIXOY')
    mt = {}
    for x in data['mants']:
        k = x['tipo'] if x['tipo'] in ('P', 'NP', 'C') else 'OTRO'
        mt.setdefault(k, [0, 0.0]); mt[k][0] += 1; mt[k][1] += x['mw']
    top_mant = sorted([x for x in data['mants'] if x['tipo'] == 'P'], key=lambda x: -x['mw'])[:5]
    return {
        'week': data['week'], 'days': data['days'], 'file': data['file'],
        'dem': sum(data['dem_energy']), 'dem_exp': sum(data['dem_energy_exp']),
        'peak': max(data['dem_power']),
        'total_cost': total_cost, 'coverage': gen_cov / gen_total, 'no_cvg': no_cvg,
        'mix': m, 'gen_total': sum(m.values()),
        'chixoy_e': chx['energy'], 'chixoy_cost': chx['cost'],
        'chixoy_wv': sum(wv) / len(wv) if wv else None,
        'top_cost': sorted([p for p in pc if p['cost']], key=lambda p: -p['cost'])[:5],
        'mant': mt, 'top_mant': top_mant,
    }


def pct(a, b):
    return (a - b) / b * 100 if b else None


def merge_versions(versions):
    """Semana vigente: el original con los días reemplazados por cada redespacho (en orden)."""
    import copy
    base = copy.deepcopy(versions[0])
    for c in base['cvg']: c['prio'] = 0
    for k, v in enumerate(versions[1:], start=1):
        for c in v['cvg']: base['cvg'].append({**c, 'prio': k})
        pos = {p['section'] + '|' + p['n']: p for p in base['plants']}
        for p in v['plants']:
            key = p['section'] + '|' + p['n']
            if key not in pos:
                newp = {**p, 'daily': [0.0] * len(base['days'])}
                base['plants'].append(newp); pos[key] = newp
        for j, d in enumerate(v['days']):
            if d not in base['days']: continue
            i = base['days'].index(d)
            vp = {p['section'] + '|' + p['n']: p for p in v['plants']}
            for key, bp in pos.items():
                bp['daily'][i] = vp[key]['daily'][j] if key in vp else 0.0
            for f in ('dem_energy', 'dem_power', 'dem_energy_exp'):
                if v.get(f) and base.get(f): base[f][i] = v[f][j]
        base['obs'] = v['obs']; base['rev'] = v['rev']; base['is_rep'] = v['is_rep']
        base['file'] = v['file']
    return base
