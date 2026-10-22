# AMM-PREDESPACHO-SLACK

Imágenes del predespacho y redespacho semanal de la AMM (línea gráfica ER), publicadas en el canal **#despacho-semanal** de Slack.

## Cómo funciona
1. Se sube el Excel de la AMM a `data/2026/` con su nombre original
   (`NN_PDSyyyymmdd.xlsx` o `NN_PDSREPyyyymmdd(k).xlsx`).
2. GitHub Actions detecta el archivo nuevo, genera la imagen y la publica en Slack con un resumen.
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
