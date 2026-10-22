"""Genera las imágenes semanales (línea gráfica ER) a partir de los Excel de la AMM.

Uso:
  python run.py pre <carpeta_excels> <carpeta_salida> [semana]
      Predespacho. Sin semana: busca el archivo NN_PDS<domingo próximo>.xlsx
      (el que la AMM publica el viernes); si no existe, termina con código 2.
  python run.py rep <carpeta_excels> <carpeta_salida> [semana]
      Último redespacho de la semana (sin semana: la más reciente con redespacho),
      comparado contra la versión inmediata anterior (original o redespacho previo).
"""
import sys, re, asyncio, datetime as dt
from pathlib import Path
from parse_pds import parse_file, merge_versions
from render import build_pre, build_rep, to_png


def index(folder):
    files = {}
    for f in Path(folder).glob('*.xlsx'):
        m = re.match(r'(\d+)_PDS(REP)?(\d{8})(?:\((\d+)\))?\.xlsx$', f.name, re.I)
        if not m: continue
        wk = int(m.group(1)); rev = int(m.group(4) or 0) if m.group(2) else 0
        files.setdefault(wk, []).append((rev, m.group(3), f))
    for wk in files: files[wk].sort(key=lambda x: (x[0], x[1]))
    return files


def main():
    mode, folder, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    idx = index(folder)
    wk = int(sys.argv[4]) if len(sys.argv) > 4 else None
    if mode == 'pre':
        if wk is None:
            today = dt.date.today()
            sunday = today + dt.timedelta(days=(6 - today.weekday()) % 7 or 7)
            tag = sunday.strftime('%Y%m%d')
            hits = [w for w, v in idx.items() for r, d, f in v if r == 0 and d == tag]
            if not hits:
                print(f'NO_ENCONTRADO: no hay predespacho *_PDS{tag}.xlsx en la carpeta'); sys.exit(2)
            wk = hits[0]
        cur = [x for x in idx[wk] if x[0] == 0][0][2]
        if wk - 1 not in idx:
            print(f'SIN_SEMANA_ANTERIOR: falta la semana {wk-1} para comparar'); sys.exit(3)
        prevs = [parse_file(x[2]) for x in idx[wk - 1]]   # original + redespachos de la semana anterior
        prev = merge_versions(prevs)                       # semana anterior vigente (con redespachos)
        html, s, p = build_pre(parse_file(cur), prev, cur.name, prev['file'])
        name = f'{wk:02d}_predespacho'
    else:
        if wk is None:
            wk = max(w for w, v in idx.items() if len(v) > 1)
        vers = idx[wk]
        if len(vers) < 2: print(f'La semana {wk} no tiene redespacho.'); sys.exit(2)
        parsed = [parse_file(x[2]) for x in vers]
        old = merge_versions(parsed[:-1])   # lo vigente antes de este redespacho
        new = parsed[-1]
        html, r = build_rep(old, new, old['file'], new['file'])
        name = f'{wk:02d}_redespacho({vers[-1][0]})'
    hp = out / f'{name}.html'; hp.write_text(html, encoding='utf-8')
    asyncio.run(to_png(hp, out / f'{name}.png'))
    hp.unlink()
    print('PNG:', out / f'{name}.png')


if __name__ == '__main__':
    main()
