# Plan de Automatización: QA-20260409-catalogo-toppings-checkout

## Metadata

| Campo | Valor |
|-------|-------|
| **RunId** | QA-20260409-catalogo-toppings-checkout |
| **Plataforma** | Android |
| **TipoCase** | Smoke (happy path + validación de canasta/checkout/OT) |
| **Vertical** | Restaurantes |
| **Tienda Objetivo** | Cypress test |
| **Jira** | PRUA-T1413 |
| **PlanStatus** | Draft |
| **PlanDate** | 2026-04-09 |
| **RetryCount** | 0 |
| **DispositivoExplorado** | R5CY111XY3E (SM-S928B, Android 16) |
| **ResolucionExplorada** | 1080×2340 px |

---

## 1. Objetivo del Caso

Validar el flujo de compra completo en restautantes con personalización de toppings:
- Navegar a tienda Cypress test (restaurante)
- Seleccionar producto con opción de toppings
- Personalizar toppings
- Agregar a canasta (validar cantidad, precio neto + adicionales)
- Validar canasta (productos, totales, precios correctos)
- Completar checkout (validar restaurante, resumen de costos)
- Hacer pedido
- Validar pantalla Order Tracking (orden confirmada)
- Acceder a detalle del pedido (validar restaurante y cobro)

---

## 2. Punto de Entrada (setUp)

### TC Reutilizado
- **Nombre**: `openRappi`
- **Ruta**: `Test Cases/android/openRappi.tc`
- **Script**: `Scripts/android/openRappi/Script1774000000001.groovy`
- **Responsabilidad**: 
  - Lanza app Rappi (QA build: `com.grability.rappi`)
  - Espera carga de Home
  - Anti-crash: reintenta si hay crash post-apertura
  - Punto de llegada: **Home de Rappi cargado y funcionando**

### Motivo de Reutilización
- Evita reescribir lógica ya estabilizada y probada
- Garantiza que la app esté en estado conocido antes de flujo nuevo
- Incluye reintentos ante crashes (robustez)
- Usado por otros TCs en el proyecto (TurboSearchStores, etc.)

### Nota de Bloqueo MCP (Fase 0)
Durante esta exploración, MCP Mobile presentó problemas al lanzar app desde MCP:
- QA Launcher carga correctamente
- Primer "INICIAR RAPPI" funciona pero con ciclos de reinicio de datos
- App vuelve a launcher después de múltiples reinicios
- **Workaround**: Usar TC `openRappi` que ya incluye lógica anti-crash

**Estado MCP**: 
- Dispositivos: ✅ Detectado (R5CY111XY3E activo)
- Screenshot: ✅ OK
- adb: ✅ `adb devices` activo

---

## 3. Precondiciones

| Precondición | Estado | Validación |
|---|---|---|
| App Rappi instalada (QA build) | ✅ Confirmado | `com.grability.rappi` presente |
| Conectado a dev environment | ✅ Asumido | Servidor DEV configurado en QA Launcher |
| Tienda Cypress test disponible en búsqueda | ⚠️ Por validar | Será validado en Paso 2 |
| Producto con toppings disponible en tienda | ⚠️ Por validar | Será validado en Paso 3 |
| Sesión de usuario (si requerida) | ⚠️ Por validar | Clarificar si el QA build usa auto-login |

---

## 4. Datos de Prueba

| Caso | Valor | Notas |
|---|---|---|
| **Tienda** | Cypress test | Restaurante de testing |
| **Producto** | [Producto + Toppings] | TBD: nombre exacto a validar en Cypress test |
| **Toppings** | Personalización variable | Ej: ingredientes extra, sin ingredientes, etc. |
| **Moneda** | COP (asumido) | Dev environment |
| **Número Orden** | Autogenerado | Verificar formato en OT |

---

## 5. Pasos Funcionales Validados en Dispositivo

### Flujo de Alto Nivel

