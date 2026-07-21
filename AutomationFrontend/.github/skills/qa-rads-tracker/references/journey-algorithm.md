# Algoritmo de journey — correlación por adToken

> Extraído sin cambios de lógica desde `.github/agents/RADS-TRACKER.md`.
> Obligatorio para TCs nuevos que validen `rads-tracker` desde mayo/2026. Los keywords
> legacy de `RadsTrackerSteps` quedan solo como compat backward de TCs ya existentes.

## Reglas duras

| # | Regla | Razón |
|---|-------|-------|
| 1 | `adToken` es la identidad PRIMARIA para correlacionar eventos del mismo elemento | Único dato confiable; placement/source pueden venir vacíos o como "Rappi" |
| 2 | PRODUCT vs BANNER se decide por `price`: PRODUCT si `price > 0`, BANNER en otro caso (null/0/''/no numérico) | El payload de Rappi es uniforme; `price` diferencia ambos universos |
| 3 | No usar `placement` ni `source` como llave primaria — solo verificación secundaria (informativo en logs) | `placement` no siempre viene confiable en `render` |
| 4 | `render` es OPCIONAL según el placement y nunca debe ser el ancla principal | Algunos placements no disparan `render` |
| 5 | Anclaje fuerte: banner manipulado → `click`; producto manipulado → `click`/`add_to_cart`/`conversion`; producto visible sin click → `viewed_impression` | Lo demás (render, viewed_impression post-navegación) es ruido |
| 6 | No usar nuevos `viewed_impression` de banner como ancla después de cambiar de pantalla/contexto | Los re-render post-navegación contaminan la correlación del banner original |
| 7 | Cada producto visible en landing debe tener `viewed_impression` con `adToken` único | Mide visibilidad efectiva de productos patrocinados |
| 8 | Si después se interactúa con un producto, `click`/`add_to_cart`/`conversion` deben compartir el mismo `adToken` que su `viewed_impression` | Demuestra que la app rastrea el journey correctamente |
| 9 | Duplicados `(type, adToken)` dentro del scope analizado = FAIL | Indica doble disparo de evento (bug en la app) |
| 10 | `productId` debe preservarse de forma consistente para eventos del mismo journey cuando aplique | Sanity adicional; no es identidad primaria |

## Implementación canónica

**Cliente de eventos** — `Keywords/com/rappi/page/android/RadsTrackerEventsPage.groovy`

| Método | Uso |
|--------|-----|
| `fetchAllEvents()` | Snapshot normalizado del buffer entero |
| `normalizeEvent(Map)` | Coerce `price` a Number, trim `adToken`, asigna `kind` |
| `classifyKind(Map)` | `'PRODUCT'` si price > 0, `'BANNER'` en otro caso |
| `findEventsByAdToken(token, type?)` | Todos los eventos del mismo elemento |
| `groupByAdToken()` | `Map<adToken, List<Map>>` del buffer |
| `findDuplicatesByTypeAndAdToken(events)` | Detecta duplicados en el scope dado |
| `assertNoDuplicatesByTypeAndAdToken(events, label)` | FAIL si hay duplicados |
| `findAnchorEvent(type, kind?, criteria?)` | Último evento que cumple (type, kind opcional) |
| `awaitAnchorEvent(type, kind, criteria?, timeoutSec)` | Polling hasta encontrar ancla; FAIL si no llega |
| `assertBannerLifecycle(adToken, label)` | Exige `[viewed_impression, click]` sin duplicados |
| `assertProductLifecycle(adToken, stages, label)` | Exige los stages provistos sin duplicados |
| `assertLandingVisibleProducts(min, label)` | Cada `viewed_impression` de PRODUCT con adToken único |
| `assertConversionContainsAdToken(adToken, timeout)` | Conversion debe contener ese token en items[] |

**Keywords semánticas** — `Keywords/com/rappi/steps/android/RadsTrackerJourneySteps.groovy`

| Keyword | Devuelve | Cuándo |
|---------|----------|--------|
| `assertBannerClickJourney(label, num)` | `String` adToken del banner | Después de tap en banner |
| `assertLandingVisibleProducts(min, label, num)` | `List<String>` adTokens | Tras entrar/scroll a landing/listado patrocinado |
| `assertProductClickJourney(label, num)` | `String` adToken del producto | Tras tap en producto patrocinado |
| `assertProductAddToCartJourney(label, expectedAdToken?, requireClick, num)` | `String` adToken | Tras "Agregar"/"+" en producto patrocinado |
| `assertProductConversionJourney(expectedAdToken, label, num)` | `String` adToken | Tras "Hacer Pedido" |
| `assertFullProductJourney(adToken, stages, label, num)` | `Map` resultado | Cierre del TC: lifecycle completo |
| `dumpEventsBuffer(label)` | — | Debug aid; no falla |

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

## Diagnóstico de journeys fallidos (para qa-debugger)

1. `Anchor type=X kind=Y no llega` → el evento esperado no se disparó; verificar la acción
   UI o `dumpEventsBuffer()` para ver qué sí llegó.
2. `Duplicados (type, adToken)` → la app dispara dos veces el mismo evento; **bug real,
   NO suprimir el assert**. Reportar al usuario el `adToken` duplicado.
3. `kind clasificado como BANNER pero esperado PRODUCT` (o viceversa) → `price` no llegó
   con el formato esperado; revisar el payload en `/events?adToken=...`.
4. `Conversion no contiene adToken=…` → el journey se rompió en alguna etapa; verificar
   que la cadena `viewed_impression → click → add_to_cart` use el mismo token.

No arreglar estos fallos relajando el assert — son señales válidas del algoritmo.

## Anti-patrones que un skill NUNCA debe generar

- ❌ `awaitEvent('click', [adTokenNotNull: true])` sin correlación posterior.
- ❌ Usar `placement='headline-data-zero'` como criterio de match.
- ❌ Tomar el `viewed_impression` de banner después de entrar a la landing como evidencia
  del banner original.
- ❌ No capturar el `adToken` del primer evento del journey y asumir que los siguientes
  corresponden al mismo elemento.
- ❌ Asumir que `render` siempre existe.
- ❌ Dejar pasar duplicados de `(type, adToken)` "porque la app a veces dispara dos veces".
