# Flow Context — QA-20260409-turbo-compra — Compra Turbo Dev

---

## Metadatos del plan

| Campo                  | Valor                                                        |
|------------------------|--------------------------------------------------------------|
| RunId                  | QA-20260409-turbo-compra                                     |
| Flujo                  | Compra de productos en tiendas TurboDev (Smoke Test)         |
| Plataforma             | android                                                      |
| Tipo                   | Smoke Test                                                   |
| PlanStatus             | Approved                                                     |
| RetryCount             | 0                                                            |
| ApprovedBy             | BMO-Explorer                                                 |
| ApprovalDate           | 2026-04-09                                                   |
| ApprovalNotes          | Todos los 8 pasos validados en dispositivo SM-S928B (R5CY111XY3E). 5 ajustes menores documentados (no bloqueantes): (1) Coord Y tarjeta Turbo varía por card "Pedido entregado" visible — y=1717 actual vs y=1567 plan; (2) Counter "+" del producto es Compose NAF post-primer-add — usar coords (413,860); (3) Total checkout $16.080 vs $14.680 en plan (precio DEV); (4) Propina default 18% vs 14% en plan; (5) Total pedido final $17.430. Todos los resource-ids clave confirmados en UIAutomator dump. |
| RejectionNotes         |                                                              |
| Fecha                  | 2026-04-09                                                   |
| DispositivoExplorado   | SM-S928B (R5CY111XY3E) — Android 16                         |
| ResolucionExplorada    | 1080×2340 px (es la resolución base del proyecto)            |
| AgenteAutor            | BMO-FlowPlanner                                              |

---

## Objetivo del caso

Validar el flujo completo de compra en una tienda **TurboDev** desde el Home de Rappi hasta la confirmación del pedido. El flujo incluye:
- Navegar al Home de la tienda Turbo
- Agregar productos hasta superar el mínimo de $7.000
- Completar el checkout con método de pago Efectivo
- Gestionar el popup "Especifica el monto de tu pago" seleccionando "No necesitaré cambio"
- Llegar a la pantalla de propina y confirmar el pedido
- Verificar que el pedido queda en estado "Seleccionando productos"

---

## Punto de entrada (setUp)

| Campo            | Valor                                                                 |
|------------------|-----------------------------------------------------------------------|
| TC reutilizado   | `openRappi` — `Scripts/android/openRappi/Script1774000000001.groovy` |
| Motivo           | El flujo parte desde el Home de Rappi ya cargado. `openRappi` incluye apertura de app, manejo del QA screen DEV y verificación de Home cargado. Evita reescribir lógica de apertura ya estabilizada. |
| Llamada sugerida | `CustomKeywords.'com.rappi.steps.common.HomeSteps.openRappi'()` o `callTestCase(findTestCase('Test Cases/android/openRappi'), ...)` |

> ⚠️ Nota sobre pantalla QA DEV: La app abre en modo QA con opciones de servidor. El `openRappi` existente ya maneja este flujo. Si se lanza manualmente, el flow pasa por la pantalla con `resource-id="com.grability.rappi:id/button_start_app"` (INICIAR RAPPI) antes de llegar al Home.

---

## Precondiciones

