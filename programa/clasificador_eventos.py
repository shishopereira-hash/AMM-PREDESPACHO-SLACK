"""
Clasificador de eventos del posdespacho (AMM) para alertas del bot.

Niveles:
  4 EMERGENCIA     -> alerta inmediata
  3 GRAVE          -> alerta
  2 HAY QUE SABER  -> va en un resumen del día (un solo mensaje), sin alerta
  1 RUTINA         -> no se envía

Entrada de un evento RSO (dict):
  texto (str, obligatorio), tipo, ambito, kv (float), carga_afectada (bool),
  mw_gen_perdida (float), dur_min (int)
Entrada de una indisponibilidad (dict):
  unidad, central, cat (Forzada / Disparo de Unidad / Falla al ser Convocado /
  Mantenimiento / Degradación / No atribuible / Causa Externa), nueva (bool: inició ese día),
  mw_unidad (float, aprox.), obs
Cada función devuelve (nivel:int, familia:str, motivo:str).
Los umbrales están juntos en UMBRAL para ajustarlos sin tocar la lógica.
"""
import re

NIVELES = {4: "EMERGENCIA", 3: "GRAVE", 2: "HAY QUE SABER", 1: "RUTINA"}

UMBRAL = dict(
    carga_emerg=100,   # MW de carga desconectada en Guatemala -> emergencia
    carga_grave=20,    # MW de carga desconectada en Guatemala -> grave
    gen_emerg=150,     # MW de generación perdida en Guatemala -> emergencia
    gen_grave=50,      # MW de generación perdida en Guatemala -> grave
    gen_saber=20,
    ser_saber=300,     # MW perdidos en otro país del SER que vale la pena mencionar
    min_sin_tension_grave=120, # min de carga sin servicio por falla -> grave
    min_multi_se_grave=30,     # min con varias subestaciones sin tensión -> grave
    min_troncal_grave=60,      # min fuera de una línea 230/400 kV disparada -> grave
    ind_grave=100,     # MW de la unidad en indisponibilidad forzada nueva -> grave
    ind_saber=50,
)

_I = re.I
RX = dict(
    edacbf=re.compile(r"EDACBF|EDCABF|baja frecuencia|etapa del EDA", _I),
    edacbv=re.compile(r"EDACBV|esquema (de )?(protecci[oó]n )?(de desconexi[oó]n de carga )?(por )?bajo voltaje|por esquema de bajo", _I),
    desc_manual=re.compile(r"desconect\w+ (la |parte de la )?carga|desconexi[oó]n de carga|reducir (la )?demanda|carga de manera manual", _I),
    ncc10=re.compile(r"NCC-10|Medidas Administrativas|falta de disponibilidad de energ", _I),
    rra=re.compile(r"Reserva R[aá]pida|\bR\.?\s?RA\b|\bRRa\b", _I),
    inter=re.compile(r"interconexi", _I),
    inter_disp=re.compile(r"(disparo|apertura|abiert\w+|abri\w+|desconexi[oó]n autom)[^.]{0,80}interconexi|interconexi[^.]{0,120}(disparo|EDALTIBV|ESIM|protecci)|EDALTIBV|ESIM\w*", _I),
    disparo=re.compile(r"dispar|abiert\w+ por disparo|falla", _I),
    multi_se=re.compile(r"sin (tensi[oó]n|servicio) (las|a las) (S/E|subestaciones)|(quedaron|quedando|dejando|perdieron tensi[oó]n) [^.]{0,30}subestaciones", _I),
    programado=re.compile(r"mantenimiento|AMM-[A-Z]{3}\d{0,4}-|programad|trabajos", _I),
    alta=re.compile(r"habilitad\w+ en el Mercado|de baja (del|en el) Mercado", _I),
    nota=re.compile(r"^A partir del \d+ de \w+ de \d{4}", _I),
    troncal=re.compile(r"(l[ií]nea|interruptor\w*|circuito)\s+(de\s+)?(230|400)\s*kV", _I),
    extranjero=re.compile(r"Panam[aá]|Nicaragua|Honduras|El Salvador|Costa Rica|Minera|Energ[ií]a del Pac", _I),
)
_MW_CARGA = re.compile(r"(?P<antes>[^.;·]{0,60})\b([\d]+(?:[.,]\d+)?)\s*MW de carga(?P<cola>[^.;·]{0,50})", _I)
_MW_GEN = re.compile(r"(?P<antes>[^.;·]{0,60})(?:p[ée]rdida de (?:aproximadamente )?|perdi\w+ |p[ée]rdida de generaci[oó]n de aproximadamente )([\d]+(?:[.,]\d+)?)\s*MW(?P<cola>[^.;·]{0,60})", _I)
_EXT_ANTES = re.compile(r"(sistema el[ée]ctrico|S\.?\s?N\.?\s?I\.?|[aá]rea de control) de (Panam|Nicaragua|Honduras|El Salvador|Costa Rica|M[eé]xico)|(en|de) (Panam[aá]|Nicaragua|Honduras|El Salvador|Costa Rica|M[eé]xico) (tuvo|hubo|se|report)|M[eé]xico report", _I)
_EXT = re.compile(r"Panam[aá]|Nicaragua|Honduras|El Salvador|Costa Rica|SER\b|Minera|(?<!desde el sistema el[ée]ctrico de )(?<!desde )M[eé]xico\b(?! a Guatemala)|[aá]rea de control de (?!Guatemala)|mexican|paname|salvadore|hondure|nicarag|costarric", _I)