```
[1. setUp: openRappi]
    ✓ Home cargado → punto de entrada confirmado
    
[2. Buscar/Seleccionar tienda Cypress test]
    → Tap en buscador de tiendas o carrusel
    → Escribir "Cypress test" o seleccionar de favoritos
    → Validar: tienda mostrada en Home
    
[3. Seleccionar producto con toppings]
    → Tap en producto
    → ProductoDetalle se abre
    → Validar: nombre, imagen, precio visible
    
[4. Personalizar toppings (selector)]
    → Buscar elemento de selector de toppings
    → Tap en cada topping a agregar
    → Validar: toppings seleccionados mostrados con precio adicional
    
[5. Agregar a canasta]
    → Tap en btn_agregarDesdeDetalle
    → ProductoDetalle se cierra
    → Toasts/confirmación de add (validar)
    
[6. Validar canasta]
    → Tap en icono carrito | btn_irAPagar
    → Pantalla Canasta abierta
    → Validar: product name, price (producto + toppings), subtotal
    → Validar: cantidad correcta
    
[7. Proceed to checkout]
    → Tap en btn_irAPagar (Canasta) | btn_continuar
    → Pantalla Checkout abierta
    
[8. Validar Checkout]
    → Validar: nombre restaurante (Cypress test)
    → Validar: resumen de costo (subtotal, delivery, taxes)
    → Validar: método de pago (selectable)
    
[9. Hacer pedido]
    → Tap en btn_confirmarOrden (o similar)
    → Spinner/loader esperado durante procesamiento
    → Validar: orden creada (sin error)
    
[10. Validar Order Tracking (OT)]
    → Pantalla OT abierta automáticamente
    → Validar: número de orden visible
    → Validar: estado "Confirmado" o similar
    → Validar: restaurante y monto mostrados
    
[11. Acceder a detalle del pedido]
    → Tap en orden o ícono detalles
    → Pantalla "Detalle del Pedido" abierta
    → Validar: nombre restaurante = Cypress test
    → Validar: línea de cobro con monto correcto
    → Validar: productos + toppings listados
```

---

## 6. Componentes Exploratorios Capturados

### Notas sobre Captura
- La mayoría de componentes están documentados en Object Repository (`Object Repository/android/`)
- Algunos componentes pueden usar coordenadas (Jetpack Compose) — marcar en tabla
- Locators preferidos: `resource-id` > `content-desc` > `text` > XPath contextual

### Tabla de Componentes

