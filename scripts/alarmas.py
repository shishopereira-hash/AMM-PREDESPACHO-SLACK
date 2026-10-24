"""Alarmas del SNI: lee el posdespacho de ayer (RSO e Indisponibilidades), clasifica cada evento
y publica en Slack (#alarmas-sni) lo que sea EMERGENCIA o GRAVE; si no hubo, un aviso corto de "sin alarmas".

- Usa el Excel que deja scripts/posdespacho.py en data/posdespacho/AAAA/PDaaaammdd.xlsx;
  si todavía no está, lo descarga de la AMM.
- Niveles y umbrales: programa/clasificador_eventos.py (UMBRAL).
- Registro: data/publicados_alarmas.txt  (fecha + resultado), para no repetir.

Uso: python scripts/alarmas.py                    (posdespacho de ayer)
     python scripts/alarmas.py --fecha 20260607   (un día en particular; vuelve a publicar)
     python scripts/alarmas.py --prueba            (no publica, solo imprime el mensaje)
     python scripts/alarmas.py --ayer-listo        (código 0 si lo de ayer ya se revisó)
"""
import os, sys, json, re, datetime as dt
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'programa'))
sys.path.insert(0, str(ROOT / 'scripts'))
import clasificador_eventos as K                       # noqa: E402
import lector_posdespacho as L                         # noqa: E402

POS = ROOT / 'data' / 'posdespacho'
LOG = ROOT / 'data' / 'publicados_alarmas.txt'
CENTRALES = json.loads((ROOT / 'data' / 'centrales_mw.json').read_text(encoding='utf-8'))
GT = dt.timezone(dt.timedelta(hours=-6))
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']
DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
MAX_POR_NIVEL = 12


def archivo_del_dia(d):
    f = POS / str(d.year) / f'PD{d:%Y%m%d}.xlsx'
    if not f.exists():
        from posdespacho import descargar               # descarga lo que falte de la última semana
        descargar()
    return f if f.exists() else None


def clasificar_dia(f, d):
    eventos, vistos = [], set()
    for e in L.leer_rso(f):
        n, fam, mot = K.clasificar_evento(e, vistos)
        if n >= 3:
            eventos.append({'nivel': n, 'familia': fam, 'motivo': mot, 'hora': e.get('h_ini'),
                            'hora_fin': e.get('h_fin'), 'texto': e['texto']})
    for x in L.leer_indisp(f, d):
        c = CENTRALES.get(x['central'], {})
        x['mw_unidad'] = c.get('mw_unidad')
        n, fam, mot = K.clasificar_indisp(x)
        if n >= 3:
            hora = (x.get('sale') or '')[11:16] or None
            eventos.append({'nivel': n, 'familia': fam, 'hora': hora, 'hora_fin': None,
                            'motivo': f"{x['unidad']} ({c.get('nombre') or x['central']}): {mot}",
                            'texto': f"{x['tipo']}. {x.get('obs') or ''}".strip()})
    eventos.sort(key=lambda e: (-e['nivel'], e['hora'] or '99'))
    return eventos


def _corto(t, n=280):
    t = re.sub(r'\s+', ' ', t or '').strip()
    return t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0] + '…'


def mensaje(d, eventos):
    fecha = f'{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}'
    emer = [e for e in eventos if e['nivel'] == 4]
    grav = [e for e in eventos if e['nivel'] == 3]
    titulo = '🔴 EMERGENCIA en el SNI' if emer else '🟠 Evento GRAVE en el SNI'
    resumen = ' · '.join(x for x in [f'{len(emer)} emergencia(s)' if emer else '',
                                     f'{len(grav)} grave(s)' if grav else ''] if x)
    blocks = [
        {'type': 'header', 'text': {'type': 'plain_text', 'text': titulo, 'emoji': True}},
        {'type': 'context', 'elements': [{'type': 'mrkdwn',
            'text': f'Operación del *{fecha}* · {resumen} · fuente: posdespacho AMM (RSO e Indisponibilidades)'}]},
    ]
    for nivel, grupo, icono, etiqueta in [(4, emer, '🔴', 'EMERGENCIA'), (3, grav, '🟠', 'GRAVE')]:
        if not grupo:
            continue
        blocks.append({'type': 'divider'})
        for e in grupo[:MAX_POR_NIVEL]:
            hora = e['hora'] + (f"–{e['hora_fin']}" if e.get('hora_fin') else '') + ' h · ' if e['hora'] else ''
            blocks.append({'type': 'section', 'text': {'type': 'mrkdwn',
                'text': f"{icono} *{etiqueta}* · {hora}*{e['motivo']}*\n>{_corto(e['texto'])}"}})
        if len(grupo) > MAX_POR_NIVEL:
            blocks.append({'type': 'context', 'elements': [{'type': 'mrkdwn',
                'text': f'… y {len(grupo) - MAX_POR_NIVEL} evento(s) {etiqueta.lower()} más en el posdespacho.'}]})
    texto = f"{titulo} — {fecha}: " + '; '.join(f"{'EMERGENCIA' if e['nivel'] == 4 else 'GRAVE'}: {e['motivo']}"
                                               for e in eventos[:5])
    return texto, blocks