def _n(x):
    """Número seguro: None/NaN/texto -> 0."""
    try:
        x = float(x)
        return 0.0 if x != x else x
    except Exception:
        return 0.0


def _f(s):
    try:
        return float(s.replace(",", "."))
    except Exception:
        return 0.0


def mw_carga_gt(t):
    """Máximo MW de carga desconectada en Guatemala (descarta los de otros países)."""
    xs = [_f(m.group(2)) for m in _MW_CARGA.finditer(t)
          if not _EXT.search(m.group("cola")) and not _EXT_ANTES.search(m.group("antes"))]
    return max(xs, default=0.0)


def mw_gen(t, dato=None):
    """(MW gen perdida en Guatemala, MW perdidos fuera)."""
    gt, ext = [0.0], [0.0]
    for m in _MW_GEN.finditer(t):
        v, cola = _f(m.group(2)), m.group("cola")
        if re.match(r"\s*de carga", cola, _I):
            continue  # es carga, no generación
        (ext if _EXT.search(cola) or _EXT_ANTES.search(m.group("antes")) else gt).append(v)
    ext += [_f(m.group(2)) for m in _MW_CARGA.finditer(t)
            if _EXT.search(m.group("cola")) or _EXT_ANTES.search(m.group("antes"))]
    if _EXT_ANTES.search(t) and dato and not gt[1:]:
        ext.append(dato)
        dato = 0
    # el dato ya extraído del RSO solo cuenta si el texto no lo atribuye a otro país
    if dato and not any(abs(dato - x) < 0.5 for x in ext):
        gt.append(dato)
    return max(gt), max(ext)


def familia_evento(e):
    t, tipo = e["texto"], e.get("tipo") or ""
    if RX["ncc10"].search(t): return "Medidas NCC-10 (falta de energía)"
    if RX["edacbf"].search(t) or (RX["inter_disp"].search(t) and RX["inter"].search(t) and "Cerrada la interconexi" not in t[:25]):
        return "Disturbio regional / disparo de interconexión"
    if tipo == "Reserva Rápida (RRa)" or RX["rra"].search(t): return "Reserva Rápida"
    if RX["edacbv"].search(t) or RX["desc_manual"].search(t): return "Bajo voltaje / desconexión de carga"
    if tipo == "Interconexión": return "Interconexión (estado diario)"
    if tipo == "Disparo / falla": return "Disparo en transmisión / distribución"
    if tipo == "Mantenimiento / maniobra": return "Mantenimiento y maniobras"
    if tipo == "Generación forzada": return "Generación forzada"
    if tipo == "Pruebas": return "Pruebas de unidades"
    if tipo == "Redespacho": return "Redespacho del PDD"
    if RX["alta"].search(t) or tipo == "Altas / bajas de centrales": return "Altas / bajas de centrales"
    if tipo == "Nota regulatoria": return "Nota regulatoria"
    return "Otros"


