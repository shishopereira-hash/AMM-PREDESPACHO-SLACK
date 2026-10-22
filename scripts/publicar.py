"""Busca Excel nuevos de la AMM en data/<año>/, genera la imagen (línea ER) y la publica en Slack.

- NN_PDSyyyymmdd.xlsx          -> imagen de predespacho (vs. semana anterior vigente)
- NN_PDSREPyyyymmdd(k).xlsx    -> imagen de redespacho (vs. versión inmediata anterior)

Lleva el registro de lo ya publicado en data/publicados.txt.
Variables de entorno: SLACK_BOT_TOKEN, SLACK_CHANNEL_ID (si faltan, solo genera la imagen).
Uso: python scripts/publicar.py            (procesa lo pendiente)
     python scripts/publicar.py --forzar 43_PDSREP20261020(1).xlsx   (re-publica uno)
"""
import os, sys, re, json, asyncio
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'programa'))
from parse_pds import parse_file, merge_versions, summary, plant_costs, pct, MIX_ORDER  # noqa: E402
from render import build_pre, build_rep, to_png, period, TECH_NAME                    # noqa: E402

DATA, IMG = ROOT / 'data', ROOT / 'imagenes'
LOG = DATA / 'publicados.txt'
PAT = re.compile(r'(\d+)_PDS(REP)?(\d{8})(?:\((\d+)\))?\.xlsx$', re.I)


def all_files():
    out = []
    for f in sorted(DATA.glob('*/*.xlsx')):
        m = PAT.match(f.name)
        if m:
            out.append({'path': f, 'year': f.parent.name, 'week': int(m.group(1)),
                        'rep': bool(m.group(2)), 'rev': int(m.group(4) or 0) if m.group(2) else 0,
                        'date': m.group(3)})
    return out


def versions(files, year, week):
    v = [x for x in files if x['year'] == year and x['week'] == week]
    return sorted(v, key=lambda x: (x['rev'], x['date']))


def prev_week_versions(files, year, week):
    if week > 1:
        return versions(files, year, week - 1)
    py = str(int(year) - 1)                      # semana 1: la anterior es la última del año pasado
    weeks = [x['week'] for x in files if x['year'] == py]
    return versions(files, py, max(weeks)) if weeks else []


def fmt_pct(p):
    return '—' if p is None else f"{'+' if p >= 0 else '−'}{abs(p):.1f}%"


def texto_pre(s, p):
    mp = s['mant'].get('P', [0, 0])
    return (f"📊 *Predespacho semanal · Semana {s['week']}* ({period(s['days'])})\n"
            f"• Demanda SNI: {s['dem']:,.0f} MWh ({fmt_pct(pct(s['dem'], p['dem']))})\n"
            f"• Pico de potencia: {s['peak']:,.0f} MW ({fmt_pct(pct(s['peak'], p['peak']))})\n"
            f"• Costo operativo: US${s['total_cost']/1e6:,.2f} M ({fmt_pct(pct(s['total_cost'], p['total_cost']))})\n"
            f"• Chixoy: {s['chixoy_e']:,.0f} MWh · valor del agua US${s['chixoy_wv']:.2f}/MWh\n"
            f"• Mantenimientos programados: {mp[0]} ({mp[1]:,.1f} MW)\n"
            f"_Variaciones vs semana {p['week']}. Fuente: AMM._")


def texto_rep(new, r):
    nota = '\n'.join(f'> {n}' for n in r['notes'])
    return (f"🔁 *Redespacho ({new['rev']}) · Semana {new['week']}* — vigente {period(new['days'])}\n"
            f"{nota}\n"
            f"• Costo operativo (días afectados): US${r['co']/1e6:,.2f} M → US${r['cn']/1e6:,.2f} M "
            f"({fmt_pct(pct(r['cn'], r['co']))})\n"
            f"• Chixoy · valor del agua: US${r['wvo']:.2f} → US${r['wvn']:.2f}/MWh\n"
            f"_Fuente: AMM._")


def slack_upload(png, comment):
    token, channel = os.environ.get('SLACK_BOT_TOKEN'), os.environ.get('SLACK_CHANNEL_ID')
    if not token or not channel:
        print('  (sin SLACK_BOT_TOKEN / SLACK_CHANNEL_ID: no se publica)'); return False
    h = {'Authorization': f'Bearer {token}'}
    data = png.read_bytes()
    r = requests.post('https://slack.com/api/files.getUploadURLExternal', headers=h,
                      data={'filename': png.name, 'length': len(data)}, timeout=60).json()
    if not r.get('ok'): raise RuntimeError(f'Slack getUploadURLExternal: {r}')
    up = requests.post(r['upload_url'], files={'file': (png.name, data, 'image/png')}, timeout=120)
    up.raise_for_status()
    c = requests.post('https://slack.com/api/files.completeUploadExternal',
                      headers={**h, 'Content-Type': 'application/json; charset=utf-8'},
                      data=json.dumps({'files': [{'id': r['file_id'], 'title': png.stem}],
                                       'channel_id': channel, 'initial_comment': comment}), timeout=60).json()
    if not c.get('ok'): raise RuntimeError(f'Slack completeUploadExternal: {c}')
    return True


def procesar(f, files):
    year, wk = f['year'], f['week']
    (IMG / year).mkdir(parents=True, exist_ok=True)
    if not f['rep']:
        prevs = prev_week_versions(files, year, wk)
        if not prevs:
            print(f'  falta la semana anterior a la {wk}; se omite'); return None
        cur = parse_file(f['path'])
        prev = merge_versions([parse_file(x['path']) for x in prevs])
        html, s, p = build_pre(cur, prev, f['path'].name, prev['file'])
        name, text = f'{wk:02d}_predespacho', texto_pre(s, p)
    else:
        vers = versions(files, year, wk)
        i = next(k for k, x in enumerate(vers) if x['path'] == f['path'])
        if i == 0:
            print('  no hay versión anterior para comparar; se omite'); return None
        old = merge_versions([parse_file(x['path']) for x in vers[:i]])
        new = parse_file(f['path'])
        html, r = build_rep(old, new, old['file'], new['file'])
        name, text = f"{wk:02d}_redespacho({f['rev']})", texto_rep(new, r)
    hp = IMG / year / f'{name}.html'
    hp.write_text(html, encoding='utf-8')
    png = IMG / year / f'{name}.png'
    asyncio.run(to_png(hp, png))
    hp.unlink()
    print('  imagen:', png.relative_to(ROOT))
    return png, text


def main():
    files = all_files()
    done = set(LOG.read_text(encoding='utf-8').split('\n')) if LOG.exists() else set()
    forzar = sys.argv[sys.argv.index('--forzar') + 1] if '--forzar' in sys.argv else None
    pend = [f for f in files if (f['path'].name == forzar) or (not forzar and f['path'].name not in done)]
    pend.sort(key=lambda x: (x['year'], x['week'], x['rev']))
    if not pend:
        print('Nada nuevo que publicar.'); return
    for f in pend:
        print('Procesando', f['path'].name)
        res = procesar(f, files)
        if res is None: continue
        png, text = res
        if not slack_upload(png, text):
            continue                     # no se marca como publicado; se reintenta en la próxima corrida
        print('  publicado en Slack')
        if f['path'].name not in done:
            with LOG.open('a', encoding='utf-8') as fh: fh.write(f['path'].name + '\n')
            done.add(f['path'].name)


if __name__ == '__main__':
    main()