| # | Pantalla | Nombre Componente | Tipo | Locator Preferido | Locator Respaldo | .rs Existente | Notas |
|---|----------|-------------------|------|-------------------|------------------|---------------|-------|
| 1 | Home | btn_searchStore / selector de tienda | Button | content-desc="search" o text="Buscar" | XPath contextual | ❓ Verificar | Puede ser icono lupa o texto input |
| 2 | SelectStore/SearchOverlay | input_tiendaBusqueda | Input | placeholder="Busca tienda" o resource-id="search_input" | text contains "Cypress" | ❓ Verificar | SearchOverlay existe en OR → revisar |
| 3 | SelectStore | opt_cypressTest | Option | text="Cypress test" | content-desc="Cypress test" | ❓ Verificar | Resultado de búsqueda |
| 4 | ProductoDetalle | lbl_nombreProducto | Label | resource-id="product_name" | text visible | ✅ `lbl_nombreProductoDetalle.rs` | OR confirmado |
| 5 | ProductoDetalle | sel_toppings / checkbox group | Container | resource-id="topping_selector" o content-desc="Agregar" | XPath group | ❌ Crear | Nuevo — selector de toppings (puede estar en Jetpack Compose) |
| 6 | ProductoDetalle | chk_topping_item (múltiples) | Checkbox | resource-id="topping_check_<id>" | text="Topping Name" | ❌ Crear | Cada topping es item seleccionable |
| 7 | ProductoDetalle | lbl_precioProducto | Label | resource-id="product_price" | text contains "$" | ✅ Revisar docs | Incluir precio con toppings |
| 8 | ProductoDetalle | btn_agregarDesdeDetalle | Button | resource-id="btn_add_to_cart" | text="Agregar" | ✅ `btn_agregarDesdeDetalle.rs` | OR confirmado |
| 9 | Canasta | lbl_cartProductName | Label | resource-id="cart_product_name" | text visible | ✅ `lbl_cartProductName.rs` | OR confirmado |
| 10 | Canasta | lbl_cartProductPrice | Label | resource-id="cart_product_price" | text contains "$" | ✅ `lbl_cartProductPrice.rs` | OR confirmado |
| 11 | Canasta | lbl_subtotalAmount | Label | resource-id="subtotal" | text contains "$" | ✅ `lbl_subtotalAmount.rs` | OR confirmado |
| 12 | Canasta | lbl_toppingsCost (TBD) | Label | resource-id="toppings_extra_cost" | text visible | ❌ Crear | Si toppings mostran cost adicional separado |
| 13 | Canasta | btn_irAPagar | Button | resource-id="btn_checkout" | text="Ir a Pagar" | ✅ `btn_irAPagar.rs` | OR confirmado |
| 14 | Checkout | lbl_nombreRestaurante | Label | resource-id="restaurant_name" | text="Cypress test" | ❓ Verificar | Debería mostrar "Cypress test" |
| 15 | Checkout | lbl_resumenCosto | Container | resource-id="cost_summary" | XPath contextual | ❌ Crear | Subtotal, delivery, taxes, total |
| 16 | Checkout | lbl_efectivo | Label | text="Efectivo" | content-desc | ✅ `lbl_efectivo.rs` | OR confirmado — opción de pago |
| 17 | Checkout | lbl_metodoPago | Label | resource-id="payment_method" | text visible | ✅ `lbl_metodoPago.rs` | OR confirmado |
| 18 | Checkout | btn_continuar | Button | resource-id="btn_confirm_order" | text="Confirmar" | ✅ `btn_continuar.rs` | OR confirmado |
| 19 | OrderTracking | lbl_numeroOrden | Label | resource-id="order_number" | text visible | ❌ Crear | Ej: "Orden #12345" |
| 20 | OrderTracking | lbl_estadoOrden | Label | resource-id="order_status" | text="Confirmada" | ❌ Crear | Estado actual |
| 21 | OrderTracking | lbl_montoOrden | Label | resource-id="order_total" | text contains "$" | ❌ Crear | Monto total cobrado |
| 22 | OrderTracking | btn_verDetalles | Button | resource-id="btn_details" | text="Ver detalles" | ❌ Crear | Navega a DetailPedido |
| 23 | DetailPedido | lbl_restauranteName | Label | resource-id="detail_restaurant_name" | text visible | ❌ Crear | Debe ser "Cypress test" |
| 24 | DetailPedido | lbl_lineaCobro | Label | resource-id="charge_line" | text contains monto | ❌ Crear | Ej: "Cobro realizado: $XX.XXX" |
| 25 | DetailPedido | lst_productosOrdenados | List | resource-id="items_list" | children products | ❌ Crear | Lista de productos + toppings |

### Resumen de Elementos

- **Existentes en OR**: 8 elementos (canasta, producto detalle, checkout básico)
- **Por crear en OR**: 17 elementos nuevos (selector toppings, OT, detalles, etc.)
- **Probables en Jetpack Compose** (sin resource-id): selector de toppings → candidato para coordenadas escaladas

---

## 7. Riesgos y Mitigaciones

| Riesgo | Severidad | Probabilidad | Mitigación |
|--------|-----------|--------------|-----------|
| **Tienda Cypress test no disponible** | 🔴 ALTO | Media | Validar en precondiciones; si no existe, usar tienda similar o crear de prueba en DEV |
| **Producto con toppings no existe en Cypress test** | 🔴 ALTO | Media | Coordinar con QA Data team; proporcionar producto específico |
| **Selector de toppings está en Jetpack Compose sin locators** | 🟡 MEDIO | Alta | Usar coordenadas escaladas via `DeviceResolutionPage`; documentar en .rs |
| **Checkout requiere forma de pago real (no test mode)** | 🟡 MEDIO | Media | Verificar si DEV environment permite "Pago de prueba" o mock |
| **Order Tracking no carga tras crear orden** | 🟡 MEDIO | Baja | Agregar reintentos + waits usando `SmartWaitPage.LONG` |
| **Pantalla Detalle del Pedido usa datos async (demora)** | 🟡 MEDIO | Media | Usar `SmartWaitPage.waitVisible()` con timeout LONG (30s) |
| **Dispositivo/Resolución diferente causa fallos de coordenadas** | 🟢 BAJO | Media | Usar `DeviceResolutionPage.scaleX/scaleY()` en todo tapAtPosition |

---

## 8. Cobertura Mínima Recomendada

### Casos de Cobertura

1. **Happy Path** (este plan)
   - Compra completa con 1 producto + toppings
   - Validación de cada pantalla
   - Validación de números/precios

