# Captura y aserción de eventos `rads-tracker` (mitmproxy)

> **Referencia compartida por todos los agentes BMO/QA**. Cualquier flujo que pruebe eventos Ads (`rads-tracker`) DEBE usar esta infraestructura. No improvisar otra captura.

## TL;DR — Lo que siempre hay que recordar

- La infra de captura **existe en `mitm/`** del proyecto. Es la **Opción C** (mitmproxy + addon Python).
- El addon corre en `mitm/addon/rads_addon.py` y expone una **API HTTP local en `http://127.0.0.1:8082`** con los eventos parseados.
- El CLI cross-platform es `mitm/setup.py` (wrappers: `mitm/setup.sh` Mac/Linux, `mitm/setup.bat` Windows).
- Antes de cualquier test con aserciones de eventos: **verificar mitmproxy corriendo + device proxeado**. Si no lo está, ayudar al usuario a configurarlo con los comandos de abajo.
- **Los asserts NUEVOS usan el algoritmo de JOURNEY con correlación por `adToken`** (ver sección abajo). Los keywords `RadsTrackerSteps.*` legacy quedan solo para compat backward; los TCs nuevos DEBEN usar `RadsTrackerJourneySteps.*`.

## Comandos canónicos

```bash
# 1) Ver estado: IP del host, puertos, mitmproxy on/off, device conectado
bash mitm/setup.sh info

# 2) Arrancar mitmweb en background (logs en ~/.mitmproxy/mitmweb.log)
bash mitm/setup.sh start

# 3) Configurar el device (proxy + push del CA cert + guía táctil para confiarlo)
bash mitm/setup.sh device

# 4) Validar que el device manda tráfico al proxy y aparecen eventos rads-tracker
bash mitm/setup.sh test

# 5) Parar
bash mitm/setup.sh stop

# 6) Desactivar proxy del device Samsung (limpia http_proxy vía adb)
bash mitm/setup.sh disable-device
```

En Windows: reemplazar `bash mitm/setup.sh` por `mitm\setup.bat`.

## API JSON del addon (puerto 8082)

| Endpoint | Uso |
|----------|-----|
| `GET /health` | `{ok, flows, events, tls_failures}` — chequeo rápido |
| `GET /flows?limit=50` | Últimos N flujos (resumen) |
| `GET /events` | Todos los eventos `rads-tracker` capturados |
| `GET /events?type=render` | Filtro por tipo (`render`, `viewed_impression`, `click`, `add_to_cart`, `conversion`) |
| `GET /events?placement=headline-data-zero` | Filtro por placement |
| `GET /events?adToken=ADS-...` | Filtro por adToken |
| `GET /events?source=global_search_data_zero` | Filtro por source |
| `GET /events?productId=<id>` | Filtro por producto |
| `GET /probe?host=services.rappi.com.ar` | `{intercepted: true|false}` — sirve para sanity check |
| `POST /reset` | Limpia buffer (llamar al inicio de cada test que arme aserciones) |

Estructura de un evento devuelto por `/events`:
```json
{
  "ts": 1718911823.41,
  "type": "render",
  "adToken": "ADS-01JECKDCA2T178F1QF1CSAHCZP",
  "placement": "headline-data-zero",
  "source": "global_search_data_zero",
  "campaignId": "TRC-01JCZWXVFPG9QWX7E1GQH18JDJ",
  "productId": null,
  "price": null,
  "index": 0,
  "itemIndex": 0,
  "host": "services.rappi.com.ar",
  "raw": { /* payload original completo */ }
}
```

## Patrón de uso en Keywords / Steps

Cualquier Page/Steps que asegure eventos debe:

1. **Resetear el buffer** al inicio del bloque (`POST http://127.0.0.1:8082/reset`).
2. Ejecutar la acción UI que dispara el evento.
3. **Polling** con `GET /events?type=<evento>` hasta encontrar match o timeout (recomendado: 10s con poll cada 500ms — la app dispara los eventos asíncronamente).
4. Asertar atributos obligatorios según el TC (ej: `adToken` no nulo, `placement` correcto, `productId` esperado, etc.).
5. NO cerrar la sesión mitm entre tests del mismo flow — sólo `/reset`.

Cliente HTTP sugerido en Groovy (sin dependencias nuevas): `java.net.HttpURLConnection` o `groovy.json.JsonSlurper` con `URL.text`.

## Pre-flight obligatorio antes de aserciones de eventos

Antes de generar/correr cualquier test que toque `/api/rads-tracker/event`, validar en este orden:

