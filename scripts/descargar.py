"""Revisa la página de la AMM y descarga a data/<año>/ los predespachos y redespachos nuevos.

Usa el mismo listado que la página "Planificación de la Operación → Semanales → Despacho Semanal":
  https://www.amm.org.gt/pds.php?anio=AAAA&fechadomingo=AAAAMMDD&semana=NN

Nombres locales (iguales a los que usa Luis Pablo):
  NN_PDSyyyymmdd.xlsx            predespacho original
  NN_PDSREPyyyymmdd(k).xlsx      k = número de redespacho de esa semana (1, 2, ...)

Escribe en GITHUB_OUTPUT  nuevos=true|false.
"""
import os, re, json, hashlib, datetime as dt
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
REG = DATA / 'descargas.json'
BASE = 'https://www.amm.org.gt/pds.php'
UA = {'User-Agent': 'Mozilla/5.0 (AMM-PREDESPACHO-SLACK)'}
GT = dt.timezone(dt.timedelta(hours=-6))


def semana_amm(domingo):
    """Semana AMM: semanas domingo-sábado; la semana 1 es la que contiene el 1 de enero."""
    sabado = domingo + dt.timedelta(days=6)
    anio = sabado.year
    ene1 = dt.date(anio, 1, 1)
    dom1 = ene1 - dt.timedelta(days=(ene1.weekday() + 1) % 7)   # domingo de la semana del 1 de enero
    return anio, (domingo - dom1).days // 7 + 1


def domingos_a_revisar(hoy):
    actual = hoy - dt.timedelta(days=(hoy.weekday() + 1) % 7)    # domingo de esta semana
    return [actual, actual + dt.timedelta(days=7)]                # esta semana y la próxima (viernes)


def listar(domingo):
    anio, sem = semana_amm(domingo)
    url = f"{BASE}?anio={anio}&fechadomingo={domingo:%Y%m%d}&semana={sem:02d}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    links = re.findall(r'href="([^"]+\.xlsx?)"', r.text, re.I)
    return anio, sem, links


def huella(fuente, nombre):
    """Resumen del contenido (días, demanda y energía por planta) para detectar el mismo archivo editado."""
    import sys, tempfile
    sys.path.insert(0, str(ROOT / 'programa'))
    from parse_pds import parse_file
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / nombre
        tmp.write_bytes(fuente if isinstance(fuente, bytes) else Path(fuente).read_bytes())
        d = parse_file(tmp)
    return (tuple(d['days']), round(sum(d['dem_energy'] or []), 1),
            tuple(round(sum(p['daily']), 1) for p in d['plants']), tuple(d['obs']))


def mismo_contenido(path, content):
    try:
        return huella(path, path.name) == huella(content, path.name)
    except Exception:
        return False


def main():
    reg = json.loads(REG.read_text(encoding='utf-8')) if REG.exists() else {}
    nuevos = []
    hoy = dt.datetime.now(GT).date()
    for dom in domingos_a_revisar(hoy):
        try:
            anio, sem, links = listar(dom)
        except Exception as e:
            print(f'No se pudo revisar la semana del {dom}: {e}'); continue
        print(f'Semana {sem} ({dom}): {len(links)} archivo(s) en la AMM')
        for url in links:
            name = url.rsplit('/', 1)[-1]
            m = re.match(r'(\d+)_PDS(REP)?(\d{8})\.xlsx?$', name, re.I)
            if not m: continue
            try:
                b = requests.get(url, headers=UA, timeout=120); b.raise_for_status()
            except Exception as e:
                print(f'  no se pudo descargar {name}: {e}'); continue
            h = hashlib.sha256(b.content).hexdigest()
            prev = reg.get(url)
            if prev and prev['sha256'] == h:
                continue                                   # ya lo tenemos, sin cambios
            wk, es_rep, fecha = int(m.group(1)), bool(m.group(2)), m.group(3)
            carpeta = DATA / str(anio); carpeta.mkdir(parents=True, exist_ok=True)
            igual = [f for f in carpeta.glob(f'{wk:02d}_PDS*.xlsx')
                     if hashlib.sha256(f.read_bytes()).hexdigest() == h or mismo_contenido(f, b.content)]
            if igual:                                      # ya estaba (subido a mano o descargado antes)
                reg[url] = {'sha256': h, 'local': igual[0].name}
                continue
            if not es_rep:
                local = f'{wk:02d}_PDS{fecha}.xlsx'
                if prev:   # la AMM reemplazó el original: se trata como un redespacho más
                    es_rep = True
            if es_rep:
                k = len(list(carpeta.glob(f'{wk:02d}_PDSREP*.xlsx'))) + 1
                local = f'{wk:02d}_PDSREP{fecha}({k}).xlsx'
            (carpeta / local).write_bytes(b.content)
            reg[url] = {'sha256': h, 'local': local, 'descargado': dt.datetime.now(GT).isoformat(timespec='minutes')}
            nuevos.append(local)
            print('  NUEVO:', local)
    REG.write_text(json.dumps(reg, indent=1, ensure_ascii=False), encoding='utf-8')
    out = os.environ.get('GITHUB_OUTPUT')
    if out:
        with open(out, 'a') as f: f.write(f"nuevos={'true' if nuevos else 'false'}\n")
    print('Nuevos:', nuevos or 'ninguno')


if __name__ == '__main__':
    main()
