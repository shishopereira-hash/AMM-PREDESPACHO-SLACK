# AMM-PREDESPACHO-SLACK

Imágenes del predespacho y redespacho semanal de la AMM (línea gráfica ER), publicadas en el canal **#despacho-semanal** de Slack.

## Cómo funciona
1. GitHub Actions revisa la AMM (`pds.php`, la misma lista de *Planificación → Semanales → Despacho Semanal*):
   cada 10 min los viernes de 3 a 6 PM y cada hora de 6 AM a 10 PM los demás días.
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

## PosDespacho diario
- La AMM publica cada día (~12:00 PM) el posdespacho del día anterior en
  `pdfs2/post_despacho/POSDESPACHO_DIARIO/AAAA/MM_MES/PDaaaammdd.zip`.
- `scripts/posdespacho.py` lo descarga a `data/posdespacho/AAAA/`, lo compara contra el programa semanal
  vigente (original + redespachos de esa semana) y publica la imagen `imagenes/AAAA/PD_aaaammdd.png` en Slack.
- Workflow: *Publicar posdespacho diario en Slack* (vigila la AMM cada minuto desde las 11:35 AM hasta que sale, y cada hora de 3 a 5 PM si se atrasa).
- Criterios: hidroeléctricas sin Chixoy (Chixoy aparte); 3 desviaciones positivas y 3 negativas por tecnología;
  la importación de oportunidad de México = importación total desde México − Energía del Caribe;
  el intercambio MER no se compara; plantas en cascada/bloques/unidades se suman (Renace I–IV, INDE, Xacbal + Delta, Jaguar, Pantaleón...).
