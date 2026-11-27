"""Control diario de zafra: arma la hoja de los ingenios con el posdespacho del día y la publica en Slack.

Uso:
  python scripts/zafra.py                    procesa y publica los días nuevos (posdespachos ya descargados)
  python scripts/zafra.py --fecha 20261125   vuelve a armar y publicar ese día
  python scripts/zafra.py --prueba           solo genera la imagen (no publica ni guarda el estado)
  python scripts/zafra.py --ayer-listo       código 0 si el día de ayer ya se publicó

Canales: SLACK_ZAFRA_CHANNEL si existe; si no, SLACK_CHANNEL_ID (#despacho-semanal) -> versión compacta.
         SLACK_ZAFRA_CHANNEL_2 (canal nuevo, opcional) -> versión con la tabla completa para computadora.
  python scripts/zafra.py --fecha 20261125 --canal 2   re-publica ese día solo en el canal nuevo
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


def canales():
    """[(etiqueta, canal, completa)]: #despacho-semanal con la versión compacta y, si existe, el canal nuevo
    (SLACK_ZAFRA_CHANNEL_2) con la tabla completa para computadora."""
    out = []
    c1 = os.environ.get('SLACK_ZAFRA_CHANNEL') or os.environ.get('SLACK_CHANNEL_ID')
    if c1:
        out.append(('', c1, False))
    c2 = os.environ.get('SLACK_ZAFRA_CHANNEL_2')
    if c2:
        out.append(('@2', c2, True))
    return out


def publicar(pngs, texto, canal):
    """Sube las imágenes en un solo mensaje de Slack al canal indicado."""
    import json, requests
    token = os.environ.get('SLACK_BOT_TOKEN')
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


def imagen(r, d, temporada, completa=False):
    """Arma la imagen única (resumen + control por bloque, lado a lado)."""
    from render_zafra import ANCHO_COMPLETA
    (IMG / str(d.year)).mkdir(parents=True, exist_ok=True)
    suf = '_completa' if completa else ''

    def render(alto):
        out = []
        for k, pagina in enumerate(build_zafra(r, temporada, alto, completa), start=1):
            hp = IMG / str(d.year) / f'ZAFRA_{d:%Y%m%d}{suf}_{k}.html'
            hp.write_text(pagina, encoding='utf-8')
            png = hp.with_suffix('.png')
            w = ANCHO_COMPLETA if (completa and k == 2) else 1080
            h = asyncio.run(to_png(hp, png, width=w)); hp.unlink()
            out.append((png, h))
        return out
    partes = render(1921)
    alto = max(h for _, h in partes)
    if any(h != alto for _, h in partes):          # una hoja creció (más alertas o bloques): igualar alturas
        partes = render(alto)
    from PIL import Image
    ims = [Image.open(p).convert('RGB') for p, _ in partes]
    H = max(im.size[1] for im in ims)
    final = Image.new('RGB', (sum(im.size[0] for im in ims), H), ims[0].getpixel((4, 4)))
    x = 0
    for im in ims:
        final.paste(im, (x, 0)); x += im.size[0]
    png = IMG / str(d.year) / f'ZAFRA_{d:%Y%m%d}{suf}.png'
    final.save(png, optimize=True)
    for p, _ in partes:
        p.unlink()
    print(f'  imagen{suf}: {final.size[0]//2} x {final.size[1]//2}')
    return png


def hacer_dia(d, est, pm, info, cambios, prueba=False, solo=None):
    """Arma y publica el día d en cada canal que falte (o en todos si prueba). Devuelve True si quedó todo publicado."""
    r = Z.armar(d, est, pm, info, cambios)
    txt = texto_zafra(r, est['temporada'])
    print(txt)
    if prueba:
        print('  imágenes de prueba:', imagen(r, d, est['temporada']), imagen(r, d, est['temporada'], True))
        return True
    ok = True
    hechos = publicados()
    for tag, canal, completa in canales():
        if solo is None and f'{d:%Y%m%d}{tag}' in hechos:
            continue
        if solo is not None and tag != solo:
            continue
        try:
            if publicar([imagen(r, d, est['temporada'], completa)], txt, canal):
                anotar(f'{d:%Y%m%d}{tag}')
            else:
                ok = False
        except Exception as e:                       # p. ej. el bot no está invitado al canal nuevo
            print(f'  no se pudo publicar en {canal}: {e}'); ok = ok and tag != ''
    return ok


def main():
    est, pm, info = Z.cargar_json('estado.json'), Z.cargar_json('pmax.json'), Z.cargar_json('bloques.json')
    prueba = '--prueba' in sys.argv
    if '--fecha' in sys.argv:
        d = dt.datetime.strptime(sys.argv[sys.argv.index('--fecha') + 1], '%Y%m%d').date()
        canal = sys.argv[sys.argv.index('--canal') + 1] if '--canal' in sys.argv else None
        solo = None if canal is None else ('@2' if canal == '2' else '')
        if solo is None and not prueba:
            for tag, c, completa in canales():       # re-publicar: en todos los canales
                hacer_dia(d, est, pm, info, [], solo=tag)
        else:
            hacer_dia(d, est, pm, info, [], prueba, solo=solo)
        return 0
    hasta = dt.date.fromisoformat(est['procesado_hasta'])
    hoy = dt.datetime.now(GT).date()
    if not prueba:                                    # días ya procesados que le faltan a algún canal (últimos 3)
        hechos = publicados()
        for k in range(3):
            x = hasta - dt.timedelta(days=k)
            for tag, canal, completa in canales():
                if f'{x:%Y%m%d}' in hechos and f'{x:%Y%m%d}{tag}' not in hechos:
                    print('Reintento de', x, 'en el canal', tag or '1')
                    hacer_dia(x, est, pm, info, [], solo=tag)
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
        hubo = True
        d += dt.timedelta(days=1)
    return 0 if hubo or d >= hoy else 3


if __name__ == '__main__':
    if '--ayer-listo' in sys.argv:
        ayer = dt.datetime.now(GT).date() - dt.timedelta(days=1)
        hechos = publicados()
        sys.exit(0 if all(f'{ayer:%Y%m%d}{tag}' in hechos for tag, _, _ in canales()) else 1)
    sys.exit(main())
