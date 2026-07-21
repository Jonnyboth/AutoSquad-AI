---
name: qa-rads-tracker
description: >
  Infraestructura de captura y aserción de eventos rads-tracker (Ads/banners
  patrocinados) vía mitmproxy para el proyecto Rappi. Provee el pre-flight de
  conectividad, el algoritmo de journey (correlación por adToken) y las keywords
  canónicas. Cargar cuando cualquier skill (qa-flow-planner, qa-explorer,
  qa-test-creator, qa-debugger) o el Orquestador trabaje con eventos Ads,
  render/viewed_impression/click/add_to_cart/conversion, banners Sponsored Brand o
  Data Zero.
---

# qa-rads-tracker — Captura y aserción de eventos Ads (mitmproxy)

Conversión a Skill de `.github/agents/RADS-TRACKER.md` (preservado sin cambios en esa
ruta). Es infraestructura **compartida** — no tiene un paso propio en el pipeline; se
carga condicionalmente desde cualquiera de los otros 4 skills o desde el Orquestador.

## TL;DR

- La infra de captura vive en `mitm/` del proyecto (mitmproxy + addon Python,
  `mitm/addon/rads_addon.py`), con API HTTP local en `http://127.0.0.1:8082`.
- CLI cross-platform: `mitm/setup.py` (`mitm/setup.sh` Mac/Linux, `mitm/setup.bat` Windows).
- Antes de cualquier test con aserciones de eventos: verificar mitmproxy corriendo +
  device proxeado.
- Los TCs **nuevos** usan el algoritmo de JOURNEY (`RadsTrackerJourneySteps.*`) con
  correlación por `adToken`. Los keywords `RadsTrackerSteps.*` legacy solo quedan para
  compat backward de TCs ya existentes.
- ❌ No crear clientes HTTP/proxy ad-hoc — reutilizar siempre el addon existente.

## Comandos canónicos

```bash
bash mitm/setup.sh info             # IP, puertos, estado mitmproxy, device conectado
bash mitm/setup.sh start            # arranca mitmweb en background
bash mitm/setup.sh device           # configura proxy + CA cert en el device
bash mitm/setup.sh test             # valida que captura tráfico y eventos rads-tracker
bash mitm/setup.sh stop             # detiene mitmweb
bash mitm/setup.sh disable-device   # limpia proxy del device vía adb
```
En Windows: `mitm\setup.bat` en vez de `bash mitm/setup.sh`.

## Pre-flight obligatorio (todo skill que asegure eventos debe ejecutarlo)

```bash
curl -s http://127.0.0.1:8082/health   # esperado: {"ok":true,"flows":N,...}
```
Si falla: **no continuar** con generación/ejecución del test de aserciones. Instruir al
usuario a ejecutar `bash mitm/setup.sh start && bash mitm/setup.sh device`.

## API JSON del addon (puerto 8082)

| Endpoint | Uso |
|---|---|
| `GET /health` | `{ok, flows, events, tls_failures}` |
| `GET /flows?limit=50` | Últimos N flujos |
| `GET /events` | Todos los eventos capturados |
| `GET /events?type=<tipo>` | Filtro por tipo (`render`, `viewed_impression`, `click`, `add_to_cart`, `conversion`) |
| `GET /events?adToken=ADS-...` | Filtro por adToken |
| `GET /probe?host=<host>` | `{intercepted: true\|false}` |
| `POST /reset` | Limpia buffer — llamar al inicio de cada test que arme aserciones |

## Algoritmo de journey (obligatorio para TCs nuevos)

Detalle completo, reglas duras y keywords en `references/journey-algorithm.md`. Resumen
de las reglas no negociables:

1. `adToken` es la identidad **primaria** de correlación — nunca `placement`/`source`.
2. PRODUCT vs BANNER se decide por `price` (`> 0` → PRODUCT).
3. `render` es opcional, nunca ancla principal.
4. Anclaje fuerte: banner → `click`; producto → `click`/`add_to_cart`/`conversion`;
   producto visible sin click → `viewed_impression`.
5. No usar `viewed_impression` de banner post-navegación como ancla.
6. Duplicados `(type, adToken)` en el scope = **FAIL** (bug real de la app, no suprimir).

## Limitación conocida (Android 7+)

Si `mitm/setup.sh test` reporta tráfico TLS pero 0 eventos rads-tracker, la app no confía
en el CA de usuario. Opciones (en orden): APK de QA/debug de Rappi, device rooteado
(mover cert a `/system/etc/security/cacerts/`), emulador con `adb root`, Frida con bypass
de SSL pinning. Detalle en `mitm/README.md`.

## Anti-patrones (nunca generar)

- Clientes HTTP/proxy ad-hoc en Keywords.
- Asumir que el device ya está proxeado sin pre-flight.
- Aserciones débiles tipo "existe algún evento del tipo X" sin correlación por `adToken`.
- Usar `placement`/`source` como llave primaria de match.
- Tomar `viewed_impression` de banner después de navegar como evidencia del banner original.
- Suprimir o relajar un assert de duplicados — es una señal válida de bug en la app.

## Referencias

- `references/journey-algorithm.md` — algoritmo completo, tabla de reglas duras, cliente
  de eventos (`RadsTrackerEventsPage`), keywords semánticas (`RadsTrackerJourneySteps`)
  y patrón canónico en Script.
- Fuente original preservada: `.github/agents/RADS-TRACKER.md`
