"""Control diario de zafra: arma la hoja de los ingenios con el posdespacho del día y la publica en Slack.

Uso:
  python scripts/zafra.py                    procesa y publica los días nuevos (posdespachos ya descargados)
  python scripts/zafra.py --fecha 20261125   vuelve a armar y publicar ese día
  python scripts/zafra.py --prueba           solo genera la imagen (no publica ni guarda el estado)
  python scripts/zafra.py --ayer-listo       código 0 si el día de ayer ya se publicó

Canal: SLACK_ZAFRA_CHANNEL si existe; si no, SLACK_CHANNEL_ID (#despacho-semanal).
Registro: data/publicados_zafra.txt   Estado de zafra: data/zafra/estado.json
"""
import os, sys, asyncio, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'programa'))
sys.path.insert(0, str(ROOT / 'scripts'))
import zafra_datos as Z                                  # noqa: E402
from render_zafra import build_zafra, texto_zafra    # noqa: E402
from render import to_png                            # noqa: E402

LOG = ROOT / 'data' / 'publicados_zafra.txt'
IMG = ROOT / 'imagenes'
GT = dt.timezone(dt.timedelta(hours=-6))


def publicados():
    return set(LOG.read_text(encoding='utf-8').split()) if LOG.exists() else set()


def anotar(tag):
    if tag not in publicados():
        with LOG.open('a', encoding='utf-8') as fh:
            fh.write(tag + '\n')


def publicar(pngs, texto):
    """Sube varias imágenes en un solo mensaje de Slack."""
    import json, requests
    token = os.environ.get('SLACK_BOT_TOKEN')
    canal = os.environ.get('SLACK_ZAFRA_CHANNEL') or os.environ.get('SLACK_CHANNEL_ID')
    if not token or not canal:
        print('  (sin SLACK_BOT_TOKEN / canal: no se publica)'); return False
    h = {'Authorization': f'Bearer {token}'}
    files = []
    for png in pngs:
        data = png.read_bytes()
        r = requests.post('https://slack.com/api/files.getUploadURLExternal', headers=h,
                          data={'filename': png.name, 'length': len(data)}, timeout=60).json()
        if not r.get('ok'): raise RuntimeError(f'Slack getUploadURLExternal: {r}')
        requests.post(r['upload_url'], files={'file': (png.name, data, 'image/png')}, timeout=120).raise_for_status()
        files.append({'id': r['file_id'], 'title': png.stem})
    c = requests.post('https://slack.com/api/files.completeUploadExternal',
                      headers={**h, 'Content-Type': 'application/json; charset=utf-8'},
                      data=json.dumps({'files': files, 'channel_id': canal, 'initial_comment': texto}), timeout=60).json()
    if not c.get('ok'): raise RuntimeError(f'Slack completeUploadExternal: {c}')
    return True


def hacer_dia(d, est, pm, info, cambios, prueba=False):
    r = Z.armar(d, est, pm, info, cambios)
    (IMG / str(d.year)).mkdir(parents=True, exist_ok=True)
    pngs = []
    for k, pagina in enumerate(build_zafra(r, est['temporada']), start=1):
        hp = IMG / str(d.year) / f'ZAFRA_{d:%Y%m%d}_{k}.html'
        hp.write_text(pagina, encoding='utf-8')
        png = hp.with_suffix('.png')
        alto = asyncio.run(to_png(hp, png)); hp.unlink()
        print(f'  página {k}: 1080 x {alto}')
        pngs.append(png)
    txt = texto_zafra(r, est['temporada'])
    print(txt)
    if prueba:
        print('  imágenes de prueba:', *pngs); return True
    return publicar(pngs, txt)


def main():
    est, pm, info = Z.cargar_json('estado.json'), Z.cargar_json('pmax.json'), Z.cargar_json('bloques.json')
    prueba = '--prueba' in sys.argv
    if '--fecha' in sys.argv:
        d = dt.datetime.strptime(sys.argv[sys.argv.index('--fecha') + 1], '%Y%m%d').date()
        if hacer_dia(d, est, pm, info, [], prueba) and not prueba:
            anotar(f'{d:%Y%m%d}')
        return 0
    hasta = dt.date.fromisoformat(est['procesado_hasta'])
    hoy = dt.datetime.now(GT).date()
    d = hasta + dt.timedelta(days=1)
    hubo = False
    while d < hoy:
        if not Z.pos_path(d).exists():
            print(f'{d}: todavía no hay posdespacho'); break
        bloques = list(est['bloques'])
        cvg = Z.cvg_dia(d, bloques)
        if not cvg:
            print(f'{d}: falta el programa semanal (CVG) de esa semana'); break
        cvg_ant = Z.cvg_dia(d - dt.timedelta(days=1), bloques)
        ch = Z.carga_horaria(d, bloques)
        cambios = Z.actualizar_estado(est, d, cvg, ch, cvg_ant)
        for c in cambios:
            print('  CAMBIO:', c)
        print('Procesando zafra', d)
        if not hacer_dia(d, est, pm, info, cambios, prueba):
            break
        if prueba:
            break
        est['procesado_hasta'] = d.isoformat()
        Z.guardar_json('estado.json', est)
        anotar(f'{d:%Y%m%d}')
        hubo = True
        d += dt.timedelta(days=1)
    return 0 if hubo or d >= hoy else 3


if __name__ == '__main__':
    if '--ayer-listo' in sys.argv:
        ayer = dt.datetime.now(GT).date() - dt.timedelta(days=1)
        sys.exit(0 if f'{ayer:%Y%m%d}' in publicados() else 1)
    sys.exit(main())
