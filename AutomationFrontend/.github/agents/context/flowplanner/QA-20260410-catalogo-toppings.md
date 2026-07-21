# Plan de Automatización: QA-20260410-catalogo-toppings

## Metadata

| Campo | Valor |
|-------|-------|
| **RunId** | QA-20260410-catalogo-toppings |
| **BasedOn** | QA-20260409-catalogo-toppings-checkout.md |
| **Plataforma** | Android |
| **TipoCase** | Smoke (happy path + validación canasta/checkout/OT con personalización toppings) |
| **Vertical** | Restaurantes |
| **Tienda Objetivo** | cypress_test |
| **PlanStatus** | Approved |
| **PlanDate** | 2026-04-10 |
| **RetryCount** | 0 |
| **ApprovedBy** | BMO-Explorer |
| **ApprovalDate** | 2026-04-10 |
| **ApprovalNotes** | Plan validado en dispositivo R5CY111XY3E. ModalEnvioGratis confirmado como OPCIONAL/CONDICIONAL: ejecutados 2 flows completos Canasta→Checkout→ModalEfectivo sin que el modal apareciera. Modal solo se activa cuando hay promo de envío gratis activa en el entorno. Estrategia: `waitVisibleOptional(container_envioGratis, SHORT)` + if visible → cerrar, else → continuar. Todos los demás pasos ✅. Ver sección 'Hallazgos Exploración BMO-Explorer' al final del plan. |
| **RejectionNotes** | — |
| **DispositivoExplorado** | R5CY111XY3E (SM-S928B, Android 16) |
| **ResolucionExplorada** | 1080×2340 px |

---

## Cambios vs Plan Anterior

| # | Cambio | Descripción |
|---|--------|-------------|
| 1 | Navegación SIN buscador | Home → tap Card Restaurante → scroll → tap cypress_test (sin search bar) |
| 2 | Modal "envío gratis" post-canasta | Aparece antes del checkout; debe cerrarse primero |
| 3 | Modal "monto de pago" (efectivo) | Seleccionar "No necesitaré cambio" → tap "Hacer pedido" |
| 4 | Vista de Propina | Rappi Tendero propina screen antes de crear pedido |
| 5 | OT Resumen expandido | Tap "Resumen del pedido" para validar restaurante y cobro |

---

## 1. Objetivo del Caso

Validar el flujo de compra completo en Restaurantes con personalización de toppings:

- Navegar a tienda `cypress_test` via Card de Restaurantes en Home (sin buscador)
- Seleccionar producto con toppings y personalizar
- Agregar a canasta y validarla
- Completar checkout (cerrar modal envío gratis → modal monto efectivo → propina)
- Hacer pedido y validar Order Tracking (OT con resumen expandido)

---

## 2. Punto de Entrada (setUp)

### TC Reutilizado

| Campo | Valor |
|-------|-------|
| **Nombre** | `openRappi` |
| **Ruta** | `Test Cases/android/openRappi.tc` |
| **Responsabilidad** | Lanza app Rappi QA (`com.grability.rappi`), espera Home, anti-crash |
| **Punto de llegada** | Home de Rappi cargado y funcionando |

**Motivo de reutilización:**
- Garantiza estado conocido de la app antes del flujo
- Incluye reintentos ante crashes (robustez)
- Evita reescribir lógica ya estabilizada

---

## 3. Precondiciones

| Precondición | Estado | Validación |
|---|---|---|
| App Rappi QA instalada (`com.grability.rappi`) | ✅ Confirmado en dispositivo | `adb shell pm list packages` |
| Dispositivo conectado y activo | ✅ R5CY111XY3E online | `adb devices` |
| Dev environment configurado en QA Launcher | ✅ Confirmado | OT creó pedido en cypress_test |
| Tienda cypress_test disponible en sección Restaurantes | ✅ Confirmado en dispositivo | Screenshot + tap exitoso |
| Producto con toppings disponible en cypress_test | ✅ Confirmado | Shawarmaa/McBacon navegado en sesión anterior |
| Método de pago: Efectivo configurado | ✅ Confirmado | Modal de monto apareció en checkout |
| Propina habilitada para cypress_test | ✅ Confirmado | Vista propina apareció |

---