```bash
# (a) mitmproxy arriba
curl -s http://127.0.0.1:8082/health
# Esperado: {"ok":true,"flows":N,...}

# (b) device proxeado (sanity: que pase tráfico ANY al proxy)
bash mitm/setup.sh test     # corre un probe automatizado, 30s

# (c) si (b) reporta "0 rads-tracker events" tras navegar la app:
#     el cert no es confiable para Rappi → ver "Limitación importante" abajo
```

Si cualquiera falla, **NO seguir con la generación/ejecución del test**. Pedir al usuario que ejecute `bash mitm/setup.sh start && bash mitm/setup.sh device` o, si es Windows, los .bat equivalentes.

## Limitación importante (Android 7+) — sin esto no captura HTTPS de Rappi

Desde Android 7, las apps sólo confían en CAs de usuario si su `network_security_config` lo permite. Si el APK productivo de Rappi no lo permite, el proxy verá conexiones TLS pero **no podrá descifrar el body** → no habrá eventos.

Si `setup.sh test` reporta tráfico TLS pero 0 eventos `rads-tracker`, escalar al usuario con una de estas opciones (en orden):

1. Usar **APK de QA/debug** de Rappi (suele confiar en user CAs — si Charles ya funciona, este APK existe).
2. **Device rooteado** → mover el cert a `/system/etc/security/cacerts/`.
3. **Emulador Android Studio** con `adb root` para mover cert al system store.
4. **Frida** con script de SSL pinning bypass.

`mitm/README.md` tiene más detalle.

## Qué NO hacer (anti-patrones)

- ❌ Crear nuevos clientes HTTP/proxy adhoc en Keywords — usar siempre el addon existente.
- ❌ Parsear logs de Charles `.chlsj`/`.har` — esa opción se descartó.
- ❌ Asumir que el device ya está proxeado — siempre hacer pre-flight (`/health` + opcionalmente `/probe`).
- ❌ Hardcodear puertos distintos — proxy `8080`, addon API `8082`. Si chocan, cambiarlos UNA vez en `mitm/addon/rads_addon.py` y `mitm/setup.py`.
- ❌ Dejar el buffer sin resetear entre tests — produce falsos positivos por eventos de runs anteriores.
- ❌ **Aserciones débiles tipo "existe algún evento del tipo X"**. Esa forma no verifica que el evento corresponda al elemento manipulado por UI y siempre pasa con eventos rezagados. Usar siempre el **algoritmo de JOURNEY** (sección siguiente).

---

# ALGORITMO DE JOURNEY (obligatorio para TCs nuevos)

A partir de mayo/2026 los TCs nuevos que validen `rads-tracker` DEBEN seguir este algoritmo. Los keywords legacy de `RadsTrackerSteps` quedan solo como compat backward para los TCs que ya existían.

## Reglas duras

| # | Regla | Razón |
|---|-------|-------|
| 1 | **`adToken` es la identidad PRIMARIA** para correlacionar eventos del mismo elemento. | Es lo único confiable; placement/source pueden venir vacíos o como "Rappi". |
| 2 | **PRODUCT vs BANNER se decide por `price`**: PRODUCT si `price > 0`, BANNER en otro caso (null / 0 / '' / no numérico). | El payload de Rappi es uniforme; el price diferencia ambos universos. |
| 3 | **No usar `placement` ni `source` como llave primaria** — solo como verificación secundaria (informativo en logs). | `placement` no siempre viene confiable en `render`. |
| 4 | **`render` es OPCIONAL** según el placement y NUNCA debe ser el ancla principal. | Algunos placements no disparan `render`; el evento puede llegar sin identidad útil. |
| 5 | **Anclaje fuerte** = el evento que ya implica interacción/visibilidad: <br>• **Banner manipulado**: `click`. <br>• **Producto manipulado**: `click`, `add_to_cart` o `conversion`. <br>• **Producto visible en landing sin click**: `viewed_impression`. | Lo demás (render, viewed_impression de banner post-navegación) es ruido. |
| 6 | **NO usar nuevos `viewed_impression` de banner como ancla** después de cambiar de pantalla/contexto. | Los re-render post-navegación contaminan la correlación del banner original. |
| 7 | **Cada producto visible en landing debe tener `viewed_impression` con `adToken` único**. | Mide visibilidad efectiva de los productos patrocinados. |
| 8 | Si después se interactúa con un producto, **`click` / `add_to_cart` / `conversion` deben compartir el mismo `adToken` que su `viewed_impression`**. | Demuestra que la app rastrea el journey correctamente. |
| 9 | **Duplicados (type, adToken) dentro del scope analizado = FAIL**. | Indica doble disparo de evento (bug en la app). |
| 10 | `productId` debe preservarse de forma consistente para los eventos del mismo journey cuando aplique. | Sanity adicional; no es identidad primaria. |

## Implementación canónica

