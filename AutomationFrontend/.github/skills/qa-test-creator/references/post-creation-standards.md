# Estándares post-creación (obligatorios en todo test generado)

> Extraído sin cambios de lógica desde `BMO-TestCreator.agent.md`.

## 1. Smart Wait compliance

Todo método de Page Object generado debe:
- Importar `rappi.utils.SmartWaitPage`
- Usar `SmartWaitPage.waitVisible(element, SmartWaitPage.CONSTANTE)` en vez de
  `Mobile.delay(N)`
- `SmartWaitPage.tapPause()` solo en loops de contador/incremento
- `SmartWaitPage.floorPause()` solo cuando no hay target de `waitVisible` disponible

## 2. Self-healing locators (dirigido por `tap_validated` del contexto)

Antes de poblar las estrategias de un `.rs`, leer el campo `tap_validated` del componente
en el archivo de contexto de `qa-flow-planner`/`qa-explorer`:

| `tap_validated` | Estrategias a poblar | `findWithFallback` | Comentario |
|---|---|---|---|
| `✅ true` | ACCESSIBILITY + ANDROID_UI_AUTOMATOR + ATTRIBUTES | ✅ usar si es ruta crítica | Interactivo confirmado en dispositivo |
| `❌ false` | Solo ATTRIBUTES | ❌ no aplica | No interactivo (label, decorativo) |
| `COMPOSE` | Solo coordenadas base + ATTRIBUTES de referencia | ❌ no aplica | `tapAtPosition` escalado con `DeviceResolutionPage` |
| *(ausente, contexto legacy)* | Poblar las 3 por defecto | ✅ si es ruta crítica | Prioridad ACCESSIBILITY > ANDROID_UI_AUTOMATOR > ATTRIBUTES |

Todo `.rs` con `tap_validated: true` debe tener ≥ 2 estrategias pobladas. Si `resource-id`
existe en los datos de contexto, es **obligatorio** usarlo en `ANDROID_UI_AUTOMATOR` como
`new UiSelector().resourceId("...")` — usar solo XPath cuando hay `resource-id` disponible
es un error de calidad.

## 3. Visual Baseline Capture (obligatorio)

Después de crear un test case, siempre agregar snapshots en 1–3 pantallas críticas:
```groovy
// BASELINE: primer run la establece; runs siguientes comparan automáticamente
CustomKeywords.'rappi.utils.ScreenshotPage.captureAndCompare'('test_name_screen_state')
```
Identificar puntos de snapshot en: pantallas de confirmación final (éxito), cambios de
estado de carrito/orden, pantallas de pago. Si no hay un punto natural, agregar uno en la
pantalla de aserción final.

## 4. LocatorHelper para elementos críticos

Para cualquier elemento en la ruta crítica de compra (carrito, checkout, pago, order
tracking), preferir:
```groovy
TestObject el = CustomKeywords.'rappi.utils.LocatorHelper.findWithFallback'(
    'content-desc-value',                     // ACCESSIBILITY
    'new UiSelector().resourceId("...")',      // ANDROID_UI_AUTOMATOR
    '//*[@content-desc="content-desc-value"]' // ATTRIBUTES
)
```
sobre una llamada `findTestObject()` sin fallback.

## 5. VisualLocatorPage para elementos dinámicos (solo Android)

Para elementos marcados `VISUAL_ONLY: true` en el plan (banners promocionales, contenido
dinámico sin atributos estables):
```groovy
import rappi.utils.VisualLocatorPage

TestObject promoEl = VisualLocatorPage.findByVisual('promo_banner_label', SmartWaitPage.MEDIUM)
if (promoEl != null) {
    Mobile.tap(promoEl, SmartWaitPage.MEDIUM)
} else {
    KeywordUtil.logInfo('⚠️ Promo element not found visually — skipping (non-critical)')
}
```
Plugin: `test-ai-classifier` v4.0.2, backend CPU. Agregar labels nuevos en
`Include/resources/classifier-labels/<label>/sample_N.png`.
