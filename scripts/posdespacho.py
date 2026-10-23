"""PosDespacho diario: descarga desde la AMM, compara contra el programa semanal vigente y publica en Slack.

- Descarga https://www.amm.org.gt/pdfs2/post_despacho/POSDESPACHO_DIARIO/AAAA/MM_MES/PDaaaammdd.zip
  de los últimos 7 días que falten, y guarda el Excel en data/posdespacho/AAAA/PDaaaammdd.xlsx.
- Por cada posdespacho no publicado: arma la imagen (línea ER) y la publica en Slack con el resumen.
- Registro: data/publicados_pos.txt

Uso: python scripts/posdespacho.py                 (descargar + publicar lo pendiente)
     python scripts/posdespacho.py --forzar 20261021 (re-publicar ese día)
"""
import os, sys, re, asyncio, datetime as dt
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'programa'))
sys.path.insert(0, str(ROOT / 'scripts'))
from parse_pds import parse_file, merge_versions                     # noqa: E402
from parse_pos import parse_pos, extract_zip, comparar               # noqa: E402
from render_pos import build_pos, texto_pos                           # noqa: E402
from render import to_png                                             # noqa: E402
from publicar import slack_upload, all_files, versions                # noqa: E402
from descargar import semana_amm, GT, UA                              # noqa: E402

POS = ROOT / 'data' / 'posdespacho'
LOG = ROOT / 'data' / 'publicados_pos.txt'
IMG = ROOT / 'imagenes'
MES = ['', 'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO',
       'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']


def descargar(dias=7):
    hoy = dt.datetime.now(GT).date()
    nuevos = []
    for k in range(1, dias + 1):
        d = hoy - dt.timedelta(days=k)
        carpeta = POS / str(d.year); carpeta.mkdir(parents=True, exist_ok=True)
        if (carpeta / f'PD{d:%Y%m%d}.xlsx').exists():
            continue
        url = (f'https://www.amm.org.gt/pdfs2/post_despacho/POSDESPACHO_DIARIO/{d.year}/'
               f'{d.month:02d}_{MES[d.month]}/PD{d:%Y%m%d}.zip')
        try:
            r = requests.get(url, headers=UA, timeout=120)
            if r.status_code != 200 or r.content[:2] != b'PK':
                continue                                   # todavía no está publicado
            extract_zip(r.content, carpeta, d)
            nuevos.append(d); print('NUEVO posdespacho:', d)
        except Exception as e:
            print(f'No se pudo descargar {d}: {e}')
    return nuevos


def programa_vigente(d):
    """Original + redespachos de la semana del día d (los redespachos solo cubren sus días vigentes)."""
    domingo = d - dt.timedelta(days=(d.weekday() + 1) % 7)
    anio, sem = semana_amm(domingo)
    vers = versions(all_files(), str(anio), sem)
    if not vers:
        return None
    return merge_versions([parse_file(x['path']) for x in vers])


def publicar(forzar=None):
    done = set(LOG.read_text(encoding='utf-8').split()) if LOG.exists() else set()
    files = sorted(POS.glob('*/PD*.xlsx'))
    for f in files:
        tag = re.search(r'PD(\d{8})', f.name).group(1)
        if (forzar and tag != forzar) or (not forzar and tag in done):
            continue
        d = dt.datetime.strptime(tag, '%Y%m%d').date()
        prog = programa_vigente(d)
        if prog is None or d not in prog['days']:
            print(f'{tag}: falta el programa semanal de esa semana; se omite'); continue
        print('Procesando posdespacho', tag)
        c = comparar(parse_pos(f), prog)
        (IMG / str(d.year)).mkdir(parents=True, exist_ok=True)
        hp = IMG / str(d.year) / f'PD_{tag}.html'
        hp.write_text(build_pos(c), encoding='utf-8')
        png = hp.with_suffix('.png')
        asyncio.run(to_png(hp, png)); hp.unlink()
        if c['sin_tech']:
            print('  nemos sin tecnología:', c['sin_tech'])
        if not slack_upload(png, texto_pos(c)):
            continue
        print('  publicado en Slack')
        if tag not in done:
            with LOG.open('a', encoding='utf-8') as fh: fh.write(tag + '\n')
            done.add(tag)


def pendientes():
    done = set(LOG.read_text(encoding='utf-8').split()) if LOG.exists() else set()
    return [f for f in POS.glob('*/PD*.xlsx') if re.search(r'PD(\d{8})', f.name).group(1) not in done]


if __name__ == '__main__':
    if '--hay-pendientes' in sys.argv:            # código 0 si hay algo por publicar
        sys.exit(0 if pendientes() else 1)
    if '--revisar' in sys.argv:                  # solo descarga y avisa si hay algo pendiente
        descargar()
        p = pendientes()
        print('Pendientes:', [x.name for x in p] or 'ninguno')
        out = os.environ.get('GITHUB_OUTPUT')
        if out:
            with open(out, 'a') as fh: fh.write(f"pendientes={'true' if p else 'false'}\n")
        sys.exit(0)
    forzar = sys.argv[sys.argv.index('--forzar') + 1] if '--forzar' in sys.argv else None
    if '--solo-publicar' not in sys.argv:
        descargar()
    publicar(forzar)