## 4. Datos de Prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| **Tienda** | cypress_test | Restaurante de testing en DEV |
| **Producto** | Shawarmaa | Producto con selector de toppings |
| **Topping** | McBacon | Confirmado en OT Resumen: "McBacon" |
| **Precio producto + topping** | $46.000 (2 unidades) | Validado en OT expandido |
| **Propina sugerida** | 18% / $8.300 | Seleccionada por defecto (Me salvas el día) |
| **Costo envío** | $6.899 | Validado en OT resumen |
| **Servicio** | $4.900 | Validado en OT resumen |
| **Total a pagar** | $66.099 | Subtotal + propina + envío + servicio |
| **Moneda** | COP | Dev environment Colombia |
| **Método de pago** | Efectivo (cash) | Requiere modal de monto de pago |

---

## 5. Pasos Funcionales Validados en Dispositivo

### Flujo Completo con Notaciones de Wait y Puntos de Riesgo

```
[1. setUp: openRappi — TC existente]
    → SmartWaitPage.waitVisible(lbl_inicioTab, SmartWaitPage.LONG)
    → Punto de llegada: Home de Rappi cargado
    → tap_validated: por openRappi TC (reutilizado)

[2. Tap Card Restaurante en Home]
    → Pre-tap Wait: SmartWaitPage.waitVisible(card_restaurante_text, SmartWaitPage.MEDIUM)
    → Tap en Card "Restaurante" — COMPOSE: coordenadas base x=292, y=1760 (1080×2340)
    → Post-tap Wait: SmartWaitPage.waitVisible(inp_buscarRestaurantes, SmartWaitPage.MEDIUM)
    → tap_validated: ✅ Navegó a sección Restaurantes confirmado
    ⚠️ COMPOSE component — no resource-id disponible en UIAutomator

[3. Scroll + Tap cypress_test en lista de Restaurantes]
    → Scroll hasta ver sección "Mis Favoritos statsig" (visible sin scroll extenso)
    → cypress_test aparece como primera tienda en "Mis Favoritos"
    → Tap en card — COMPOSE: coordenadas base x=200, y=1150 (1080×2340)
    → Post-tap Wait: SmartWaitPage.waitVisible(lbl_storeName_cypressTest, SmartWaitPage.MEDIUM)
    → tap_validated: ✅ Navegó a store landing de cypress_test
    ⚠️ COMPOSE component — localizar por texto "cypress_test" visible

[4. Seleccionar producto con toppings (Shawarmaa)]
    → SmartWaitPage.waitVisible(lbl_storeName_cypressTest, SmartWaitPage.MEDIUM)
    → Tap en producto "Shawarmaa" en catálogo de tienda
    → Post-tap Wait: SmartWaitPage.waitVisible(lbl_nombreProductoDetalle, SmartWaitPage.MEDIUM)
    → tap_validated: ✅ (validado en sesión anterior)

[5. Personalizar topping McBacon]
    → SmartWaitPage.waitVisible(sel_toppingGroup, SmartWaitPage.SHORT)
    → Tap en topping "McBacon"
    → SmartWaitPage.floorPause() — animación de selección
    → tap_validated: ✅ (confirmado en orden final: "McBacon" visible en OT)

[6. Agregar a canasta]
    → SmartWaitPage.waitVisible(btn_agregarDesdeDetalle, SmartWaitPage.SHORT)
    → Tap btn_agregarDesdeDetalle
    → Post-tap Wait: SmartWaitPage.waitGone(spinner, SmartWaitPage.MEDIUM)
    → tap_validated: ✅ (2 productos en OT resumen)

[7. Ir a canasta]
    → SmartWaitPage.waitVisible(btn_irAPagar, SmartWaitPage.SHORT)
    → Tap btn_irAPagar (Canasta)
    → Post-tap Wait: SmartWaitPage.waitVisible(lbl_subtotalAmount, SmartWaitPage.MEDIUM)
    → tap_validated: ✅ OR existente — btn_irAPagar.rs

[8. Tap Continuar en Canasta → Modal Envío Gratis aparece]
    → SmartWaitPage.waitVisible(btn_continuarCanasta, SmartWaitPage.SHORT)
    → Tap btn_continuarCanasta
    → Post-tap Wait: SmartWaitPage.waitVisible(container_envioGratis, SmartWaitPage.MEDIUM)
    → tap_validated: ⚠️ WAIT_UNKNOWN — modal no capturado en este run
    ⚠️ MODAL NO CAPTURADO: requiere exploración específica por BMO-Explorer

[9. Cerrar Modal Envío Gratis]
    → SmartWaitPage.waitVisible(btn_cerrarEnvioGratis, SmartWaitPage.SHORT)
    → Tap btn_cerrarEnvioGratis (X o "Continuar sin envío gratis")
    → Post-tap Wait: SmartWaitPage.waitVisible(btn_continuar_checkout, SmartWaitPage.MEDIUM)
    → tap_validated: ⚠️ WAIT_UNKNOWN — modal no capturado en este run
    ⚠️ MODAL NO CAPTURADO: requiere exploración específica por BMO-Explorer

[10. Validar Checkout + Tap Continuar]
    → SmartWaitPage.waitVisible(btn_continuar, SmartWaitPage.MEDIUM)
    → Validar: lbl_efectivo visible, lbl_metodoPago visible
    → Tap btn_continuar (checkout)
    → Post-tap Wait: SmartWaitPage.waitVisible(container_cashModal, SmartWaitPage.MEDIUM)
    → tap_validated: ✅ OR existente — btn_continuar.rs, lbl_efectivo.rs

[11. Modal "Monto de Pago" — Seleccionar "No necesitaré cambio"]
    → SmartWaitPage.waitVisible(container_cashModal, SmartWaitPage.MEDIUM)
    → Tap radio_noNecesitoChange (RadioButton[1] dentro de container_cashModal)
      → Estrategia: XPath //*[@resource-id="com.grability.rappi:id/checkout_cash_modal_view_container"]//android.widget.RadioButton[1]
      → Alternativa COMPOSE: coordenadas x=96, y=1399 (1080×2340)
    → SmartWaitPage.floorPause()
    → Verificar: botón cambia de "Ingresar valor" a "Hacer pedido" (content-desc)
    → Tap btn_hacerPedidoCash (content-desc='Hacer pedido')
    → Post-tap Wait: SmartWaitPage.waitVisible(lbl_reconoceEsfuerzo, SmartWaitPage.MEDIUM)
    → tap_validated: ✅ radio + btn explorados en dispositivo; OR existente en ModalEfectivo/

[12. Vista de Propina — Tap Hacer Pedido]
    → SmartWaitPage.waitVisible(lbl_reconoceEsfuerzo, SmartWaitPage.MEDIUM)
    → Opción 18% "Me salvas el día" seleccionada por defecto (OK para happy path)
    → Tap btn_hacerPedidoPropina — COMPOSE: View en bounds [68,2002][1012,2160]
      → Estrategia primaria: OR Propina/btn_hacerPedidoPropina.rs (XPath text="Hacer pedido")
      → Alternativa coordenadas: x=540, y=2081 (1080×2340)
    → Post-tap Wait: SmartWaitPage.waitVisible(lbl_creatingOrder, SmartWaitPage.LONG)
    → tap_validated: ✅ Tap ejecutado → OT cargó con cypress_test pedido
    → Visual Checkpoint: ScreenshotPage.captureAndCompare('propina_screen')

[13. Pantalla "Estamos creando tu pedido"]
    → SmartWaitPage.waitVisible(lbl_orderStatus, SmartWaitPage.LONG)
      → lbl_orderStatus.rs: text="Estamos creando tu pedido" — OR existente
    → SmartWaitPage.waitGone(lbl_creatingOrder, SmartWaitPage.LONG) — esperar transición a OT
    → tap_validated: ✅ pantalla mostrada confirmada en OT

[14. OT — Pedido Creado, Validar Resumen]
    → SmartWaitPage.waitVisible(lbl_orderSummary, SmartWaitPage.LONG)
      → lbl_orderSummary.rs: rid='description', text='2 Productos · $66.099' — OR existente
    → ASSERTION: getText(lbl_orderSummary) contains "2 Productos"
    → Tap lbl_orderSummary (expandir "Resumen del pedido")
    → Post-tap Wait: SmartWaitPage.waitVisible(lbl_orderCreatedTime, SmartWaitPage.SHORT)
    → tap_validated: ✅ Expandido correctamente en dispositivo

[15. OT — Validar Detalle del Pedido (Resumen Expandido)]
    → SmartWaitPage.waitVisible(lbl_orderCreatedTime, SmartWaitPage.SHORT)
    → ASSERTIONS:
      → Verificar texto "cypress_test" en sección restaurante (ubicación)
      → Verificar producto "Shawarmaa" visible
      → Verificar topping "McBacon" visible
      → Verificar "Total a pagar" + monto "$66.099"
      → Verificar método de pago "cash"
    → Visual Checkpoint: ScreenshotPage.captureAndCompare('ot_resumen_expandido')
    → tap_validated: ✅ Todos los valores validados visualmente en dispositivo
```

