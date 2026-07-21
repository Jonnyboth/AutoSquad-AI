# QA-Automatizador Pipeline State

RunId: QA-20260525-radstracker-events-sponsoredbrand
Fecha: 2026-05-25
Flujo: Trade | Data Zero Sponsored Brand FP — Validar banner, productos y eventos en [Rads Tracker]
Plataforma: android
Tipo: REFACTOR de TCs existentes (TestData0SearchStoreCorridor, TestData0SearchStoreHome) + aserción de 8 eventos `rads-tracker` capturados vía mint proxy.

## Estado actual
Phase: BLOCKED_PRE_FASE_1
RunnerRetryCount: 0

## Agentes invocados
- FlowPlanner: blocked (no invocado — bloqueo técnico previo)
- Explorer-Validate: pending
- Explorer-Capture: pending
- TestCreator: pending
- Runner: pending
- Debugger: pending

## PlanStatus actual
PlanStatus: N/A (no se generó plan — bloqueo)

## Bloqueo técnico detectado (pre-FASE 1)

El requerimiento exige aserciones sobre eventos HTTP `*/api/rads-tracker/event` capturados con mint proxy / Charles. Antes de invocar al FlowPlanner se realizó un descubrimiento exhaustivo del repo:

### Búsquedas ejecutadas
1. `grep -ril "mint|rads-tracker|mintproxy|charles|HAR|httpProxy|http_proxy" --include=*.groovy Keywords/ Include/ Drivers/` → **0 hits**
2. `grep -ril "rads|mint|adToken|viewed_impression|ADS-" en .groovy/.gradle/.xml/.properties/.json/.sh` → **0 hits** (excluyendo `bin/`, `.git/`)
3. Inspección de `Profiles/default.glbl` → sin proxy host/port ni claves de mint.
4. Inspección de `runner/src/main/groovy/runner/AppiumDriverManager.groovy` → no setea capabilities de proxy en Appium.
5. Inspección de `Libs/`, `Drivers/`, `runner/Include` → ningún cliente HTTP, ninguna lib de Charles/BrowserMob/mitm/mint.
6. `Keywords/com/rappi/page/android/` no contiene Page de eventos, tracker o network.

### Conclusión
**No existe integración previa con mint proxy ni con ninguna forma de captura HTTP en este proyecto Katalon.** Los TCs actuales son puramente UI (Appium/UIAutomator). No hay forma de aserciónar eventos `rads-tracker` sin añadir nueva infraestructura.

Continuar a FASE 1 (FlowPlanner) en estas condiciones sólo produciría un plan UI sin capa de network — no cumpliría el criterio de aceptación 2 (aserciones de evento). El protocolo del agent file indica explícitamente: *"Si NO existe integración previa con mint proxy, ese hecho debe quedar registrado en el plan como un bloqueo técnico, y BMO-Explorer debe validar la viabilidad antes de aprobar."*

Auto Mode → decisión tomada: **escalar al usuario con propuestas concretas de habilitación**, no fabricar mint inexistente.

## Propuestas concretas para desbloquear (elegir una antes de FASE 1)

### Opción A — Cliente lector del log mint/Charles (mínimo invasivo, recomendada si el QA ya corre mint externamente)
- El operador lanza mint proxy / Charles localmente con session-log a archivo (`~/charles-rads.chlsj` o `mint-events.ndjson`).
- Configurar Appium capability `appium:proxyType=manual`, `appium:httpProxy=<host>:<port>` en `AppiumDriverManager.groovy` (o en GlobalVariable `proxyHost/Port` de `Profiles/default.glbl`).
- Crear `Keywords/com/rappi/network/RadsTrackerProxyPage.groovy`:
  - `void startCapture()` — vacía el log a un buffer interno (timestamp inicio).
  - `List<Map> waitForEvent(String type, Map filters, int timeoutSec)` — polea el archivo, filtra entradas con path contiene `/api/rads-tracker/event`, parsea JSON body y filtra por `type` + atributos.
  - `void assertEvent(String type, Map requiredAttrs)` — wrapper que falla con `KeywordUtil.markFailed` si timeout.
- Steps: `RadsTrackerSteps.assertBannerRender()`, `assertBannerImpression()`, `assertBannerClick()`, `assertProductImpression()`, `assertProductClick()`, `assertAddToCart()`, `assertConversion(List items)`.
- Coste: ~1 Page + 1 Steps + 1 setup change en AppiumDriverManager. Sin dependencias externas nuevas (solo `groovy.json.JsonSlurper`, ya en classpath).

### Opción B — BrowserMob/Proxy embebido en el runner
- Añadir `net.lightbody.bmp:browsermob-core` a `runner/build.gradle`.
- Levantar `BrowserMobProxy` en `AppiumDriverManager.setUp()`, pasar `proxy` capability al `AndroidDriver`.
- Filtrar `RequestFilter` por path `rads-tracker/event`, almacenar en lista thread-safe.
- Page/Steps similares a Opción A pero leen de la lista en memoria (más confiable, sin I/O de archivo).
- Coste: 1 dependencia gradle + cert install en device (Android 7+ requiere user-cert install para HTTPS — paso manual una vez por device).

### Opción C — mitmproxy externo + addon Python
- Operador corre `mitmdump -s rads_capture.py --listen-port 8888` que escribe a `rads-events.ndjson`.
- Página Groovy lee tail del archivo (similar a Opción A).
- Coste: requiere instalar mitmproxy en máquina del QA; cert install en device. Menos integrado al pipeline Katalon.

### Recomendación
**Opción A** si Charles/mint ya forma parte del workflow del equipo (asumido por el nombre "mint proxy" en el ticket). **Opción B** si se quiere integración 100% headless sin dependencia externa.

## Acciones requeridas del usuario

1. Confirmar qué opción adoptar (A / B / C).
2. Si Opción A: indicar **ruta exacta** del session log de mint y formato (`.chlsj`, `.har`, `.ndjson`).
3. Confirmar host/puerto del proxy y si los devices ya tienen el cert instalado (HTTPS) — sin cert, `rads-tracker` (HTTPS) no será desencriptable.
4. Confirmar credenciales / dirección Geant Arenal Grande 2076, Montevideo UY ya configuradas en setUp existente (revisar `Profiles/default.glbl`).

Una vez confirmada la opción, el pipeline reanuda:
- FASE 0 (nueva): habilitar capa de captura (Page + Steps + setUp change).
- FASE 1: FlowPlanner con plan E2E que incluye los 8 puntos de aserción.
- FASE 2A/2B/3/5/5B según protocolo estándar.

## Archivos generados
- Context orchestrator: `.github/agents/context/orchestrator/QA-20260525-radstracker-events-sponsoredbrand.md` (este archivo)
- Context flowplanner: pending (bloqueado)
- .rs creados: ninguno
- Files de código: ninguno

## Reporte final
Pipeline detenido en pre-FASE 1 por gap de infraestructura. Ver propuestas Opción A/B/C arriba.