| # | Precondición                                                                 |
|---|------------------------------------------------------------------------------|
| 1 | Dispositivo Android conectado con `adb devices` en estado `device`           |
| 2 | App `com.grability.rappi` instalada en ambiente DEV (Monolito: http://v2.dev.rappi.com/) |
| 3 | Usuario autenticado con cuenta válida en DEV (Jhon - CO_101459658)           |
| 4 | Dirección de entrega configurada: Cl. 93 #19-58, Bogotá, Colombia            |
| 5 | Método de pago Efectivo configurado en la cuenta del usuario                 |
| 6 | Tienda Turbo disponible y operativa en DEV                                   |
| 7 | Conexión a internet activa en el dispositivo                                 |
| 8 | `GlobalVariable.G_Platform = "android"` en Profile default                  |

---

## Datos de prueba

| Variable           | Valor                        | Observación                                          |
|--------------------|------------------------------|------------------------------------------------------|
| Tienda objetivo    | Super Tienda Turbo (Nitro.)  | Identificada en UI como "Turbo Express"              |
| Mínimo de compra   | $7.000                       | Validado en-app: "Mínimo de compra $7,000"           |
| Producto usado     | Heineken Cerveza 0.0 Alcohol | $220/unidad en DEV — 1 x 250 mL                     |
| Unidades requeridas| ≥ 32 (se usan 34 en prueba)  | 34 × $220 = $7.480 > $7.000 ✅                       |
| Método de pago     | Efectivo                     | Ya preseleccionado en cuenta del usuario de prueba   |
| Opción de cambio   | No necesitaré cambio         | Activa CTA "Hacer pedido" en lugar de "Ingresar valor"|
| Propina sugerida   | "Me salvas el día" (14%)     | Seleccionada por defecto ($1.050 sobre base $7.480)  |

---

## Pasos funcionales validados en dispositivo

### Paso 1 — Abrir app de Rappi en ambiente DEV → Ver Home
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | App instalada. Puede estar cerrada o en background.                   |
| Acción         | `setUp`: llamar TC `openRappi` (maneja QA screen + inicio en DEV)     |
| Bifurcación    | Si app abre en QA screen: tap `btn_startApp` (resource-id estable)    |
| Bifurcación    | Si aparece banner "Estás lejos de la dirección": cerrar con X (Compose, coordenada ~[906,463]) |
| Validación     | Home de Rappi cargado — tarjetas "Restaurante" y "Turbo" visibles     |
| Estado post    | Home screen con `home_card_button` visibles                           |
| Riesgo         | Banner de ubicación bloquea UI → manejar con try/catch                |

---

### Paso 2 — Tap en tarjeta Turbo → Ver Home de la tienda Turbo
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Home de Rappi cargado                                                 |
| Acción         | Tap en tarjeta Turbo — `resource-id="home_card_button"` (Compose, tap por coordenadas escaladas) |
| Coordenadas    | Centro de la tarjeta Turbo: base 1080×2340 → x=787, y=1567           |
| Validación     | Home Turbo visible: título "Super Tienda Turbo", texto "Mínimo de compra $7,000", barra de búsqueda, categorías |
| Estado post    | Pantalla Turbo Store Home                                             |
| Riesgo         | Tarjeta Turbo puede estar fuera de pantalla → usar scroll si no visible |

---

### Paso 3 — Scroll y agregar productos hasta > $7.000
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Turbo Store Home cargado                                              |
| Acción 3a      | Scroll down para ver sección "Bebidas" con productos                  |
| Acción 3b      | Tap en botón "+" del producto disponible (Heineken u otro)            |
| Repetición     | Loop: tap "+" hasta que banner `lbl_minimoCompletado` sea visible     |
| Botón "+"      | `content-desc="add"` (Compose View, clickable parent Compose)         |
| Coordenadas +  | Base 1080×2340 → aprox. centro área "add" según posición scroll       |
| Validación 3a  | Cada tap incrementa contador en barra inferior                        |
| Validación 3b  | Banner verde: `resource-id="com.grability.rappi:id/square_notification_text"` text="¡Has completado el mínimo de compra!" |
| Validación 3c  | Barra inferior muestra total > $7.000 y botón "Ir a canasta" activo   |
| Estado post    | Barra inferior: "1 producto · $7.480 — Ir a canasta"                 |
| Criterio ✅    | El monto acumulado en la barra inferior debe superar $7.000           |
| Riesgo         | En DEV, precios muy bajos ($220/unidad) → requiere ≥32 taps en loop  |
| Riesgo         | El botón "+" es Compose sin resource-id → usar coordenadas escaladas  |

---

### Paso 4a — Tap "Ir a canasta" → Ver canasta con lista de productos
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Mínimo de compra completado, barra inferior visible                   |
| Acción         | Tap `content-desc="Ir a canasta"` bounds=[666,2035][1024,2170]       |
| Validación     | Vista canasta: producto listado con nombre, cantidad, precio. Subtotal visible. Banner mínimo. |
| Elementos clave| `resource-id="basketui_text_view_product_name"`, `basketui_text_view_product_price` |
| Estado post    | Pantalla Canasta / Nitro Cart                                         |

---

### Paso 4b — Click "Ir a pagar" → Vista Checkout "Terminar y pagar"
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Vista canasta abierta                                                 |
| Acción         | Tap `content-desc="Ir a pagar"` bounds=[648,2013][1024,2148]         |
| Bifurcación    | Modal PRO "Envíos GRATIS y más" puede aparecer → cerrar con `resource-id="com.grability.rappi:id/growth_prime_imageView_close"` bounds=[925,551][1015,641] |
| Validación     | Pantalla "Terminar y pagar" con mapa, dirección, detalles, tiempo "16-18 min con Turbo", sección "Método de pago" |
| Estado post    | Checkout screen                                                       |
| Riesgo CRÍTICO | Modal PRO aparece entre canasta y checkout → manejar siempre con try/catch antes de validar checkout |

---

### Paso 5 — Verificar / Seleccionar método de pago Efectivo
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Pantalla Checkout visible (sin modal PRO)                             |
| Acción         | Verificar que `text="Efectivo"` esté visible en sección "Método de pago" |
| Si no está     | Tap en `text="Cambiar"` para cambiar a Efectivo                       |
| Validación     | `text="Efectivo"` clickable=true visible en bounds=[204,1748][362,1883] |
| Estado post    | Método Efectivo seleccionado. Total a pagar visible ($14.680 incluye envío $4.700) |

---

### Paso 6 — Tap "Continuar" → Ver popup "Especifica el monto"
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Checkout con Efectivo seleccionado                                    |
| Acción         | Tap `content-desc="Continuar"` bounds=[540,2013][1024,2148]          |
| Validación     | Bottom sheet emergente con: título "Por favor, especifica el monto de tu pago", 3 opciones radio, botón CTA |
| Container      | `resource-id="com.grability.rappi:id/checkout_cash_modal_view_container"` (ComposeView) |
| Estado post    | Popup modal visible con "Necesitaré cambio" preseleccionado           |
| Riesgo         | El bottom sheet es Compose — radio buttons sí expuestos como `android.widget.RadioButton` |

---

### Paso 7 — Seleccionar "No necesitaré cambio" → Tap "Hacer pedido"
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Popup efectivo visible                                                |
| Acción 7a      | Tap RadioButton "No necesitaré cambio" en bounds=[29,1332][164,1467] (center 96,1399) |
| Validación 7a  | RadioButton `checked=true`. Botón CTA cambia a `content-desc="Hacer pedido"` |
| Acción 7b      | Tap `content-desc="Hacer pedido"` bounds=[135,1991][945,2149] (center 540,2070) |
| Validación 7b  | Navega a pantalla de propina del Rappitendero                         |
| Elementos clave| RadioButton sin resource-id — locator: `class="android.widget.RadioButton"` + orden/posición |
| Estado post    | Pantalla "¡Reconoce su esfuerzo!" con opciones de propina             |
| Criterio ✅    | Al seleccionar "No necesitaré cambio", el CTA debe cambiar de "Ingresar valor" a "Hacer pedido" |

---

### Paso 8 — Tap "Hacer pedido" en pantalla propina → Pedido creado
| Atributo       | Valor                                                                 |
|----------------|-----------------------------------------------------------------------|
| Precondición   | Pantalla propina del Rappitendero visible                             |
| Acción         | Tap botón "Hacer pedido" (Compose View, bounds=[68,2002][1012,2160]) |
| Validación     | Pantalla de tracking: `resource-id="com.grability.rappi:id/container_order_tracking_screen"` |
| Validación     | Estado: `text="Seleccionando productos"` visible                      |
| Validación     | `resource-id="description"` muestra "X Productos · $Y"               |
| Estado post    | Order tracking screen con estado "Seleccionando productos"            |
| Criterio ✅    | Pedido confirmado y en tracking                                       |
| Riesgo         | Botón "Hacer pedido" en propina es Compose sin resource-id → coordenadas |
| Riesgo         | Creación del pedido puede tardar → usar `waitForElementPresent` con timeout 15s |

---

## Modelo del flujo

```
[setUp] → openRappi (TC existente)
  → Home de Rappi cargado
  → [Flujo Turbo comienza aquí]
  → handle: banner "Estás lejos dirección" (dismiss X)
  → Tap tarjeta Turbo (home_card_button, coord escalada)
  → Home Turbo → verificar "Mínimo de compra $7,000"
  → Scroll hasta productos visible (Bebidas)
  → Loop: tap "+" producto hasta banner "¡Has completado el mínimo de compra!"
      → Validar: total barra inferior > $7.000
  → Tap "Ir a canasta" (content-desc="Ir a canasta")
  → Vista canasta → validar producto y subtotal
  → Tap "Ir a pagar" (content-desc="Ir a pagar")
      → Bifurcación A: Modal PRO aparece → cerrar con growth_prime_imageView_close
      → Bifurcación B: Modal PRO no aparece → continuar directo
  → Checkout "Terminar y pagar"
  → Verificar Efectivo seleccionado (text="Efectivo" visible)
  → Tap "Continuar" (content-desc="Continuar")
  → Popup "Por favor especifica el monto de tu pago" emergente
      → checkout_cash_modal_view_container
  → Tap RadioButton "No necesitaré cambio"
      → CTA cambia: "Ingresar valor" → "Hacer pedido"
  → Tap "Hacer pedido" (content-desc="Hacer pedido")
  → Vista propina "¡Reconoce su esfuerzo!"
  → Tap "Hacer pedido" (Compose coord [540,2081])
  → Esperar → container_order_tracking_screen
  → Validar: "Seleccionando productos" visible ✅
```

---

## Componentes UI capturados

> **Nota de coordenadas:** Dispositivo explorado = SM-S928B 1080×2340 (resolución base del proyecto). Las coordenadas `bounds` expresadas a continuación corresponden directamente a la base `DeviceResolutionPage` sin escalar.

| Paso | Pantalla          | class / type                          | text / resource-id                                              | content-desc       | bounds (1080×2340)      | .rs sugerido                         | Locator preferido       | Locator respaldo                  |
|------|-------------------|---------------------------------------|-----------------------------------------------------------------|--------------------|-------------------------|--------------------------------------|-------------------------|-----------------------------------|
| 1    | QA Screen         | android.widget.Button                 | `resource-id="com.grability.rappi:id/button_start_app"`         | -                  | [84,1184][996,1319]     | `btn_iniciarRappi`                   | resource-id             | text="INICIAR RAPPI"              |
| 1    | Home              | android.view.View (Compose)           | -                                                               | -                  | [880,415]~[950,511]     | `btn_closeBannerWarning`             | coordenadas escaladas   | N/A (Compose sin acc.)            |
| 2    | Home              | android.view.View (Compose)           | `resource-id="home_card_button"` (parent), child text="Turbo"   | -                  | [562,1376][1012,1759]   | `card_turbo`                         | resource-id (parent)    | coordenadas escaladas (centro)    |
| 3    | Turbo Home        | android.widget.TextView               | text="Mínimo de compra $7,000"                                  | -                  | visible en scroll       | `lbl_minimoCompra`                   | text                    | -                                 |
| 3    | Turbo Products    | android.view.View (Compose)           | -                                                               | `add`              | ~[367,943][502,1078]    | `btn_addProducto`                    | content-desc="add"      | coordenadas escaladas             |
| 3    | Turbo Products    | android.widget.TextView               | `resource-id="com.grability.rappi:id/square_notification_text"` | -                  | [144,1909][973,1955]    | `lbl_minimoCompletado`               | resource-id             | text="¡Has completado..."         |
| 3    | Turbo Products    | android.view.View (Compose)           | -                                                               | `Ir a canasta`     | [666,2035][1024,2170]   | `btn_irACanasta`                     | content-desc            | coordenadas escaladas             |
| 4a   | Canasta           | android.widget.TextView               | `resource-id="basketui_text_view_product_name"`                 | -                  | [237,357][697,453]      | `lbl_cartProductName`                | resource-id             | -                                 |
| 4a   | Canasta           | android.widget.TextView               | `resource-id="basketui_text_view_product_price"`                | -                  | [237,459][370,510]      | `lbl_cartProductPrice`               | resource-id             | -                                 |
| 4b   | Canasta           | android.view.View (Compose)           | -                                                               | `Ir a pagar`       | [648,2013][1024,2148]   | `btn_irAPagar`                       | content-desc            | coordenadas escaladas             |
| 4b   | Modal PRO         | android.widget.ImageView              | `resource-id="com.grability.rappi:id/growth_prime_imageView_close"` | -              | [925,551][1015,641]     | `btn_closeProModal`                  | resource-id             | coordenadas escaladas             |
| 5    | Checkout          | android.widget.TextView               | text="Método de pago"                                           | -                  | [68,1624][759,1683]     | `lbl_metodoPago`                     | text                    | -                                 |
| 5    | Checkout          | android.widget.TextView               | text="Efectivo" (clickable=true)                                | -                  | [204,1748][362,1883]    | `lbl_efectivo`                       | text                    | -                                 |
| 6    | Checkout          | android.view.View (Compose)           | -                                                               | `Continuar`        | [540,2013][1024,2148]   | `btn_continuar`                      | content-desc            | coordenadas escaladas             |
| 6    | Modal Efectivo    | androidx.compose.ui.platform.ComposeView | `resource-id="com.grability.rappi:id/checkout_cash_modal_view_container"` | - | [0,806][1080,2205]   | `container_cashModal`                | resource-id             | -                                 |
| 6    | Modal Efectivo    | android.widget.TextView               | text="Por favor, especifica el monto de tu pago"                | -                  | [68,874][855,1059]      | `lbl_cashModalTitle`                 | text                    | -                                 |
| 7    | Modal Efectivo    | android.widget.RadioButton            | checked=false → true al tap                                     | -                  | [29,1332][164,1467]     | `radio_noNecesitoChange`             | class + index (0)       | coordenadas (96,1399)             |
| 7    | Modal Efectivo    | android.widget.RadioButton            | checked=true (default)                                          | -                  | [29,1558][164,1693]     | `radio_necesitoChange`               | class + index (1)       | coordenadas (96,1625)             |
| 7    | Modal Efectivo    | android.view.View (Compose)           | -                                                               | `Hacer pedido`     | [135,1991][945,2149]    | `btn_hacerPedidoCash`                | content-desc            | coordenadas (540,2070)            |
| 8    | Propina           | android.widget.TextView               | text="¡Reconoce su esfuerzo!"                                   | -                  | [68,676][722,750]       | `lbl_reconoceEsfuerzo`               | text                    | -                                 |
| 8    | Propina           | android.view.View (Compose, NAF)      | -                                                               | -                  | [68,2002][1012,2160]    | `btn_hacerPedidoPropina`             | coordenadas (540,2081)  | N/A (Compose sin acc.)            |
| 8    | OrderTracking     | android.view.ViewGroup                | `resource-id="com.grability.rappi:id/container_order_tracking_screen"` | -       | [0,0][1080,2340]        | `container_orderTracking`            | resource-id             | -                                 |
| 8    | OrderTracking     | android.widget.TextView               | text="Seleccionando productos"                                  | -                  | [68,288][927,375]       | `lbl_orderStatus`                    | text                    | -                                 |
| 8    | OrderTracking     | android.widget.TextView               | `resource-id="description"` — "X Productos · $Y"               | -                  | [204,1333][644,1384]    | `lbl_orderSummary`                   | resource-id             | text parcial                      |

---

## Estructura de archivos a crear

### Object Repository
```
Object Repository/android/
├── QAScreen/
│   └── btn_iniciarRappi.rs               ← resource-id: button_start_app
├── TurboStore/
│   ├── lbl_minimoCompra.rs               ← text: "Mínimo de compra $7,000"
│   ├── lbl_minimoCompletado.rs           ← resource-id: square_notification_text
│   ├── btn_irACanasta.rs                 ← content-desc: "Ir a canasta"
│   └── btn_addProducto.rs                ← content-desc: "add" (Compose)
├── Canasta/
│   ├── lbl_cartProductName.rs            ← resource-id: basketui_text_view_product_name
│   ├── lbl_cartProductPrice.rs           ← resource-id: basketui_text_view_product_price
│   └── btn_irAPagar.rs                   ← content-desc: "Ir a pagar"
├── ModalPro/
│   └── btn_closeProModal.rs              ← resource-id: growth_prime_imageView_close
├── Checkout/
│   ├── lbl_metodoPago.rs                 ← text: "Método de pago"
│   ├── lbl_efectivo.rs                   ← text: "Efectivo"
│   └── btn_continuar.rs                  ← content-desc: "Continuar"
├── ModalEfectivo/
│   ├── container_cashModal.rs            ← resource-id: checkout_cash_modal_view_container
│   ├── lbl_cashModalTitle.rs             ← text: "Por favor, especifica el monto de tu pago"
│   ├── radio_noNecesitoChange.rs         ← class: RadioButton, index 0
│   ├── radio_necesitoChange.rs           ← class: RadioButton, index 1
│   └── btn_hacerPedidoCash.rs            ← content-desc: "Hacer pedido"
├── Propina/
│   ├── lbl_reconoceEsfuerzo.rs           ← text: "¡Reconoce su esfuerzo!"
│   └── btn_hacerPedidoPropina.rs         ← Compose NAF — coordenadas (540,2081)
└── OrderTracking/
    ├── container_orderTracking.rs        ← resource-id: container_order_tracking_screen
    ├── lbl_orderStatus.rs                ← text: "Seleccionando productos"
    └── lbl_orderSummary.rs              ← resource-id: description
```

### Keywords — Capa 1 (Page)
```
Keywords/com/rappi/page/android/
├── TurboStorePage.groovy      ← navegación home tienda, scroll, addProductos loop
├── TurboCartPage.groovy       ← validación canasta, btn irAPagar
├── TurboCheckoutPage.groovy   ← verificar Efectivo, tap Continuar, cerrar Modal PRO
├── TurboCashModalPage.groovy  ← seleccionar radio "No necesitaré cambio", tap Hacer pedido
├── TurboTipPage.groovy        ← verificar pantalla propina, tap Hacer pedido (coords)
└── TurboOrderTrackingPage.groovy ← validar estado "Seleccionando productos"
```

> **Reutilizar siempre:**
> - `UtilsPage.groovy` — scroll adaptativo y validación masiva de elementos
> - `DeviceResolutionPage.groovy` — escalado de coordenadas para TurboStorePage, TurboTipPage

### Keywords — Capa 2 (Steps)
```
Keywords/com/rappi/steps/android/
└── TurboSteps.groovy          ← @Keyword públicos: navigateToTurbo, addProductosUntilMinimum,
                                   goToCart, proceedToCheckout, handleProModal,
                                   verifyEfectivoSelected, tapContinuar,
                                   handleCashModal, tapHacerPedidoEnPropina,
                                   verifyOrderCreated
```

### Capa 3 — Script
```
Scripts/android/QA-20260409-turbo-compra/
└── Script<timestamp>.groovy   ← Orquestador: solo CustomKeywords.''() calls
```

### Test Case
```
Test Cases/android/
└── QA-20260409-turbo-compra.tc
```

---

## CustomKeywords y setUp a reutilizar

| Keyword / TC existente        | Ruta                                                   | Uso en este flujo                           |
|-------------------------------|--------------------------------------------------------|---------------------------------------------|
| `openRappi` (TC)              | `Test Cases/android/openRappi.tc`                      | setUp: abre app en DEV, verifica Home       |
| `UtilsPage.scroll*()`         | `Keywords/com/rappi/page/common/UtilsPage.groovy`      | Scroll hasta productos en Turbo Store       |
| `UtilsPage.validateElements()`| `Keywords/com/rappi/page/common/UtilsPage.groovy`      | Validar múltiples elementos en checkout     |
| `DeviceResolutionPage`        | `Keywords/com/rappi/page/common/DeviceResolutionPage.groovy` | Escalar coordenadas para Compose elements |

---

## Riesgos y mitigaciones

| # | Riesgo                                                                 | Mitigación                                                                         |
|---|------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 1 | **Banner "Estás lejos de la dirección"** aparece en Home y bloquea UI | `try/catch` en setUp. Si visible, cerrar con coordenada escalada (Compose sin acc.)|
| 2 | **Modal PRO "Envíos GRATIS"** aparece entre canasta y checkout        | Siempre verificar y cerrar `growth_prime_imageView_close` antes de validar checkout |
| 3 | **Tarjeta Turbo no visible** sin scroll en Home                        | Usar `Mobile.scrollToText("Turbo")` o scroll adaptativo de UtilsPage               |
| 4 | **Botón "+" es Compose NAF** — sin resource-id estable                | Usar `content-desc="add"` como locator primario. Fallback: coordenadas escaladas via DeviceResolutionPage |
| 5 | **Precios bajos en DEV** ($220/unidad) → muchos taps para $7.000      | Loop con 35 taps via adb o `Mobile.tap()` en loop. Verificar `lbl_minimoCompletado` |
| 6 | **RadioButton "No necesitaré cambio"** sin resource-id                | Locator por class + index (0). Fallback: coordenadas (96,1399) escaladas            |
| 7 | **"Hacer pedido" en propina** es Compose NAF sin accesibilidad        | Coordenadas fijas (540,2081) escaladas via `DeviceResolutionPage`                  |
| 8 | **Latencia en creación del pedido** — pantalla tracking puede tardar  | `waitForElementPresent(container_orderTracking, 15s)` antes de validar              |
| 9 | **Tienda Turbo no disponible** en DEV                                  | Precondición verificable: validar que tarjeta Turbo existe en home antes de tap     |

---

## Cobertura mínima recomendada

| Escenario                                      | Prioridad | Criterio de éxito                                              |
|------------------------------------------------|-----------|----------------------------------------------------------------|
| Happy path — compra completa con Efectivo      | P0 — MUST | Pedido creado, tracking screen visible con "Seleccionando productos" |
| Validación mínimo $7.000                       | P0 — MUST | Banner "¡Has completado el mínimo de compra!" visible antes de ir a canasta |
| Modal PRO manejado correctamente               | P1 — SHOULD | Modal se cierra y llega a checkout sin fallar                 |
| Modal Efectivo — opción "No necesitaré cambio" | P0 — MUST | CTA cambia a "Hacer pedido" al seleccionar la opción          |
| Propina → Hacer pedido final                   | P0 — MUST | Pantalla tracking visible post-tap                             |

---

## Criterios de aceptación mapeados a pasos

| Criterio de Aceptación (del RunId)                          | Paso(s) que lo valida    | Elemento verificado                                              |
|-------------------------------------------------------------|--------------------------|------------------------------------------------------------------|
| El usuario puede realizar compra en tiendas Turbo           | Paso 8 — final           | `container_order_tracking_screen` visible + "Seleccionando productos" |
| Solo puede comprar si canasta > $7.000                      | Paso 3 — durante loop    | `lbl_minimoCompletado` visible (square_notification_text)        |
| Método Efectivo disponible y seleccionable                  | Paso 5                   | `text="Efectivo"` visible en sección Método de pago              |
| Popup "Especifica monto" aparece al continuar con Efectivo  | Paso 6                   | `checkout_cash_modal_view_container` visible                     |
| "No necesitaré cambio" activa "Hacer pedido"                | Paso 7                   | `content-desc="Hacer pedido"` visible tras tap radio             |
| Propina de rappitendero mostrada antes del pedido final     | Paso 7→8                 | `lbl_reconoceEsfuerzo` visible                                   |

---

## Compatibilidad multi-dispositivo

| Paso | Elemento                    | Motivo coordenadas                                                      | Base de coordenadas | Escalado via                |
|------|-----------------------------|-------------------------------------------------------------------------|---------------------|-----------------------------|
| 1    | Cerrar banner "Lejos dirección" | View Compose sin accessibility node, sin content-desc              | 1080×2340           | `DeviceResolutionPage`      |
| 2    | Tap tarjeta Turbo           | `home_card_button` Compose — clickable en View padre, no expuesto en UIAutomator | 1080×2340 | `DeviceResolutionPage`  |
| 3    | Botón "+" producto          | `content-desc="add"` disponible como locator estable — coordenadas solo como fallback | 1080×2340 | `DeviceResolutionPage` |
| 8    | "Hacer pedido" en propina   | Compose NAF, clickable=true pero sin resource-id ni content-desc expuesto | 1080×2340        | `DeviceResolutionPage`      |

**Resolución objetivo primaria:** 1080×2340 (SM-S928B) — es la resolución base de `DeviceResolutionPage`.
**Dispositivos secundarios:** Cualquier Android compatible con Appium UiAutomator2 y la app Rappi DEV instalada.
**Plan de eliminación de coordenadas:** Reportar a equipo de desarrollo de Rappi que los elementos Compose críticos deben tener `semantics { contentDescription = "..." }` o `testTag` para accesibilidad en testing.

---

## Pasos validados en dispositivo — Resumen

| # | Pantalla                   | Acción realizada                               | Resultado observado                          | ✅ |
|---|----------------------------|------------------------------------------------|----------------------------------------------|-----|
| 1 | QA Screen DEV              | Tap "INICIAR RAPPI"                            | App reinicia y carga Home de Rappi           | ✅  |
| 2 | Home Rappi                 | Cerrar banner ubicación. Tap tarjeta Turbo     | Home de Turbo cargado con mínimo $7.000      | ✅  |
| 3 | Turbo Products (Bebidas)   | 35 taps en botón "+" Heineken $220             | Banner verde "¡Has completado el mínimo!" $7.480 | ✅ |
| 4 | Barra inferior Turbo       | Tap "Ir a canasta"                             | Vista canasta con 34 uds. Heineken $7.480    | ✅  |
| 4 | Canasta                    | Tap "Ir a pagar"                               | Modal PRO aparece → cerrar → Checkout abre  | ✅  |
| 5 | Checkout "Terminar y pagar"| Verificar Efectivo ya seleccionado             | "Efectivo" visible, total $14.680            | ✅  |
| 6 | Checkout                   | Tap "Continuar"                                | Popup "Por favor especifica el monto" emerge | ✅  |
| 7 | Popup efectivo             | Tap radio "No necesitaré cambio"               | CTA cambia a "Hacer pedido"                  | ✅  |
| 7 | Popup efectivo             | Tap "Hacer pedido"                             | Navega a pantalla propina rappitendero       | ✅  |
| 8 | Propina Rappitendero       | Tap "Hacer pedido" (coords 540,2081)           | Order tracking screen "Seleccionando productos" | ✅ |

---

## Instrucciones para BMO-TestCreator

### setUp a usar
```groovy
// Al inicio del Script, llamar TC openRappi para llegar al Home
WebUI.callTestCase(findTestCase('Test Cases/android/openRappi'), [:], FailureHandling.STOP_ON_FAILURE)
```

### Keywords a reutilizar (NO reimplementar)
```
com.rappi.page.common.UtilsPage          → scroll y validaciones masivas
com.rappi.page.common.DeviceResolutionPage → scaleX/scaleY para coordenadas Compose
```

### Nuevos archivos a crear (en orden)
1. `.rs` files en `Object Repository/android/TurboStore/`, `Canasta/`, `ModalPro/`, `Checkout/`, `ModalEfectivo/`, `Propina/`, `OrderTracking/`
2. `Keywords/com/rappi/page/android/TurboStorePage.groovy`
3. `Keywords/com/rappi/page/android/TurboCartPage.groovy`
4. `Keywords/com/rappi/page/android/TurboCheckoutPage.groovy`
5. `Keywords/com/rappi/page/android/TurboCashModalPage.groovy`
6. `Keywords/com/rappi/page/android/TurboTipPage.groovy`
7. `Keywords/com/rappi/page/android/TurboOrderTrackingPage.groovy`
8. `Keywords/com/rappi/steps/android/TurboSteps.groovy`
9. `Scripts/android/QA-20260409-turbo-compra/Script<timestamp>.groovy`
10. `Test Cases/android/QA-20260409-turbo-compra.tc`

### Patrón de naming Groovy (ejemplo TurboStorePage)
```groovy
package com.rappi.page.android

import com.kms.katalon.core.mobile.keyword.MobileBuiltInKeywords as Mobile
import com.kms.katalon.core.testobject.TestObject
import com.kms.katalon.core.testobject.ObjectRepository
import com.rappi.page.common.DeviceResolutionPage
import com.rappi.page.common.UtilsPage

class TurboStorePage {
    static DeviceResolutionPage deviceRes = new DeviceResolutionPage()

    static void tapTurboCard() {
        // home_card_button Compose — usar coordenadas escaladas
        int x = deviceRes.scaleX(787)
        int y = deviceRes.scaleY(1567)
        Mobile.tapAtPosition(x, y)
    }

    static void addProductsUntilMinimum(int maxTaps = 40) {
        // Tap "+" hasta que lbl_minimoCompletado sea visible
        for (int i = 0; i < maxTaps; i++) {
            Mobile.tap(findTestObject('Object Repository/android/TurboStore/btn_addProducto'), 2)
            if (Mobile.verifyElementVisible(findTestObject('...lbl_minimoCompletado'), false)) break
        }
    }
}
```

### Notas especiales para TestCreator
- **Botón "+" de productos**: usar `content-desc="add"` con `MobileLocatorStrategy.ACCESSIBILITY` en el `.rs`
- **RadioButton sin resource-id**: en el `.rs` usar XPATH: `//android.widget.RadioButton[@index='0']` dentro del modal container
- **Hacer pedido (Propina)**: es Compose NAF → SOLO coordenadas via `tapAtPosition` con `DeviceResolutionPage.scaleX(540)`, `scaleY(2081)`
- **Loop de productos**: implementar en `TurboStorePage.addProductsUntilMinimum()` con contador máximo
- **Modal PRO**: siempre manejar en `TurboCheckoutPage.proceedToCheckout()` con try/catch

---

## Dumps capturados durante validación (BMO-Explorer — 2026-04-09)

> ⚡ Reutilizar estos dumps en MODO CAPTURA sin re-navegar el dispositivo.

| Paso | Pantalla                  | Archivo dump local                       | Estado validación |
|------|---------------------------|------------------------------------------|-------------------|
| 1    | QA Screen DEV             | /tmp/val_paso1_qascreen.xml              | ✅ resource-id button_start_app confirmado |
| 1    | Home Rappi                | /tmp/val_paso1_home.xml                  | ✅ home_card_button, text=Turbo, text=Restaurante, banner riesgo |
| 2    | Turbo Store Home          | /tmp/val_paso2_turbo.xml                 | ✅ Mínimo $7,000, Bebidas, search bar |
| 3    | Bebidas (productos)       | /tmp/val_paso3_bebidas.xml               | ✅ content-desc=add, Heineken $220 |
| 3b   | Bebidas (contador activo) | /tmp/val_paso3b.xml                      | ✅ square_notification_text, Ir a canasta bounds exactos |
| 4a   | Canasta Nitro             | /tmp/val_paso4_canasta.xml               | ✅ basketui_text_view_product_name/price, Ir a pagar |
| 4b   | Modal PRO                 | /tmp/val_paso4b_modal.xml                | ✅ growth_prime_imageView_close [925,551][1015,641] |
| 5    | Checkout Terminar y pagar | /tmp/val_paso5_checkout.xml              | ✅ Efectivo, Continuar [540,2013][1024,2148] |
| 6    | Modal Efectivo            | /tmp/val_paso6_cashmodal.xml             | ✅ checkout_cash_modal_view_container, RadioButtons |
| 7a   | Modal Efectivo (post-tap) | /tmp/val_paso7_nocambio.xml              | ✅ RadioButton checked=true, Hacer pedido [135,1991][945,2149] |
| 7b   | Propina Rappitendero      | /tmp/val_paso7b_propina.xml              | ✅ ¡Reconoce su esfuerzo!, Hacer pedido Compose NAF |
| 8    | Order Tracking            | /tmp/val_paso8_tracking.xml              | ✅ container_order_tracking_screen, Seleccionando productos |

### Ajustes identificados durante validación (⚠️ no bloqueantes)

| # | Ajuste | Detalle | Impacto en automation |
|---|--------|---------|----------------------|
| A1 | Coord Y tarjeta Turbo | Plan dice y=1567; actual y=1717 (card "Pedido entregado" empuja las tarjetas hacia abajo). El X=787 coincide exactamente. | TestCreator: scroll hasta que Turbo sea visible antes de tap. Preferir `Mobile.scrollToText("Turbo")` + tapAtPosition |
| A2 | Counter "+" Compose NAF | Después del primer add, el "+" del contador NO está en UIAutomator. Coordenada: device (413, 860). Primera add usa content-desc="add" correctamente. | TestCreator: `TurboStorePage.addProductsUntilMinimum()` debe usar tapAtPosition(scaleX(413), scaleY(860)) para taps del contador |
| A3 | Total checkout $16.080 | Plan dice $14.680. Diferencia por delivery fee actualizado en DEV. No afecta criterios de aceptación. | Sin impacto en criterios P0 |
| A4 | Propina default 18% | Plan dice 14%. La pantalla muestra 18%/$1.350. No afecta el flujo. | Sin impacto — el TestCreator no valida % específico |
| A5 | Botón "Hacer pedido" propina | Confirmado Compose NAF — sin content-desc ni resource-id. Coordenada (540,2081) funciona correctamente. | TestCreator: usar SOLO tapAtPosition con DeviceResolutionPage.scaleX/scaleY |

---

## Instrucciones para BMO-Explorer

1. Validar que todos los locators de la tabla de componentes sean correctos y alcanzables
2. Verificar que el punto de entrada `openRappi` cubre correctamente la apertura en DEV (incluyendo QA Screen)
3. Confirmar que la estrategia de loop para agregar productos es viable automáticamente
4. Validar que la estructura de archivos propuesta es consistente con el proyecto existente
5. Confirmar que los pasos con coordenadas tienen su par escalado via `DeviceResolutionPage`
6. Si aprueba: cambiar `PlanStatus` a `Approved`, llenar `ApprovedBy`, `ApprovalDate`, `ApprovalNotes`
7. Si rechaza: llenar `RejectionNotes` con razón específica. BMO-FlowPlanner revisará (máx 3 intentos)

**Archivo de contexto:** `.github/agents/context/flowplanner/QA-20260409-turbo-compra-turbo-compra.md`
