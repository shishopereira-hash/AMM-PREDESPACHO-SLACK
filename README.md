# AMM-PREDESPACHO-SLACK

Imágenes del predespacho y redespacho semanal de la AMM (línea gráfica ER), publicadas en el canal **#despacho-semanal** de Slack.

## Cómo funciona
1. GitHub Actions revisa la AMM (`pds.php`, la misma lista de *Planificación → Semanales → Despacho Semanal*):
   los viernes revisa cada minuto desde las 2:35 PM hasta que sale el predespacho (workflow "Vigilar predespacho del viernes"), y cada hora de 6 AM a 10 PM para redespachos.
2. Si hay un predespacho o redespacho nuevo, lo descarga a `data/2026/`
   (`NN_PDSyyyymmdd.xlsx` o `NN_PDSREPyyyymmdd(k).xlsx`), genera la imagen y la publica en Slack con un resumen.
   También se puede subir un Excel a mano a `data/2026/` y se publica igual.
3. La imagen queda en `imagenes/2026/` y el archivo se anota en `data/publicados.txt`.

- **Predespacho:** se compara contra la semana anterior vigente (original + redespachos).
- **Redespacho:** se compara contra la versión inmediata anterior en los días que cambia.

## Volver a publicar o probar
Pestaña **Actions → Publicar predespacho / redespacho en Slack → Run workflow**.
En "forzar" se puede poner el nombre exacto de un Excel para volver a publicarlo.

## Secretos necesarios (Settings → Secrets and variables → Actions)
- `SLACK_BOT_TOKEN`: token `xoxb-...` de la app *Predespacho AMM*.
- `SLACK_CHANNEL_ID`: ID del canal (`C0BUDFD8VA4`).

## Criterios
- Hidroeléctricas sin Chixoy; Chixoy aparte. % del mix sobre la suma de tecnologías (sin MER).
- Costo = energía diaria × CVG vigente ese día (hoja CVG). LA UNIÓN B1 = LUN-B.
- Mantenimientos: se leen todas las filas de la hoja.
- Nota AMM del redespacho = observaciones nuevas respecto a la versión anterior.

## Alarmas del SNI (#alarmas-sni)
- Workflow *Alarmas del SNI en Slack*: todos los días a las **2:00 PM** revisa el posdespacho de ayer
  (hojas RSO e Indisponibilidades) con `scripts/alarmas.py` y publica en **#alarmas-sni** solo estos eventos, todos con el mismo encabezado
  **"⚠️ EVENTO EN EL SNI"** (el mensaje no dice si es grave o emergencia; la clasificación es interna):
  - 🔴 **EMERGENCIA**: ≥100 MW de carga desconectada en Guatemala, o ≥150 MW de generación/importación perdida.
  - 🟠 **GRAVE**: EDACBF; 20–100 MW de carga; 50–150 MW de generación; medidas NCC-10; corte manual de carga;
    disparos de 230/400 kV (≥60 min o con carga afectada); varias subestaciones sin tensión ≥30 min;
    disparo de interconexión con RRA convocada; disparo de la interconexión 400 kV Guatemala – México;
    frecuencia mínima por debajo de 59.5 Hz; salida forzada de una unidad ≥100 MW.
- Cada evento trae hora, el dato (MW, kV, Hz, minutos) y el texto del RSO, en orden de hora.
- Días sin emergencias ni graves: se publica un aviso corto "✅ Sin eventos en el SNI el …". Registro en `data/publicados_alarmas.txt`.
- Umbrales: `UMBRAL` en `programa/clasificador_eventos.py`. Potencia por central: `data/centrales_mw.json`.
- Secreto extra: `SLACK_ALARMAS_CHANNEL` = ID del canal #alarmas-sni (la app debe estar invitada al canal).
- Probar un día: *Actions → Alarmas del SNI en Slack → Run workflow* con la fecha `AAAAMMDD`
  (en local: `python scripts/alarmas.py --fecha 20260607 --prueba`).

## PosDespacho diario
- La AMM publica cada día (~12:00 PM) el posdespacho del día anterior en
  `pdfs2/post_despacho/POSDESPACHO_DIARIO/AAAA/MM_MES/PDaaaammdd.zip`.
- `scripts/posdespacho.py` lo descarga a `data/posdespacho/AAAA/`, lo compara contra el programa semanal
  vigente (original + redespachos de esa semana) y publica la imagen `imagenes/AAAA/PD_aaaammdd.png` en Slack.
- Workflow: *Publicar posdespacho diario en Slack* (vigila la AMM cada minuto desde las 11:35 AM hasta que sale, y cada hora de 3 a 5 PM si se atrasa).
- Criterios: hidroeléctricas sin Chixoy (Chixoy aparte); 3 desviaciones positivas y 3 negativas por tecnología;
  la importación de oportunidad de México = importación total desde México − Energía del Caribe;
  el intercambio MER no se compara; plantas en cascada/bloques/unidades se suman (Renace I–IV, INDE, Xacbal + Delta, Jaguar, Pantaleón...).

## Control de zafra (ingenios) — uso interno
- Cada día, en cuanto sale el posdespacho, se publica en **#despacho-semanal** la hoja *Control diario · Zafra*
  (estilo propio, oscuro verde/ámbar): energía, CVG, Pmax, factor de planta y acumulado por bloque,
  salidas y fallas del día (hoja Indisponibilidades + RSO) y alertas.
- Alertas: inicio/fin de zafra; bloque sin generación; baja ≥ 15 % contra el día anterior; baja ≥ 10 % del total;
  factor de planta < 50 %; salidas forzadas/disparos; cambio de CVG.
- Factor de planta = energía ÷ (Pmax × 24 h). Pmax: `data/zafra/pmax.json` (del predespacho diario; valor vigente = el último con fecha ≤ día).
- Estado de zafra: `data/zafra/estado.json` (arrancó con la Hoja4 del Directorio al 25-nov-2026). El bot marca el
  **inicio** el primer día con CVG < 30 y generación > 0, y el **fin** cuando el CVG sube (ayer < 30, hoy ≥ 40 y > 3×).
  Se puede corregir a mano (fechas `inicio` / `fin`). MAG-B4 tiene CVG bajo todo el año: su fin se pone a mano.
- Script: `scripts/zafra.py` (lógica en `programa/zafra_datos.py`, imagen en `programa/render_zafra.py`). Registro: `data/publicados_zafra.txt`.
- Workflow de respaldo: *Control de zafra en Slack* (2:10 PM y 3:45–5:45 PM; *Run workflow* con fecha `AAAAMMDD` para re-publicar).
  Para dispararlo desde cron-job.org: `POST https://api.github.com/repos/shishopereira-hash/AMM-PREDESPACHO-SLACK/actions/workflows/zafra.yml/dispatches`
  con el encabezado `Authorization: Bearer <token>` y el cuerpo `{"ref":"main"}`.
- Canal: el mismo de los predespachos (`SLACK_CHANNEL_ID`). Si algún día se quiere otro canal, crear el secreto `SLACK_ZAFRA_CHANNEL`.
- Prueba local: `python scripts/zafra.py --fecha 20261125 --prueba`.