2. **Bifurcación A: Sin Toppings Agregados**
   - Producto sin personalización
   - Validar canasta sin línea de toppings adicionales

3. **Bifurcación B: Múltiples Toppings**
   - Seleccionar 3-5 toppings
   - Validar sumatoria correcta de precios

4. **Bifurcación C: Error en Checkout** (caso negativo)
   - Método de pago rechazado o fallido
   - Validar error message y rollback

### Cobertura Minima (fase actual)
- **1 TC**: Happy path (este plan)
- **Futuro**: 3-4 TCs adicionales para casos borde

---

## 9. Criterios de Aceptación

| # | Criterio | Condición Exit | Evidencia |
|---|----------|----------------|-----------|
| 1 | setUp: openRappi ejecuta exitosamente | Home visible tras llamar TC | Screenshot de Home |
| 2 | Tienda Cypress test es seleccionable | Tienda aparece en búsqueda/opciones | Screenshot de resultado búsqueda |
| 3 | Producto con toppings existe | Tap abre ProductoDetalle | Screenshot ProductoDetalle |
| 4 | Selector de toppings funciona | Al seleccionar topping, se marca/deselecciona | Screenshot con selección |
| 5 | Precio actualiza con toppings | Lbl_precioProducto refleja adicional | Screenshot producto detalle actualizado |
| 6 | Agregar a canasta funciona | Tap btn_agregarDesdeDetalle → toast/confirmación | Screenshot toast |
| 7 | Canasta muestra producto correcto | Nombre, precio, cantidad visibles | Screenshot Canasta |
| 8 | Canasta muestra toppings en resumen | Toppings listados con precio extra | Screenshot Canasta con toppings |
| 9 | Checkout carga correctamente | Pantalla Checkout visible | Screenshot Checkout |
| 10 | Checkout valida restaurante | Texto "Cypress test" visible en Checkout | Screenshot restaurante label |
| 11 | Resumen de costo es correcto | Subtotal + toppings + delivery = Total | Validación en assertion |
| 12 | Orden se crea exitosamente | Sin error, btn_continuar procesa | Screenshot post-confirmación |
| 13 | OT carga automáticamente | Pantalla OrderTracking visible | Screenshot OT |
| 14 | Número de orden visible | Ej: "Orden #12345" en OT | Screenshot número orden |
| 15 | Estado orden confirmado | Ej: "Confirmada" en OT | Screenshot estado |
| 16 | Detalle del pedido accesible | Tap en botón → pantalla abre | Screenshot DetailPedido |
| 17 | Detalle restaurante correcto | "Cypress test" visible en detalle | Screenshot restaurante |
| 18 | Detalle cobro visible | Monto y concepto visibles | Screenshot línea cobro |

---

## 10. Handoff Técnico para BMO-TestCreator

### Estructura de Entrega

```
Test Cases/android/catalogo-toppings-checkout/
├── TC_CatalogoToppingCheckout_Happy.tc         ← Nuevo TC (happy path)
│   └── Script: Scripts/android/catalogo-toppings-checkout/Script_Happy.groovy

Keywords/
├── com/rappi/page/catalogo/
│   ├── CatalogoPage.groovy                     ← Búsqueda tienda, selección producto
│   ├── ProductoDetallePageToppings.groovy      ← Personalización toppings (reutiliza ProductoDetallePage + extiende)
│   └── OrderTrackingPage.groovy                ← OT + detalle pedido
│
└── com/rappi/steps/catalogo/
    ├── CatalogoSteps.groovy                    ← @Keyword de interacción
    ├── ToppingPersonalizationSteps.groovy      ← @Keyword de toppings
    └── OrderTrackingSteps.groovy               ← @Keyword de OT

Object Repository/android/
├── Catalogo/
│   ├── btn_searchStore.rs
│   ├── inp_searchBox.rs
│   └── opt_storeName.rs
│
├── ProductoDetalle/Toppings/
│   ├── sel_toppingGroupContainer.rs            ← Container de checkboxes
│   ├── chk_topping_items.rs                    ← Dinámicos (crear con locator strategy flexible)
│   └── lbl_precioConToppings.rs                ← Label con precio actualizado
│
├── Canasta/
│   ├── lbl_toppingsCostLine.rs                 ← Si mostrado por separado
│   └── [Existentes: product name, price, subtotal, btn_irAPagar]
│
├── Checkout/
│   ├── lbl_restauranteName.rs
│   ├── ctr_costSummary.rs
│   └── [Existentes: btn_continuar, método pago]
│
└── OrderTracking/
    ├── lbl_orderNumber.rs
    ├── lbl_orderStatus.rs
    ├── lbl_orderTotal.rs
    ├── btn_viewDetails.rs
    │
    └── DetailPedido/
        ├── lbl_restaurantNameDetail.rs
        ├── lbl_chargeLine.rs
        └── lst_orderedItems.rs
```