def clasificar_evento(e, notas_vistas=None):
    t = e["texto"]; kv = _n(e.get("kv")); tipo = e.get("tipo") or ""
    fam = familia_evento(e)
    carga = mw_carga_gt(t)
    gen_gt, gen_ext = mw_gen(t, _n(e.get("mw_gen_perdida")))
    dur = int(_n(e.get("dur_min")))
    afect = e.get("carga_afectada") is True
    prog = bool(RX["programado"].search(t)) and tipo in ("Mantenimiento / maniobra",)
    inter_disp = fam == "Disturbio regional / disparo de interconexión"

    # ---- EMERGENCIA
    if carga >= UMBRAL["carga_emerg"]:
        return 4, fam, f"Se desconectaron {carga:.0f} MW de carga en Guatemala"
    if gen_gt >= UMBRAL["gen_emerg"]:
        return 4, fam, f"Pérdida de {gen_gt:.0f} MW de generación/importación para Guatemala"

    # ---- GRAVE
    if RX["edacbf"].search(t):
        return 3, fam, "Actuó el esquema de desconexión de carga por baja frecuencia (EDACBF)"
    if carga >= UMBRAL["carga_grave"]:
        return 3, fam, f"Se desconectaron {carga:.0f} MW de carga en Guatemala"
    if gen_gt >= UMBRAL["gen_grave"]:
        return 3, fam, f"Pérdida de {gen_gt:.0f} MW de generación/importación para Guatemala"
    if fam == "Medidas NCC-10 (falta de energía)":
        return 3, fam, "Medidas administrativas NCC-10 por falta de disponibilidad de energía"
    if RX["desc_manual"].search(t) and not prog and not RX["edacbv"].search(t):
        return 3, fam, "Desconexión manual de carga para sostener voltaje / balance"
    m_tr = RX["troncal"].search(t)
    troncal = tipo == "Disparo / falla" and m_tr and not RX["inter"].search(t)
    if troncal: kv = float(m_tr.group(3))
    if troncal and (afect or dur >= UMBRAL["min_troncal_grave"]):
        return 3, fam, f"Disparo de línea de {kv:.0f} kV ({dur} min fuera)" if dur else f"Disparo de línea de {kv:.0f} kV con afectación"
    multi = tipo in ("Disparo / falla", "Otro") and RX["multi_se"].search(t)
    if multi and dur >= UMBRAL["min_multi_se_grave"]:
        return 3, fam, f"Varias subestaciones sin tensión por falla ({dur} min)"
    if tipo == "Disparo / falla" and afect and kv >= 138 and dur >= UMBRAL["min_sin_tension_grave"]:
        return 3, fam, f"Carga sin servicio {dur // 60} h {dur % 60} min por falla"
    if inter_disp and (fam == "Reserva Rápida" or RX["rra"].search(t)):
        return 3, fam, "Disparo de interconexión con convocatoria de Reserva Rápida"

    # ---- HAY QUE SABER
    if troncal:
        return 2, fam, f"Disparo breve de línea de {kv:.0f} kV, sin afectación"
    if multi:
        return 2, fam, "Varias subestaciones sin tensión por pocos minutos"
    if RX["desc_manual"].search(t) and not prog:
        return 2, fam, "Desconexión de carga local por esquema de bajo voltaje"
    if inter_disp:
        return 2, fam, "Disparo/apertura de interconexión sin pérdida de carga relevante en Guatemala"
    if fam == "Reserva Rápida":
        return 2, fam, "Se convocó Reserva Rápida"
    if RX["edacbv"].search(t):
        return 2, fam, "Actuó esquema por bajo voltaje (afectación local)"
    if tipo == "Disparo / falla" and (afect or kv >= 138):
        return 2, fam, "Disparo con carga afectada" if afect else f"Disparo en {kv:.0f} kV"
    if gen_gt >= UMBRAL["gen_saber"]:
        return 2, fam, f"Pérdida de {gen_gt:.0f} MW de generación"
    if gen_ext >= UMBRAL["ser_saber"]:
        return 2, fam, f"Evento grande en el SER ({gen_ext:.0f} MW)"
    if fam == "Altas / bajas de centrales":
        return 2, fam, "Alta o baja de central en el Mercado Mayorista"
    if fam == "Nota regulatoria":
        clave = t[:80]
        if notas_vistas is not None:
            if clave in notas_vistas: return 1, fam, "Nota regulatoria repetida"
            notas_vistas.add(clave)
        return 2, fam, "Nota regulatoria nueva"
    if tipo == "Interconexión" and RX["disparo"].search(t):
        return 2, fam, "Interconexión abierta por falla"
    return 1, fam, "Operación de rutina"


def clasificar_indisp(x):
    cat, mw = x.get("cat"), x.get("mw_unidad") or 0
    if not x.get("nueva"): return 1, "Indisponibilidad", "Continúa de días anteriores"
    if cat in ("Forzada", "Disparo de Unidad", "Falla al ser Convocado"):
        if mw >= UMBRAL["ind_grave"]: return 3, "Indisponibilidad forzada", f"Salida forzada de unidad de ~{mw:.0f} MW"
        if mw >= UMBRAL["ind_saber"] or cat == "Falla al ser Convocado":
            return 2, "Indisponibilidad forzada", f"{cat} de unidad de ~{mw:.0f} MW"
    return 1, "Indisponibilidad", "Rutina"


ICONO = {4: "🔴", 3: "🟠", 2: "🟡"}


def mensaje_del_dia(fecha, eventos, indisp=()):
    """
    eventos / indisp: listas de tuplas (nivel, familia, motivo, texto, hora).
    Devuelve el texto del mensaje, o None si el día fue de rutina (no se envía nada).
    Emergencia o Grave -> alerta. Si solo hay "Hay que saber" -> resumen corto.
    """
    xs = sorted([x for x in list(eventos) + list(indisp) if x[0] >= 2], key=lambda x: (-x[0], x[4] if isinstance(x[4], str) else "99"))
    if not xs:
        return None
    top = xs[0][0]
    cab = {4: "🔴 EMERGENCIA en el SNI", 3: "🟠 Evento grave en el SNI", 2: "🟡 Para tener en cuenta"}[top]
    lin = [f"*{cab}* — operación del {fecha} (posdespacho AMM)"]
    for n in (4, 3, 2):
        grupo = [x for x in xs if x[0] == n]
        if not grupo:
            continue
        if n == 2 and top >= 3:
            lin.append(f"🟡 Además: {len(grupo)} evento(s) para tener en cuenta (" +
                       "; ".join(sorted({g[2] for g in grupo})[:3]) + ")")
            continue
        for g in grupo[:5]:
            h = f"{g[4]} h · " if isinstance(g[4], str) and g[4] else ""
            lin.append(f"{ICONO[n]} {h}{g[2]}")
        if len(grupo) > 5:
            lin.append(f"   … y {len(grupo) - 5} más")
    return "\n".join(lin)