---

## 6. Tabla de Componentes

> **Nota de resolución**: Coordenadas base expresadas en resolución 1080×2340 (SM-S928B explorado).
> Escalar con `DeviceResolutionPage.scaleX(x)/scaleY(y)` para otros dispositivos.

| # | Pantalla | Nombre Componente | resource-id real | content-desc | tap_validated | .rs existente | Notas |
|---|----------|-------------------|------------------|--------------|---------------|---------------|-------|
| 1 | Home | card_restaurante | — | — | ✅ true | ❌ crear | COMPOSE; text='Restaurante'; bounds texto [79,1836][506,1895]; tap base x=292,y=1760 |
| 2 | Home | lbl_inicioTab | — | 'Inicio' | — | ✅ `Home/lbl_inicioTab.rs` | Tab inicio bottom bar |
| 3 | Restaurantes | card_cypressTest | — | — | ✅ true | ❌ crear | COMPOSE; text='cypress_test'; bounds [68,1218][354,1277]; tap base x=200,y=1150 |
| 4 | Restaurantes | inp_buscarRestaurantes | — | — | — | ❌ crear | Search field; text placeholder |
| 5 | Store Landing | lbl_storeName_cypressTest | — | — | ✅ true | ❌ crear | text='cypress_test' en header de tienda |
| 6 | ProductoDetalle | lbl_nombreProductoDetalle | — | — | ✅ true | ✅ existente OR Geant | Verificar nombre producto |
| 7 | ProductoDetalle | sel_toppingGroup | — | — | ✅ true | ❌ crear | Selector grupo toppings (posible Compose) |
| 8 | ProductoDetalle | chk_mcbacon | — | — | ✅ true | ❌ crear | Topping específico; text='McBacon' |
| 9 | ProductoDetalle | btn_agregarDesdeDetalle | — | — | ✅ true | ✅ `ProductoDetalle/btn_agregarDesdeDetalle.rs` | Agregar al carrito |
| 10 | Canasta | btn_irAPagar | — | — | ✅ true | ✅ `Canasta/btn_irAPagar.rs` | Ir a checkout |
| 11 | Canasta | lbl_cartProductName | `description` | — | — | ✅ `Canasta/lbl_cartProductName.rs` | Nombre producto en canasta |
| 12 | Canasta | lbl_subtotalAmount | — | — | — | ✅ `Canasta/lbl_subtotalAmount.rs` | Subtotal canasta |
| 13 | **ModalEnvioGratis** | **container_modalEnvioGratis** | **⚠️ CONDICIONAL** | — | ⚠️ OPCIONAL | ❌ crear (solo si modal activo) | Modal OPCIONAL — solo aparece cuando promo de envío gratis está activa. En 2 runs consecutivos NO apareció (Canasta→Checkout directo). Estrategia: `waitVisibleOptional`. Locator sugerido basado en patron Rappi: `com.grability.rappi:id/checkout_cash_modal_view_container` o similar sheet modal. |
| 14 | **ModalEnvioGratis** | **btn_cerrarEnvioGratis** | **⚠️ CONDICIONAL** | — | ⚠️ OPCIONAL | ❌ crear (solo si modal activo) | Botón de cierre del modal envío gratis (X, "Continuar sin envío gratis" o "No gracias"). SOLO interactuar si container_modalEnvioGratis fue visible. Estrategia: `if (SmartWaitPage.waitVisibleOptional(container, SHORT)) { tap(btn_cerrar) }` |
| 15 | Checkout | btn_continuar | — | — | ✅ true | ✅ `Checkout/btn_continuar.rs` | Confirmar checkout |
| 16 | Checkout | lbl_efectivo | — | — | ✅ true | ✅ `Checkout/lbl_efectivo.rs` | Método de pago |
| 17 | ModalEfectivo | container_cashModal | `com.grability.rappi:id/checkout_cash_modal_view_container` | — | ✅ true | ✅ `ModalEfectivo/container_cashModal.rs` | Modal monto de pago efectivo |
| 18 | ModalEfectivo | lbl_cashModalTitle | — | — | — | ✅ `ModalEfectivo/lbl_cashModalTitle.rs` | "Por favor, especifica el monto..." |
| 19 | ModalEfectivo | radio_noNecesitoChange | — (XPath: container//RadioButton[1]) | — | ✅ true | ✅ `ModalEfectivo/radio_noNecesitoChange.rs` | Primera Radio en modal; bounds [29,1332][164,1467]; tap base x=96,y=1399 |
| 20 | ModalEfectivo | btn_hacerPedidoCash | — | `'Hacer pedido'` | ✅ true | ✅ `ModalEfectivo/btn_hacerPedidoCash.rs` | Aparece tras seleccionar radio; bounds [135,1991][945,2149] |
| 21 | Propina | lbl_reconoceEsfuerzo | — | — | — | ✅ `Propina/lbl_reconoceEsfuerzo.rs` | Título pantalla propina |
| 22 | Propina | row_meSalvasElDia (18%) | — | — | — | ❌ crear si necesario | Fila seleccionada por defecto; bounds [68,1400][1012,1535] |
| 23 | Propina | btn_hacerPedidoPropina | — | — | ✅ true | ✅ `Propina/btn_hacerPedidoPropina.rs` | View [68,2002][1012,2160]; tap base x=540,y=2081; ⚠️ XPath usa text="Hacer pedido" pero no aparece en dump — verificar |
| 24 | OT | lbl_orderStatus | — (text="Estamos creando tu pedido") | — | ✅ true | ✅ `OrderTracking/lbl_orderStatus.rs` | Estado inicial OT |
| 25 | OT | lbl_orderSummary | `description` | — | ✅ true | ✅ `OrderTracking/lbl_orderSummary.rs` | "2 Productos · $66.099"; clickable → expande detalle |
| 26 | OT | text_view_eta | `text_view_eta_small` | — | — | ❌ crear | Timer de entrega "52:07" |
| 27 | OT (expandido) | lbl_orderCreatedTime | `textView_order_created` | — | ✅ true | ❌ crear | "Pedido creado: 12:54 am"; confirma orden creada |
| 28 | OT (expandido) | lbl_totalAPagar | — (text='Total a pagar') | — | ✅ true | ❌ crear | Monto total $66.099 en resumen |
| 29 | OT (expandido) | lbl_productNameOT | — (text='Shawarmaa') | — | ✅ true | ❌ crear | Nombre producto en resumen expandido |
| 30 | OT (expandido) | lbl_toppingOT | — (text='McBacon') | — | ✅ true | ❌ crear | Topping en resumen expandido |
| 31 | Home (OT Preview) | home_order_card_widget | `home_order_card_widget` | — | — | ❌ crear | Card de pedido activo en Home; contiene store_name y status |
| 32 | Home (OT Preview) | home_order_store_name | `home_order_store_name` | — | — | ❌ crear | text='cypress_test' en card orden activa |

### Elementos Críticos NO Capturados (requieren BMO-Explorer)

| # | Pantalla | Elemento | Razón |
|---|----------|----------|-------|
| 13 | ModalEnvioGratis | container + btn_cerrar | Modal no visible durante exploración de este run — se produce entre canasta y checkout |

---

## 7. Riesgos y Mitigaciones

| Riesgo | Severidad | Probabilidad | Mitigación |
|--------|-----------|--------------|------------|
| **Modal envío gratis NO capturado** | 🔴 ALTO | Alta | BMO-Explorer debe reproducir el flujo completo y capturar el modal; bloquea el paso 9 |
| **btn_hacerPedidoPropina XPath usa text="Hacer pedido" pero no aparece en dump** | 🔴 ALTO | Media | Verificar en BMO-Explorer: puede ser un child TextView no mostrado, o necesitar content-desc/coordenadas |
| **Card Restaurante COMPOSE sin resource-id** | 🟡 MEDIO | Alta | Usar `tapAtPosition` con DeviceResolutionPage; texto "Restaurante" como indicador post-tap |
| **Card cypress_test COMPOSE sin resource-id** | 🟡 MEDIO | Alta | Usar `tapAtPosition`; texto "cypress_test" como indicador de navegación exitosa |
| **Propina porcentaje cambia dinámicamente** | 🟡 MEDIO | Media | El happy path NO selecciona manualmente propina (usa default 18%); no assertions sobre % exacto |
| **OT Resumen sin resource-ids en ítems individuales** | 🟡 MEDIO | Alta | Usar XPath contextual por text visible; riesgo en i18n |
| **Modal monto aparece SOLO con método Efectivo** | 🟡 MEDIO | Baja | Verificar en precondiciones que Efectivo esté configurado como pago |
| **Tienda cypress_test no aparece primera en lista** | 🟢 BAJO | Baja | Aparece en "Mis Favoritos statsig"; si no aparece primero, usar scroll.waitForText("cypress_test") |

---

## 8. Handoff Técnico para BMO-TestCreator

### Estructura de Archivos a Crear

```
Test Cases/android/catalogo-toppings/
└── TC_CatalogoToppingsHappyPath.tc
    └── Scripts/android/catalogo-toppings/Script_Happy.groovy

Keywords/com/rappi/
├── page/catalogo/
│   ├── RestaurantesLandingPage.groovy      ← Home → Card Restaurante → Restaurantes section
│   ├── CypressTestStorePage.groovy         ← scroll + tap cypress_test en lista
│   └── OTResumenPage.groovy                ← Expandir resumen OT + assertions
│
└── steps/catalogo/
    ├── RestaurantesNavigationSteps.groovy  ← @Keyword: navigateToRestaurantes(), selectStore(name)
    └── OTResumenSteps.groovy               ← @Keyword: expandOrderSummary(), validateResumen()

Object Repository/android/
├── Home/
│   └── card_restaurante.rs                ← COMPOSE; tapAtPosition base x=292,y=1760
│
├── Restaurantes/
│   ├── card_cypressTest.rs                 ← COMPOSE; tapAtPosition x=200,y=1150
│   └── inp_buscarRestaurantes.rs           ← Search field (a futuro)
│
├── ModalEnvioGratis/                       ← ⚠️ NUEVA carpeta; BMO-Explorer captura primero
│   ├── container_modalEnvioGratis.rs       ← ⚠️ PENDIENTE captura
│   └── btn_cerrarEnvioGratis.rs            ← ⚠️ PENDIENTE captura
│
└── OrderTracking/
    ├── lbl_orderCreatedTime.rs             ← rid='textView_order_created'
    ├── lbl_totalAPagar.rs                  ← text='Total a pagar' (en resumen expandido)
    ├── lbl_productNameOT.rs               ← text='Shawarmaa' (en resumen expandido)
    └── lbl_toppingOT.rs                    ← text='McBacon' (en resumen expandido)
```

### Custom Keywords a Reutilizar (del Proyecto)

| Keyword / TC | Ubicación | Uso |
|---|---|---|
| `openRappi` (TC) | `Test Cases/android/openRappi.tc` | setUp — llamada al inicio del Script |
| `btn_irAPagar` | `Canasta/btn_irAPagar.rs` | Navegar de canasta a checkout |
| `btn_continuar` | `Checkout/btn_continuar.rs` | Confirmar checkout |
| `lbl_efectivo` | `Checkout/lbl_efectivo.rs` | Assertion método de pago |
| `container_cashModal` | `ModalEfectivo/container_cashModal.rs` | Wait para modal monto |
| `radio_noNecesitoChange` | `ModalEfectivo/radio_noNecesitoChange.rs` | Tap opción sin cambio |
| `btn_hacerPedidoCash` | `ModalEfectivo/btn_hacerPedidoCash.rs` | Tap hacer pedido post-radio |
| `lbl_reconoceEsfuerzo` | `Propina/lbl_reconoceEsfuerzo.rs` | Wait pantalla propina |
| `btn_hacerPedidoPropina` | `Propina/btn_hacerPedidoPropina.rs` | ⚠️ Verificar XPath en BMO-Explorer |
| `lbl_orderStatus` | `OrderTracking/lbl_orderStatus.rs` | Wait "Estamos creando tu pedido" |
| `lbl_orderSummary` | `OrderTracking/lbl_orderSummary.rs` | Tap para expandir resumen OT |
| `SmartWaitPage` | `rappi/utils/SmartWaitPage` | Todos los waits del flujo |
| `DeviceResolutionPage` | `rappi/page/common/DeviceResolutionPage` | Escalar coordenadas COMPOSE |
| `ScreenshotPage` | `rappi/utils/ScreenshotPage` | Visual checkpoints en Propina + OT |

### Utilities a Usar

```groovy
// Tap en elemento COMPOSE (Card Restaurante)
int scaledX = DeviceResolutionPage.scaleX(292, 1080)
int scaledY = DeviceResolutionPage.scaleY(1760, 2340)
Mobile.tapAtPosition(scaledX, scaledY)

// Esperar elemento crítico
SmartWaitPage.waitVisible(findTestObject('OrderTracking/lbl_orderSummary'), SmartWaitPage.LONG)

// Visual checkpoint
ScreenshotPage.captureAndCompare('ot_resumen_expandido')
```

### Bloqueo: ModalEnvioGratis NO tiene OR

**Condición de desbloqueo para BMO-TestCreator:**
BMO-Explorer debe capturar los resource-ids de `container_modalEnvioGratis` y `btn_cerrarEnvioGratis` ANTES de que BMO-TestCreator pueda crear el Paso 9.

Alternativa provisional: si BMO-Explorer confirma que el modal puede cerrarse con `Mobile.pressBack()` o tap en coordenadas fijas, documentarlo como coordenadas escaladas.

---

## 9. Criterios de Aceptación

| # | Criterio | Condición Exit |
|---|----------|----------------|
| 1 | setUp openRappi exitoso | Home visible, sin crash |
| 2 | Navegación a Restaurantes | Sección restaurantes visible (sin buscador) |
| 3 | cypress_test seleccionable | Tap abre store landing |
| 4 | Producto + topping seleccionado | Shawarmaa con McBacon en canasta |
| 5 | Modal envío gratis cerrado | Checkout visible tras cerrar modal |
| 6 | Radio "no necesitaré cambio" seleccionado | Botón cambia a "Hacer pedido" |
| 7 | Propina skipped (default 18%) | Vista propina → tap Hacer pedido → OT |
| 8 | OT carga con "Pedido creado" | `lbl_orderStatus` visible |
| 9 | OT Resumen muestra cypress_test | Tienda y topping visibles en expandido |
| 10 | Total a pagar coincide | $66.099 validado en OT resumen |

---

## 10. Compatibilidad Multi-Dispositivo

### Dispositivos Objetivo

| Dispositivo | Resolución | Estado |
|-------------|-----------|--------|
| SM-S928B (explorado) | 1080×2340 px | ✅ Base de referencia |
| SM-S22+ / S23 | Aprox 1080×2340 | 🟡 Por validar |
| Pixel 6/7 | 1080×2400 | 🟡 Factor escala ~1.026 |
| Emulador Android 14-16 | Configurable 1080×1920 | 🟡 Factor escala diferente |

### Pasos con Coordenadas COMPOSE

| Paso | Pantalla | Componente | Bounds (1080×2340) | base_x | base_y | Escalar Via |
|------|----------|-----------|-------------------|--------|--------|-------------|
| 2 | Home | card_restaurante | [79,1836][506,1895] | 292 | 1760 | DeviceResolutionPage |
| 3 | Restaurantes | card_cypressTest | [68,1218][354,1277] | 200 | 1150 | DeviceResolutionPage |
| 11 | ModalEfectivo | radio_noNecesitoChange | [29,1332][164,1467] | 96 | 1399 | DeviceResolutionPage |
| 12 | Propina | btn_hacerPedidoPropina | [68,2002][1012,2160] | 540 | 2081 | DeviceResolutionPage |

**Plan de eliminación de coordenadas:**
- Pasos 2-3: Eliminar si card_restaurante y card_cypressTest exponen `content-desc` en versiones futuras de Rappi
- Paso 11: Ya tiene fallback XPath vía container resource-id → usar XPath primero; coordenadas solo como fallback
- Paso 12: Verificar si `btn_hacerPedidoPropina.rs` XPath funciona → BMO-Explorer debe confirmar

---

## 11. Smart Wait Annotations — Resumen

| Paso | Wait Tipo | Elemento objetivo | Constante | Razón |
|------|-----------|------------------|-----------|-------|
| 1 | waitVisible | lbl_inicioTab | LONG (30s) | App launch completa |
| 2 | waitVisible | inp_buscarRestaurantes | MEDIUM (15s) | Navegación de sección |
| 3 | waitVisible | lbl_storeName_cypressTest | MEDIUM (15s) | Store landing load |
| 7 | waitVisible | lbl_subtotalAmount | MEDIUM (15s) | Canasta render |
| 8 | waitVisible | container_envioGratis | MEDIUM (15s) | Modal backend delay |
| 10 | waitVisible | btn_continuar | MEDIUM (15s) | Checkout load |
| 10-11 | waitVisible | container_cashModal | MEDIUM (15s) | Modal pago efectivo |
| 11 | floorPause | — | 1s | Animación radio selection |
| 12 | waitVisible | lbl_reconoceEsfuerzo | MEDIUM (15s) | Propina screen load |
| 13 | waitVisible | lbl_orderStatus | LONG (30s) | Creación de pedido |
| 14 | waitVisible | lbl_orderSummary | LONG (30s) | OT confirmación pedido |

---

## 12. Instrucciones para BMO-Explorer (Validación)

### Checklist de Validación Empírica

- [ ] **PRIORIDAD ALTA**: Reproducir flujo desde canasta → continuar → capturar Modal Envío Gratis
  - Capturar: resource-id del container y del botón de cierre
  - Validar: ¿El modal cierra con X, con swipe, o con botón específico?
  
- [ ] Validar que `btn_selectRestVertical.rs` (text='Restaurantes') NO funciona con nueva UI
  - Confirmar si debe actualizarse o si el COMPOSE card con coordenadas es la estrategia definitiva

- [ ] Validar `btn_hacerPedidoPropina.rs` XPath `//android.widget.TextView[@text="Hacer pedido"]`
  - El dump no mostró este texto directamente en la View; verificar si es un child TextView
  - Si falla: actualizar a content-desc o coordenadas escaladas

- [ ] Validar `radio_noNecesitoChange.rs` XPath (requiere container resource-id)
  - Test: `adb shell uiautomator dump` + buscar `checkout_cash_modal_view_container`
  - Confirmar XPath: `//*[@resource-id="com.grability.rappi:id/checkout_cash_modal_view_container"]//android.widget.RadioButton[1]`

- [ ] Validar estrategia de scroll hasta cypress_test
  - ¿`UtilsPage.scrollToText("cypress_test")` funciona o se necesita `tapAtPosition`?
  - Confirmar que cypress_test siempre está en "Mis Favoritos statsig"

- [ ] MODO CAPTURA: Poblar sección "Componentes validados empíricamente" con base_x/base_y en 1080×2340

### Componentes validados empíricamente
*(BMO-Explorer poblará esta sección durante MODO CAPTURA)*

| .rs sugerido | resource-id | content-desc | bounds reales | base_x (1080) | base_y (2340) | tap_validated | estrategia_primaria | fallback |
|---|---|---|---|---|---|---|---|---|
| card_restaurante.rs | — | — | [79,1836][506,1895] (texto) | 292 | 1760 | true | tapAtPosition+DevRes | text="Restaurante" assert |
| card_cypressTest.rs | — | — | [68,1218][354,1277] (texto) | 200 | 1150 | true | tapAtPosition+DevRes | scrollToText("cypress_test") |
| container_modalEnvioGratis.rs | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | false | ⚠️ TBD | ⚠️ TBD |
| btn_cerrarEnvioGratis.rs | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | ⚠️ TBD | false | ⚠️ TBD | ⚠️ TBD |
| radio_noNecesitoChange.rs | (XPath container) | — | [29,1332][164,1467] | 96 | 1399 | true | XPath container+RadioButton[1] | tapAtPosition |
| btn_hacerPedidoCash.rs | — | 'Hacer pedido' | [135,1991][945,2149] | 540 | 2070 | true | ACCESSIBILITY content-desc | tapAtPosition |
| btn_hacerPedidoPropina.rs | — | ⚠️ verificar | [68,2002][1012,2160] | 540 | 2081 | true | ⚠️ XPath text a validar | tapAtPosition |
| lbl_orderCreatedTime.rs | textView_order_created | — | (dinámico) | — | — | true | ID resource-id | text contains "Pedido creado" |
| lbl_totalAPagar.rs | — | — | [68,1008][825,1059] | — | — | true | text="Total a pagar" | XPath contextual |

---

*Archivo generado por BMO-FlowPlanner | RunId: QA-20260410-catalogo-toppings | 2026-04-10*