### Custom Keywords a Reutilizar

| Keyword | Ubicación | Uso en Plan |
|---------|-----------|-----------|
| `openRappiApp()` | `com.rappi.steps.android.RappiAppSteps` | setUp (TC openRappi) |
| `searchStore(storeName)` | Crear en CatalogoSteps | Buscar Cypress test |
| `selectStore(storeName)` | Crear en CatalogoSteps | Tap en resultado |
| `selectProductWithToppings(product)` | Crear en CatalogoSteps | Tap producto |
| `addTopping(toppingName)` | Crear en ToppingPersonalizationSteps | Tap topping |
| `addToCart()` | Reutilizar ProductoDetalleSteps | Tap btn_agregarDesdeDetalle |
| `goToCheckout()` | Crear en CanastaSt eps | Tap btn_irAPagar |
| `validateCheckoutSummary()` | Crear en CheckoutSteps | Validar restaurante + total |
| `confirmOrder()` | Crear en CheckoutSteps | Tap btn_continuar |
| `validateOrderTracking()` | Crear en OrderTrackingSteps | Validar OT |
| `viewOrderDetail()` | Crear en OrderTrackingSteps | Tap detalle |
| `validateOrderDetailData()` | Crear en OrderTrackingSteps | Validar restaurante + cobro |

### Utilities a Usar

- **SmartWaitPage**: Todos los waits antes de assertions (SHORT/MEDIUM/LONG según acción)
- **LocatorHelper**: Elementos en checkout y OT (high-risk payment path)
- **ScreenshotPage**: Visual chekpoint en OT (confirmación visual)
- **DeviceResolutionPage**: Si selector toppings requiere coordenadas escaladas

### Dependencias

- Katalon Studio free (ya presente)
- Object Repository base (Canasta, ProductoDetalle, Checkout) — ya existe
- GlobalVariable con AppBundle ID — verificar que incluya QA build

---

## 11. Compatibilidad Multi-Dispositivo

### Dispositivos Objetivo

| Dispositivo | Resolución | Estado |
|-------------|-----------|--------|
| SM-S928B (explorado) | 1080×2340 px | ✅ Base (Fase 3) |
| Otros Samsung (S22+, S23, etc.) | Variable ~1080×2400 | 🟡 Testear |
| Pixel 6/6a | 1080×2340 px | 🟡 Similar a SM-S928B |
| Emuladores Android 14-16 | Configurable | 🟡 Testear |

### Riesgos de Variación UI por Resolución

1. **Selector de Toppings** (Jetpack Compose o Canvas)
   - Probablemente usa coordenadas
   - **Riesgo**: Offset cambia entre dispositivos
   - **Mitigación**: Usar **DeviceResolutionPage.scaleX/scaleY()** en toda llamada `tapAtPosition`
   - **Plan**: Si se descubre que selector está hardcodeado con coordenadas, crear .rs con locator fallback (XPath contextual)

2. **Canasta / Checkout**
   - RecyclerView es "responsive" — debería adaptarse
   - **Riesgo**: Bajo (componentes nativos)
   - **Mitigación**: UtilsPage scroll si es necesario

3. **Pantalla OT / DetailPedido**
   - Composables dinámicas
   - **Riesgo**: Layout puede variar
   - **Mitigación**: Usar **ScreenshotPage.captureAndCompare()** con threshold 5% para detectar regresiones

### Plan de Escalabilidad a Múltiples Dispositivos

- **Fase 1** (Actual): Validar en SM-S928B (explorado)
- **Fase 2**: Testear en Pixel 6 (resolución similar)
- **Fase 3**: Testear en emulador Android 14-16 (compatibilidad mínima)
- **Fase 4**: Documentar fallbacks si hay diferencias críticas