def slack_post(texto, blocks):
    token = os.environ.get('SLACK_BOT_TOKEN')
    canal = os.environ.get('SLACK_ALARMAS_CHANNEL') or 'alarmas-sni'
    if not token:
        print('(sin SLACK_BOT_TOKEN: no se publica)'); return False
    r = requests.post('https://slack.com/api/chat.postMessage',
                      headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json; charset=utf-8'},
                      data=json.dumps({'channel': canal, 'text': texto, 'blocks': blocks, 'unfurl_links': False}),
                      timeout=60).json()
    if not r.get('ok'):
        if r.get('error') in ('not_in_channel', 'channel_not_found'):
            raise RuntimeError(f"Slack: {r.get('error')}. Invitá la app al canal #alarmas-sni (/invite @Predespacho AMM) "
                               "o poné el ID del canal en el secreto SLACK_ALARMAS_CHANNEL.")
        raise RuntimeError(f'Slack chat.postMessage: {r}')
    return True


def registrados():
    if not LOG.exists():
        return {}
    return dict(l.split(maxsplit=1) for l in LOG.read_text(encoding='utf-8').splitlines() if l.strip())


def anotar(tag, resultado):
    reg = registrados(); reg[tag] = resultado
    LOG.write_text(''.join(f'{k} {v}\n' for k, v in sorted(reg.items())), encoding='utf-8')


def correr(d, prueba=False, forzar=False):
    tag = f'{d:%Y%m%d}'
    if not forzar and not prueba and tag in registrados():
        print(f'{tag}: ya revisado ({registrados()[tag]})'); return True
    f = archivo_del_dia(d)
    if f is None:
        print(f'{tag}: el posdespacho todavía no está en la AMM'); return False
    eventos = clasificar_dia(f, d)
    if not eventos:
        fecha = f'{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]} de {d.year}'
        texto = f'✅ Sin emergencias ni graves en el SNI el {fecha}'
        blocks = [{'type': 'section', 'text': {'type': 'mrkdwn', 'text': f'✅ *Sin emergencias ni graves* en el SNI el *{fecha}*'}},
                  {'type': 'context', 'elements': [{'type': 'mrkdwn',
                   'text': 'Revisado el posdespacho AMM (RSO e Indisponibilidades).'}]}]
        if prueba:
            print(texto); return True
        if slack_post(texto, blocks):
            anotar(tag, 'sin-alarmas'); print(f'{tag}: publicado "sin alarmas" en Slack')
        return True
    texto, blocks = mensaje(d, eventos)
    if prueba:
        print(texto); print(json.dumps(blocks, ensure_ascii=False, indent=1)); return True
    if slack_post(texto, blocks):
        n4 = sum(e['nivel'] == 4 for e in eventos); n3 = len(eventos) - n4
        anotar(tag, f'publicado E{n4}-G{n3}'); print(f'{tag}: publicado en Slack ({n4} emergencias, {n3} graves)')
    return True


if __name__ == '__main__':
    ayer = dt.datetime.now(GT).date() - dt.timedelta(days=1)
    if '--ayer-listo' in sys.argv:
        sys.exit(0 if f'{ayer:%Y%m%d}' in registrados() else 1)
    if '--fecha' in sys.argv:
        d = dt.datetime.strptime(sys.argv[sys.argv.index('--fecha') + 1], '%Y%m%d').date()
        ok = correr(d, prueba='--prueba' in sys.argv, forzar=True)
    else:
        ok = correr(ayer, prueba='--prueba' in sys.argv)
    sys.exit(0 if ok else 3)                          # 3 = todavía no hay posdespacho