**Cliente de eventos** — [`Keywords/com/rappi/page/android/RadsTrackerEventsPage.groovy`](../../Keywords/com/rappi/page/android/RadsTrackerEventsPage.groovy)
Métodos públicos del nuevo algoritmo:

| Método | Uso |
|--------|-----|
| `fetchAllEvents()` | Snapshot normalizado del buffer entero. |
| `normalizeEvent(Map)` | Coerce `price` a Number, trim `adToken`, asigna `kind`. |
| `classifyKind(Map)` | `'PRODUCT'` si price > 0, `'BANNER'` en otro caso. |
| `findEventsByAdToken(token, type?)` | Todos los eventos del mismo elemento. |
| `groupByAdToken()` | `Map<adToken, List<Map>>` del buffer. |
| `findDuplicatesByTypeAndAdToken(events)` | Detecta duplicados en el scope dado. |
| `assertNoDuplicatesByTypeAndAdToken(events, label)` | FAIL si hay duplicados. |
| `findAnchorEvent(type, kind?, criteria?)` | Último evento que cumple (type, kind opcional). |
| `awaitAnchorEvent(type, kind, criteria?, timeoutSec)` | Polling hasta encontrar ancla; FAIL si no llega. |
| `assertBannerLifecycle(adToken, label)` | Exige `[viewed_impression, click]` sin duplicados. |
| `assertProductLifecycle(adToken, stages, label)` | Exige los stages provistos sin duplicados. |
| `assertLandingVisibleProducts(min, label)` | Cada `viewed_impression` de PRODUCT con adToken único. |
| `assertConversionContainsAdToken(adToken, timeout)` | Conversion debe contener ese token en items[]. |

**Keywords semánticas** — [`Keywords/com/rappi/steps/android/RadsTrackerJourneySteps.groovy`](../../Keywords/com/rappi/steps/android/RadsTrackerJourneySteps.groovy)

| Keyword | Devuelve | Cuándo |
|---------|----------|--------|
| `assertBannerClickJourney(label, num)` | `String` adToken del banner | Después de tap en banner. |
| `assertLandingVisibleProducts(min, label, num)` | `List<String>` adTokens | Tras entrar/scroll a una landing/listado patrocinado. |
| `assertProductClickJourney(label, num)` | `String` adToken del producto | Tras tap en producto patrocinado (abrir detalle, etc.). |
| `assertProductAddToCartJourney(label, expectedAdToken?, requireClick, num)` | `String` adToken | Tras "Agregar" o "+" en producto patrocinado. |
| `assertProductConversionJourney(expectedAdToken, label, num)` | `String` adToken | Tras "Hacer Pedido". |
| `assertFullProductJourney(adToken, stages, label, num)` | `Map` resultado | Cierre del TC: lifecycle completo. |
| `dumpEventsBuffer(label)` | — | Debug aid; no falla. |

## Patrón canónico en un Script

```groovy
// Captura adToken del banner como ancla, valida lifecycle banner.
String bannerToken = CustomKeywords.'com.rappi.steps.android.RadsTrackerJourneySteps.assertBannerClickJourney'(
    'Banner Sponsored Brand Search', '3') as String

// Tras entrar a landing, valida que hay ≥1 producto visible con viewed_impression único.
List<String> productosVisibles = CustomKeywords.'com.rappi.steps.android.RadsTrackerJourneySteps.assertLandingVisibleProducts'(
    1, 'Data Zero Landing', '4') as List<String>

// Tras click en producto, captura su adToken y valida lifecycle [viewed_impression, click].
String productoToken = CustomKeywords.'com.rappi.steps.android.RadsTrackerJourneySteps.assertProductClickJourney'(
    'Producto sponsored', '5') as String

// Tras "Hacer Pedido", la conversion debe contener el mismo adToken.
CustomKeywords.'com.rappi.steps.android.RadsTrackerJourneySteps.assertProductConversionJourney'(
    productoToken, 'Conversion del producto del journey', '8')
```

## Anti-patrones que un agente NUNCA debe generar

- ❌ Asserts del estilo `awaitEvent('click', [adTokenNotNull: true])` sin correlación posterior — eso valida "alguien hizo click" no "el banner que toqué fue trackeado".
- ❌ Usar `placement='headline-data-zero'` como criterio de match — `placement` puede venir `null` aún cuando el evento es válido.
- ❌ Tomar el `viewed_impression` de banner DESPUÉS de entrar a la landing como evidencia del banner original — la app vuelve a enviar viewed_impression por re-render.
- ❌ No capturar el `adToken` del primer evento del journey y luego asumir que los siguientes corresponden al mismo elemento.
- ❌ Asumir que `render` siempre existe — algunos placements lo omiten.
- ❌ Dejar pasar duplicados de `(type, adToken)` "porque la app a veces dispara dos veces" — eso es un bug que el test debe denunciar.