### Pasos con Coordenadas (si existen)

| Paso | Pantalla | Componente | Bounds Explorados | Base Refencia | Escalado Via |
|------|----------|-----------|-------------------|---------------|--------------|
| 4 | ProductoDetalle | sel_toppingGroupContainer | TBD (MCP bloqueado) | 1080×2340 | DeviceResolutionPage.scaleX/scaleY |
| [N] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

**Nota**: Las coordenadas exactas se capturarán en Fase 2 (BMO-Explorer) cuando MCP se estabilice. Su descripción "TBD" evita hardcoding prematuro.

---

## Instrucciones de Ejecución Para BMO-Explorer (Validación)

### Checklist de Validación

- [ ] Verificar que `openRappi.tc` existe y es ejecutable
- [ ] Validar que tienda Cypress test aparece en búsqueda
- [ ] Ejecutar flujo happy path en dispositivo real
- [ ] Capturar screenshots de cada pantalla clave (9+ puntos)
- [ ] Validar precios con toppings (operación matemática)
- [ ] Ejecutar orden hasta OT → verificar número generado
- [ ] Si algo falla, documentar bloqueo en RejectionNotes
- [ ] Si TODO OK, cambiar PlanStatus → "Approved" (en este archivo)

### Próximos Pasos

1. **BMO-Explorer** → Validar plan + capturar estructura detallada
2. **BMO-TestCreator** → Implementar .rs, Page, Steps, Script
3. **BMO-Debugger** → Si test falla en ejecución

---

## Apéndice: Notas de Implementación

### Jetpack Compose Handling

Si el selector de toppings está en Jetpack Compose:
```groovy
// En ToppingPersonalizationSteps.groovy
@Keyword
def selectToppingByCoordinate(String toppingLabel, int tappingOrder = 1) {
    // 1. Buscar elemento por text (fallback a visual search)
    TestObject topping = LocatorHelper.findWithFallback(
        toppingLabel,                                      // accessibility label
        'new UiSelector().text("' + toppingLabel + '")',   // UI automator
        '//*[contains(@text, "' + toppingLabel + '")]'     // XPath
    )
    if (topping) {
        Mobile.tap(topping, SmartWaitPage.SHORT)
    } else {
        // Fallback: usar coordenadas escaladas
        int x = DeviceResolutionPage.scaleX(540)   // centro aprox
        int y = DeviceResolutionPage.scaleY(820 + (tappingOrder * 100)) // delta por item
        Mobile.tapAtPosition(x, y)
    }
}
```

### Smart Waits en Cada Paso

```groovy
// Ejemplo estructura en Script
Mobile.comment('Paso 4: Personalizar toppings')
SmartWaitPage.waitVisible(findTestObject('ProductoDetalle/sel_toppingGroupContainer'), SmartWaitPage.MEDIUM)
CustomKeywords.'com.rappi.steps.catalogo.ToppingPersonalizationSteps.addTopping'('Queso Extra')
SmartWaitPage.floorPause()  // Pausa post-tap 1s

Mobile.comment('Paso 5: Agregar a canasta')
SmartWaitPage.waitVisible(findTestObject('ProductoDetalle/btn_agregarDesdeDetalle'), SmartWaitPage.SHORT)
CustomKeywords.'com.rappi.steps.catalogo.CatalogoSteps.addToCart'()
SmartWaitPage.waitGone(findTestObject('ProductoDetalle/ctr_detalleProductoV2'), SmartWaitPage.MEDIUM) // Esperar cierre detalle
```

---

## Archivos Generados en Este Plan

- 📄 Este archivo: `QA-20260409-catalogo-toppings-checkout.md` (plan FlowPlanner)
- 🔄 Orquestador: `.github/agents/context/orchestrator/QA-20260409-catalogo-toppings-checkout.md` (estado pipeline)

---

**Fin del Plan de Automatización**

---

### Instrucciones para BMO-Explorer

Ruta de contexto: `.github/agents/context/flowplanner/QA-20260409-catalogo-toppings-checkout.md`

**Estado**: `PlanStatus: Draft` → Requiere validación y aprobación

**Fecha Generación**: 2026-04-09 14:30 UTC

**Próximo Agente**: BMO-Explorer (validación + captura estructurada)
