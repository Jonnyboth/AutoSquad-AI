# Flow Context — QA-20260414-turbo-compra — Compra Turbo con Fecha Programada

---

## Metadatos del plan

| Campo                  | Valor                                                                |
|------------------------|----------------------------------------------------------------------|
| RunId                  | QA-20260414-turbo-compra                                             |
| Flujo                  | Compra en TurboDev con selección de fecha/hora programada            |
| Plataforma             | android                                                              |
| Tipo                   | Smoke Test                                                           |
| PlanStatus             | Approved                                                             |
| RetryCount             | 0                                                                    |
| ApprovedBy             | BMO-Explorer                                                         |
| ApprovalDate           | 2026-04-14                                                           |
| CaptureDate            | 2026-04-14                                                           |
| CapturedBy             | BMO-Explorer                                                         |
| ApprovalNotes          | Todos los pasos confirmados en dispositivo R5CY111XY3E. Ajustes menores documentados: (1) pill_fechaFutura usa text dinámico — coordenadas (470,745) ajustadas a (463,734) para la segunda pill. (2) btn_continuarScheduling NO expone content-desc en UIAutomator — es android.widget.Button vacío, usar coords (540,2081) como primario. (3) sáb abr 11 tiene 7+ slots (plan decía 2-3) — no bloqueante. |
| RejectionNotes         |                                                                      |
| Fecha                  | 2026-04-14                                                           |
| DispositivoExplorado   | SM-S928B (R5CY111XY3E) — Android 16                                  |
| ResolucionExplorada    | 1080×2340 px (es la resolución base del proyecto)                    |
| AgenteAutor            | BMO-FlowPlanner                                                      |
| PlanBase               | QA-20260409-turbo-compra-turbo-compra.md (pasos 1-5 y checkout reutilizados) |
| TCName                 | TC_TurboCompraConFechaProgramada                                     |

---

## Objetivo del caso

Validar el flujo de compra en **TurboDev** con el **paso intermedio de programación de entrega** (`Programa tu pedido`), introducido entre la canasta y el checkout. El flujo valida:
- Aparición de la pantalla `Programa tu pedido` al tap "Ir a pagar" desde la canasta
- Selección de fecha futura (> primer slot disponible) desde el selector de fechas
- Selección de franja horaria → habilitación del botón "Continuar"
- Navegación al checkout con la **fecha/hora programada visible**
- Completar compra con Efectivo → pedido en tracking

---

## Diferencia clave vs QA-20260409

| Aspecto | QA-20260409 (original) | QA-20260414 (este plan) |
|---------|------------------------|--------------------------|
| Pantalla post "Ir a pagar" | Checkout directo (o Modal PRO) | Pantalla "Programa tu pedido" NUEVA |
| Selector de fecha/hora | No existía | ✅ Presente — requiere selección explícita |
| Checkout | Solo método pago + total | Muestra además fecha/hora programada |
| TC name | QA-20260409-turbo-compra | TC_TurboCompraConFechaProgramada |

---

## Punto de entrada (setUp)

| Campo            | Valor                                                                |
|------------------|----------------------------------------------------------------------|
| TC reutilizado   | `openRappi` — `Scripts/android/openRappi/Script1774000000001.groovy` |
| Motivo           | El flujo parte desde Home de Rappi ya cargado. `openRappi` maneja QA screen DEV y verificación de Home. |
| Llamada sugerida | `WebUI.callTestCase(findTestCase('Test Cases/android/openRappi'), [:], FailureHandling.STOP_ON_FAILURE)` |

> ⚠️ Si la app abre en QA screen DEV, `openRappi` maneja el `resource-id="com.grability.rappi:id/button_start_app"` automáticamente.

---

## Precondiciones

| # | Precondición                                                                       |
|---|------------------------------------------------------------------------------------|
| 1 | Dispositivo Android conectado con `adb devices` en estado `device`                 |
| 2 | App `com.grability.rappi` instalada en ambiente DEV (Monolito)                     |
| 3 | Usuario autenticado: Jhon — CO_101459658 en DEV                                    |
| 4 | Dirección configurada: Cl. 93 #19-58, Bogotá, Colombia                             |
| 5 | Método de pago Efectivo configurado en la cuenta                                   |
| 6 | Tienda Turbo disponible y operativa en DEV                                         |
| 7 | Conexión a internet activa                                                         |
| 8 | `GlobalVariable.G_Platform = "android"` en Profile default                         |
| 9 | Al menos una fecha futura disponible en el selector de scheduling                  |

---

## Datos de prueba

| Variable             | Valor                          | Observación                                        |
|----------------------|--------------------------------|----------------------------------------------------|
| Tienda objetivo      | Super Tienda Turbo (Nitro.)    | Identificada como "Turbo Express" en Home          |
| Mínimo de compra     | $7.000                         | Validado en-app                                    |
| Producto usado       | Heineken Cerveza 0.0 Alcohol   | $220/unidad — 1 × 250 mL                          |
| Unidades requeridas  | ≥ 32 (se usan 36 en prueba)    | 36 × $220 = $7.920 → supera $7.000 ✅              |
| Fecha seleccionada   | Fecha futura disponible en app | En DEV explorado: "jue abr 16" como futuro         |
| Slot horario         | Cualquier franja disponible    | En DEV explorado: "8:00 am - 9:00 am"             |
| Método de pago       | Efectivo                       | Ya preseleccionado en cuenta del usuario de prueba |
| Opción de cambio     | No necesitaré cambio           | Activa CTA "Hacer pedido"                          |

---

## Pasos funcionales validados en dispositivo

### Paso 1 — Abrir app de Rappi en ambiente DEV → Ver Home
*(COPIADO de QA-20260409 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | App instalada. Puede estar cerrada o en background.                  |
| Acción         | `setUp`: llamar TC `openRappi`                                       |
| Bifurcación    | QA screen: tap `btn_startApp` (resource-id estable)                  |
| Bifurcación    | Banner "Estás lejos de la dirección": cerrar con X (Compose ~[906,463]) |
| Validación     | Home de Rappi cargado — tarjetas "Restaurante" y "Turbo" visibles    |
| Estado post    | Home screen con `home_card_button` visibles                          |
| Wait Strategy  | `SmartWaitPage.waitVisible(home_card_button, SmartWaitPage.MEDIUM)`  |
| Riesgo         | Banner ubicación bloquea UI → try/catch                              |

---

### Paso 2 — Tap en tarjeta Turbo → Ver Home de la tienda Turbo
*(COPIADO de QA-20260409 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Home de Rappi cargado                                                |
| Acción         | Tap tarjeta Turbo — `resource-id="home_card_button"` via coords escaladas |
| Coordenadas    | Base 1080×2340 → x=787, y=1567                                       |
| Validación     | Home Turbo: título "Super Tienda Turbo", "Mínimo de compra $7,000", pill "Entrega en ⚡ Hoy, 10 AM" |
| Estado post    | Pantalla Turbo Store Home                                            |
| Wait Strategy  | Pre-tap: `SmartWaitPage.waitVisible(home_card_button, SmartWaitPage.SHORT)` · Post-tap: `waitVisible(lbl_minimoCompra, SmartWaitPage.MEDIUM)` |
| Riesgo         | Tarjeta fuera de pantalla → scroll si no visible                     |

---

### Paso 3 — Scroll y agregar productos hasta > $7.000
*(COPIADO de QA-20260409 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Turbo Store Home cargado                                             |
| Acción 3a      | Scroll down para ver sección "Bebidas"                               |
| Acción 3b      | Tap "+" (primer add) → barra inferior aparece                        |
| Acción 3c      | Loop: tap "+" hasta que `lbl_minimoCompletado` sea visible           |
| Botón "+"      | Primer tap: `content-desc="add"` · Post-primer: coords (413,1810) en device |
| Validación     | `lbl_minimoCompletado` visible + total > $7.000 en barra inferior    |
| Estado post    | Barra inferior: "1 producto · $7.X00 — Ir a canasta"                |
| Wait Strategy  | POST-LOOP: `SmartWaitPage.waitVisible(lbl_minimoCompletado, SmartWaitPage.SHORT)` · Entre taps: `SmartWaitPage.tapPause()` |
| Riesgo         | DEV $220/unidad → ≥ 32 taps; botón "+" post-primer es Compose NAF   |

---

### Paso 4 — Tap "Ir a canasta" → Vista canasta
*(COPIADO de QA-20260409 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Mínimo de compra completado                                          |
| Acción         | Tap `content-desc="Ir a canasta"` bounds=[666,2035][1024,2170]       |
| Validación     | Vista canasta: producto listado, subtotal visible, banner "¡Has completado el mínimo!" |
| Estado post    | Canasta / Nitro Cart con "Ir a pagar" visible                        |
| Wait Strategy  | `SmartWaitPage.waitVisible(lbl_cartProductName, SmartWaitPage.SHORT)` |

---

### Paso 5 — Tap "Ir a pagar" → Pantalla "Programa tu pedido" (NUEVO)
*(NUEVO — explorado en este RunId)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Vista canasta con "Ir a pagar" visible                               |
| Acción         | Tap `content-desc="Ir a pagar"` bounds=[648,2013][1024,2148]         |
| Resultado      | Navega a pantalla FULL SCREEN "Programa tu pedido" (NO al checkout directamente) |
| Validación     | Texto "Programa tu pedido" visible. Pill de fecha actual seleccionada (color dark). Al menos 2 franjas horarias visibles. |
| Estado post    | Pantalla "Programa tu pedido" con fecha actual seleccionada          |
| Wait Strategy  | `SmartWaitPage.waitVisible(lbl_programaTuPedidoTitle, SmartWaitPage.MEDIUM)` |
| ⚠️ CAMBIO DE FLUJO | En el plan QA-20260409, "Ir a pagar" iba directo al checkout. Ahora va a la pantalla de scheduling PRIMERO. |

---

### Paso 6 — Seleccionar fecha futura en "Programa tu pedido" (NUEVO)
*(NUEVO — explorado en este RunId)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Pantalla "Programa tu pedido" visible. Fecha actual (lun/hoy) seleccionada por defecto. |
| Acción         | Tap en pill de fecha FUTURA (segunda opción, e.g. "jue abr 16")      |
| Validación     | Pill futura seleccionada (fondo oscuro/black). Lista de franjas horarias se EXPANDE (12+ slots vs 2 del día actual). |
| Comportamiento | Día actual disponible: solo 2-3 franjas (slots casi agotados). Día futuro: 12+ franjas disponibles todo el día (8am–8pm). |
| Estado post    | Fecha futura seleccionada. Lista de tiempo slots completa visible.   |
| Coordenadas    | Pill "jue abr 16" validado en dispositivo: **device (470, 745)**     |
| Wait Strategy  | Post-tap: `SmartWaitPage.waitVisible(lbl_timeSlot_first, SmartWaitPage.SHORT)` |
| ⚠️ WAIT_UNKNOWN | El elemento pill de fecha no tiene resource-id conocido (Compose). Usar coordenadas o text match. |

---

### Paso 7 — Seleccionar franja horaria → "Continuar" habilitado (NUEVO)
*(NUEVO — explorado en este RunId)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Fecha futura seleccionada, slots horarios visibles                   |
| Acción         | Tap en primer slot disponible (e.g., "8:00 am - 9:00 am")           |
| Validación     | Fila seleccionada queda con borde/highlight visible. Botón "Continuar" (verde) APARECE en la parte inferior de la pantalla. |
| Estado post    | Franja horaria seleccionada. "Continuar" verde visible y habilitado. |
| Coordenadas    | Slot "8:00 am - 9:00 am" validado en dispositivo: **device (551, 961)** (varía según scroll) |
| Wait Strategy  | Post-tap: `SmartWaitPage.waitVisible(btn_continuarScheduling, SmartWaitPage.SHORT)` |
| Riesgo         | Slots son Compose — sin resource-id; text matching ("8:00 am") como locator primario |
| Criterio ✅    | El botón "Continuar" SOLO aparece cuando fecha + slot están seleccionados |

---

### Paso 8 — Tap "Continuar" → (Modal PRO) → Checkout con fecha programada (NUEVO + reutilizado)
*(NUEVO tap + bifurcación PRO ya conocida)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Slot horario seleccionado, botón "Continuar" visible                 |
| Acción 8a      | Tap `content-desc="Continuar"` O coords device **(540, 2140)**       |
| Bifurcación    | Modal PRO puede aparecer → cerrar con `resource-id="com.grability.rappi:id/growth_prime_imageView_close"` |
| Validación 8b  | Pantalla "Terminar y pagar" (Checkout) visible                       |
| Validación NUEVA | Elemento de fecha programada visible en checkout: texto con formato "DíaNombre DD de mes, HH:MM - HH:MM AM" (e.g., "Lunes 13 de abril, 08:00 - 09:00 AM") |
| Estado post    | Checkout con fecha/hora programada visible                           |
| Wait Strategy  | Pre-tap: `SmartWaitPage.waitVisible(btn_continuarScheduling, SmartWaitPage.SHORT)` · Post Modal: `SmartWaitPage.waitVisible(lbl_scheduledTime, SmartWaitPage.MEDIUM)` |
| Riesgo         | Modal PRO SIEMPRE debe manejarse con try/catch antes de validar checkout |

---

### Paso 9 — Verificar método de pago Efectivo en Checkout
*(COPIADO de QA-20260409 paso 5 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Checkout "Terminar y pagar" visible (sin Modal PRO)                  |
| Acción         | Verificar que `text="Efectivo"` visible en sección "Método de pago"  |
| Si no está     | Tap en `text="Cambiar"` para cambiar a Efectivo                      |
| Validación     | `text="Efectivo"` visible en bounds=[204,1748][362,1883]             |
| Estado post    | Efectivo seleccionado. El total a pagar incluye: subtotal ($7.700+) + envío ($4.700) |
| Wait Strategy  | `SmartWaitPage.waitVisible(lbl_efectivo, SmartWaitPage.SHORT)`       |

---

### Paso 10 — Tap "Continuar" en Checkout → Modal Efectivo
*(COPIADO de QA-20260409 paso 6 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Checkout con Efectivo seleccionado                                   |
| Acción         | Tap `content-desc="Continuar"` bounds=[540,2013][1024,2148]          |
| Validación     | Bottom sheet: `resource-id="com.grability.rappi:id/checkout_cash_modal_view_container"` visible |
| Estado post    | Popup "Por favor especifica el monto de tu pago" visible             |
| Wait Strategy  | `SmartWaitPage.waitVisible(container_cashModal, SmartWaitPage.MEDIUM)` |

---

### Paso 11 — Seleccionar "No necesitaré cambio" → Tap "Hacer pedido"
*(COPIADO de QA-20260409 paso 7 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Modal Efectivo visible                                               |
| Acción 11a     | Tap RadioButton "No necesitaré cambio" bounds=[29,1332][164,1467] center (96,1399) |
| Validación 11a | RadioButton checked=true. CTA cambia a `content-desc="Hacer pedido"` |
| Acción 11b     | Tap `content-desc="Hacer pedido"` bounds=[135,1991][945,2149]        |
| Validación 11b | Navega a pantalla propina del Rappitendero                           |
| Estado post    | Pantalla "¡Reconoce su esfuerzo!" visible                            |
| Wait Strategy  | Post 11a: `SmartWaitPage.tapPause()` · Post 11b: `SmartWaitPage.waitVisible(lbl_reconoceEsfuerzo, SmartWaitPage.MEDIUM)` |

---

### Paso 12 — Tap "Hacer pedido" en propina → Pedido creado
*(COPIADO de QA-20260409 paso 8 — validado)*

| Atributo       | Valor                                                                |
|----------------|----------------------------------------------------------------------|
| Precondición   | Pantalla propina visible                                             |
| Acción         | Tap "Hacer pedido" (Compose NAF) bounds=[68,2002][1012,2160] coords (540,2081) |
| Validación     | `resource-id="com.grability.rappi:id/container_order_tracking_screen"` visible |
| Validación     | `text="Seleccionando productos"` visible                             |
| Estado post    | Order tracking con estado "Seleccionando productos"                  |
| Wait Strategy  | `SmartWaitPage.waitVisible(container_orderTracking, SmartWaitPage.LONG)` |
| Criterio ✅    | Pedido creado con entrega programada                                 |

---

## Modelo del flujo

```
[setUp] → openRappi (TC existente)
  → Home de Rappi cargado
  → handle: banner "Estás lejos dirección" (dismiss X)
  → Tap tarjeta Turbo (home_card_button, coords escaladas)
  → Home Turbo → verificar "Mínimo de compra $7,000"
  → Scroll hasta Bebidas → tap "+" Heineken × 36 (loop)
      → Validar: lbl_minimoCompletado visible, total > $7.000
  → Tap "Ir a canasta" (content-desc)
  → Vista canasta → validar producto + subtotal
  → Tap "Ir a pagar" (content-desc)
      ↓ [NUEVO — pantalla scheduling]
  → Pantalla "Programa tu pedido" FULL SCREEN
      → Tap pill fecha futura ("jue abr 16" o equivalente)
      → Lista de slots se expande (12+ slots)
      → Tap slot horario (e.g., "8:00 am - 9:00 am")
      → Botón "Continuar" (verde) aparece en footer
      → Tap "Continuar"
      ↓
  → (Bifurcación PRO: Modal aparece → cerrar growth_prime_imageView_close)
      ↓
  → Checkout "Terminar y pagar"
      → Validar texto fecha/hora programada visible (e.g., "Lunes 13 de abril, 08:00 - 09:00 AM")
      → Verificar Efectivo seleccionado
  → Tap "Continuar" (Checkout)
  → Popup "Por favor especifica el monto"
  → Tap radio "No necesitaré cambio" → CTA → "Hacer pedido"
  → Tap "Hacer pedido"
  → Vista propina "¡Reconoce su esfuerzo!"
  → Tap "Hacer pedido" (Compose coords 540,2081)
  → Esperar → container_order_tracking_screen
  → Validar: "Seleccionando productos" visible ✅
```

---

## Componentes UI capturados

> **Nota de coordenadas:** Dispositivo explorado = SM-S928B 1080×2340. Coordenadas en device pixels (resolución base).
> Las coordenadas de la pantalla "Programa tu pedido" son COORDENADAS VALIDADAS empiricamente mediante taps confirmados.

### Nuevos (Pantalla "Programa tu pedido")

| Paso | Pantalla              | class / type                   | text / resource-id                         | content-desc | bounds (1080×2340 estimado) | .rs sugerido                    | Locator preferido       | Locator respaldo                 |
|------|----------------------|--------------------------------|--------------------------------------------|--------------|-----------------------------|---------------------------------|-------------------------|----------------------------------|
| 5    | Programa tu pedido   | android.widget.TextView (Compose?) | text="Programa tu pedido"              | -            | ~[68,150][700,225]          | `lbl_programaTuPedidoTitle`     | text                    | -                                |
| 5    | Programa tu pedido   | android.view.View (Compose)    | -                                          | -            | ~[945,165][1060,245]        | `btn_closeProgramarPedido`      | coordenadas (981, 201)  | N/A (Compose sin acc.)          |
| 5    | Programa tu pedido   | android.widget.TextView (Compose?) | text="Cl. 93 #19-58, Bogotá, Colombia" | -            | ~[68,280][950,350]          | `lbl_schedulingAddress`         | text parcial            | -                                |
| 6    | Programa tu pedido   | android.view.View (Compose)    | - (pill fecha actual, e.g. "lun abr 13") | -            | ~[68,650][182,750]          | `pill_fechaActual`              | text (día+fecha)        | coordenadas (192, 745)          |
| 6    | Programa tu pedido   | android.view.View (Compose)    | - (pill fecha futura, e.g. "jue abr 16") | -            | ~[182,650][330,750]         | `pill_fechaFutura`              | text (día+fecha)        | **coordenadas validadas: (470, 745)** |
| 7    | Programa tu pedido   | android.view.View (Compose)    | text="8:00 am - 9:00 am"                  | -            | ~[68,870][1012,950]         | `row_timeSlot`                  | text (hora)             | **coordenadas validadas: (551, 961)** |
| 7    | Programa tu pedido   | android.view.View (Compose)    | text (precio envío) "4.700"               | -            | ~[850,870][1012,950]        | `lbl_slotPrice`                 | text                    | -                                |
| 8    | Programa tu pedido   | android.view.View (Compose)    | -                                          | "Continuar" (presumible) | ~[68,2080][1012,2190]  | `btn_continuarScheduling`       | content-desc="Continuar" | **coordenadas validadas: (540, 2140)** |

### Nuevo elemento en Checkout

| Paso | Pantalla    | class / type                   | text / resource-id                                       | content-desc | bounds (1080×2340 estimado) | .rs sugerido      | Locator preferido | Locator respaldo |
|------|-------------|--------------------------------|----------------------------------------------------------|--------------|-----------------------------|-------------------|-------------------|------------------|
| 8+   | Checkout    | android.widget.TextView        | text format: "DíaNombre DD de mes, HH:MM - HH:MM AM"    | -            | ~[68,1400][950,1460]        | `lbl_scheduledTime` | text parcial regex | -              |

### Componentes reutilizados de QA-20260409 (todos validados)

| .rs sugerido                | resource-id / locator principal                                              | Pantalla          |
|-----------------------------|------------------------------------------------------------------------------|-------------------|
| `btn_iniciarRappi`          | `com.grability.rappi:id/button_start_app`                                    | QA Screen         |
| `card_turbo`                | `resource-id="home_card_button"` + coords (787,1567)                         | Home              |
| `lbl_minimoCompra`          | text="Mínimo de compra $7,000"                                               | Turbo Home        |
| `btn_addProducto`           | `content-desc="add"`                                                         | Turbo Products    |
| `lbl_minimoCompletado`      | `com.grability.rappi:id/square_notification_text`                            | Turbo Products    |
| `btn_irACanasta`            | `content-desc="Ir a canasta"`                                                | Turbo Products    |
| `lbl_cartProductName`       | `basketui_text_view_product_name`                                            | Canasta           |
| `btn_irAPagar`              | `content-desc="Ir a pagar"`                                                  | Canasta           |
| `btn_closeProModal`         | `com.grability.rappi:id/growth_prime_imageView_close`                        | Modal PRO         |
| `lbl_efectivo`              | text="Efectivo"                                                              | Checkout          |
| `btn_continuar` (checkout)  | `content-desc="Continuar"`                                                   | Checkout          |
| `container_cashModal`       | `com.grability.rappi:id/checkout_cash_modal_view_container`                  | Modal Efectivo    |
| `radio_noNecesitoChange`    | class RadioButton, index 0                                                   | Modal Efectivo    |
| `btn_hacerPedidoCash`       | `content-desc="Hacer pedido"`                                                | Modal Efectivo    |
| `lbl_reconoceEsfuerzo`      | text="¡Reconoce su esfuerzo!"                                                | Propina           |
| `btn_hacerPedidoPropina`    | Compose NAF coords (540,2081)                                                | Propina           |
| `container_orderTracking`   | `com.grability.rappi:id/container_order_tracking_screen`                     | OrderTracking     |
| `lbl_orderStatus`           | text="Seleccionando productos"                                               | OrderTracking     |

---

## Componentes validados empíricamente (nueva pantalla "Programa tu pedido")

| .rs sugerido           | resource-id | content-desc | bounds validados (tap real) | base_x (1080) | base_y (2340) | tap_validated | estrategia_primaria | fallback |
|------------------------|-------------|--------------|------------------------------|---------------|---------------|---------------|---------------------|---------|
| `pill_fechaFutura`     | N/D         | N/D          | ~[182,650][330,750]         | 470           | 745           | ✅            | text (día+fecha)    | coords (470,745) |
| `row_timeSlot_800_900` | N/D         | N/D          | ~[68,870][1012,950]         | 551           | 961           | ✅            | text="8:00 am"      | coords (551,961) |
| `btn_continuarScheduling` | N/D      | "Continuar"  | ~[68,2080][1012,2190]       | 540           | 2140          | ✅            | content-desc="Continuar" | coords (540,2140) |
| `btn_closeProgramarPedido` | N/D     | N/D          | ~[945,165][1060,245]        | 981           | 201           | ✅ (via PRO modal close coord) | coords (981,201) | N/A |

---

## Dumps capturados (BMO-Explorer — Capture Mode 2026-04-14)

| Pantalla            | Archivo dump                              | Notas                                          |
|---------------------|-------------------------------------------|------------------------------------------------|
| Programa tu pedido  | /tmp/uidump_programar.xml                 | Capturado con sáb abr 11 seleccionado, 8 slots visibles |
| Programa tu pedido  | /tmp/uidump_slot_selected.xml             | Post-tap slot 8:00am — btn_continuarScheduling visible |
| Checkout            | /tmp/uidump_checkout.xml                  | Con fecha programada "Domingo 12 de abril, 08:00 - 09:00 AM" |

## .rs creados (BMO-Explorer — 2026-04-14)

| .rs                          | Carpeta                                    | Locator usado                                                        | tap_validated |
|------------------------------|--------------------------------------------|----------------------------------------------------------------------|---------------|
| lbl_programaTuPedidoTitle    | android/ProgramarPedido/                   | text="Programa tu pedido"                                            | false (label) |
| btn_closeProgramarPedido     | android/ProgramarPedido/                   | market_slots_dialog//android.widget.ImageView                        | coords(978,200)|
| lbl_schedulingAddress        | android/ProgramarPedido/                   | contains(@text, "Cl. 93")                                            | false (label) |
| pill_fechaActual             | android/ProgramarPedido/                   | //android.view.View[.//TextView[@text="Hoy"]] · coords(980,734)      | true          |
| pill_fechaFutura             | android/ProgramarPedido/                   | //android.view.View[.//TextView[@text="abr 12"]] · coords(463,734)   | true          |
| row_timeSlot                 | android/ProgramarPedido/                   | //android.view.View[.//TextView[contains(@text,"8:00 am")]]          | true          |
| lbl_slotPrice                | android/ProgramarPedido/                   | text="$4.700" (primer match)                                         | false (label) |
| btn_continuarScheduling      | android/ProgramarPedido/                   | Compose NAF · coords(540,2081) — aparece solo post-slot-selection     | true          |
| lbl_scheduledTime            | android/Checkout/                          | contains(@text," de ") and contains(@text,"AM")                      | false (label) |



### Object Repository — NUEVOS

```
Object Repository/android/
├── ProgramarPedido/                      ← NUEVA carpeta
│   ├── lbl_programaTuPedidoTitle.rs      ← text: "Programa tu pedido"
│   ├── btn_closeProgramarPedido.rs       ← Compose NAF — coords (981,201)
│   ├── lbl_schedulingAddress.rs          ← text parcial: "Cl. 93"
│   ├── pill_fechaActual.rs               ← text: día+fecha actual (dinámico)
│   ├── pill_fechaFutura.rs               ← text: día+fecha futura (dinámico)
│   ├── row_timeSlot.rs                   ← text: "8:00 am" o similar
│   ├── lbl_slotPrice.rs                  ← text: "$4.700"
│   └── btn_continuarScheduling.rs        ← content-desc="Continuar" (en scheduling screen)
└── Checkout/
    └── lbl_scheduledTime.rs              ← text parcial: "de abril" o regex del tiempo
```

> **Nota:** Los `.rs` de fecha (pill_fechaActual, pill_fechaFutura) son dinámicos por fecha. Usar locator dinámico: se inyecta desde `GlobalVariable` o parámetro del test.

### Keywords — NUEVOS

```
Keywords/com/rappi/page/android/
└── TurboSchedulingPage.groovy     ← NUEVA - toda la interacción con "Programa tu pedido"
                                      Métodos: waitForScreen(), selectFutureDate(String dateText),
                                      selectTimeSlot(String slotText), tapContinuar()
```

> **Actualizar:** `TurboCheckoutPage.groovy` — agregar método `verifyScheduledTimeVisible(String expectedText)`

### Keywords — Capa Steps (actualizar)

```
Keywords/com/rappi/steps/android/
└── TurboSteps.groovy   ← agregar @Keyword: scheduleAndContinue(String dateText, String slotText)
```

### Script y Test Case

```
Scripts/android/TC_TurboCompraConFechaProgramada/
└── Script<timestamp>.groovy   ← Orquestador

Test Cases/android/
└── TC_TurboCompraConFechaProgramada.tc
```

---

## Riesgos y mitigaciones

| # | Riesgo                                                                          | Mitigación                                                                           |
|---|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| 1 | **Fechas en "Programa tu pedido" son dinámicas** — cambian cada día             | Usar locator por texto dinámico; NO hardcodear fecha. Inyectar `dateText` desde GlobalVariable o parámetro. |
| 2 | **"Continuar" en scheduling NO visible** sin tiempo slot seleccionado          | Siempre tap slot ANTES de buscar btn_continuarScheduling. Usar `waitForElementPresent` con timeout SHORT. |
| 3 | **Día actual solo tiene 2 slots** (casi agotados en DEV) — podría no tener slots | Usar SIEMPRE el segundo día disponible (fecha futura) para máxima disponibilidad     |
| 4 | **Pills de fecha son Compose NAF** — sin resource-id estable                   | Locator primario: `text` del label. Fallback: coordenadas escaladas via `DeviceResolutionPage` |
| 5 | **Time slots son Compose NAF** — sin resource-id                               | Locator primario: `text` matching hora ("8:00 am"). Fallback: coordenadas escaladas  |
| 6 | **Modal PRO** entre scheduling y checkout                                       | Siempre try/catch `growth_prime_imageView_close` antes de validar checkout           |
| 7 | **Scroll en lista de time slots** — slots de tarde pueden requerir scroll       | Usar slots de la madrugada/mañana (8am-9am) que están al inicio de la lista — sin scroll |
| 8 | **lbl_scheduledTime en Checkout** — texto incluye fecha dinámica               | Usar `waitForElementPresent` con regex parcial o text contains "de abril" · En inglés no aplica |
| 9 | **DEV: Turbo disponibilidad** — posible no disponible en ciertos horarios       | Precondición: verificar que tienda Turbo está activa antes de ejecutar TC            |
| 10| **Banner "Estás lejos de la dirección"** en checkout                           | Visible en screenshot explorado (texto naranja) — no bloqueante para el flujo       |

---

## Cobertura mínima recomendada

| Escenario                                        | Prioridad | Criterio de éxito                                                   |
|--------------------------------------------------|-----------|---------------------------------------------------------------------|
| Happy path — fecha futura + slot + checkout      | P0 — MUST | Pedido creado, tracking "Seleccionando productos" visible           |
| Validación: "Continuar" bloqueado sin slot seleccionado | P1 — SHOULD | Botón "Continuar" NO visible cuando solo hay fecha seleccionada (sin slot) |
| Fecha programada visible en Checkout             | P0 — MUST | Campo con fecha/hora visible en pantalla "Terminar y pagar"         |
| Modal PRO manejado correctamente                 | P1 — SHOULD | Modal cierra y llega a checkout sin fallar                          |
| Mínimo $7.000 completado antes de scheduling     | P0 — MUST | Banner "¡Has completado el mínimo de compra!" visible               |

---

## Criterios de aceptación

| Criterio                                                         | Paso(s)   | Elemento verificado                                           |
|------------------------------------------------------------------|-----------|---------------------------------------------------------------|
| Pantalla "Programa tu pedido" aparece al tap "Ir a pagar"        | Paso 5    | `lbl_programaTuPedidoTitle` visible                           |
| Fecha futura muestra más slots que fecha actual                  | Paso 6    | ≥2 slots para fecha actual, ≥12 slots para fecha futura       |
| "Continuar" aparece solo tras seleccionar slot                   | Paso 7    | `btn_continuarScheduling` visible únicamente con slot activo  |
| Checkout muestra fecha/hora programada                           | Paso 8+   | `lbl_scheduledTime` con texto del día y franjas horarias      |
| Pedido se crea con entrega programada                            | Paso 12   | `container_order_tracking_screen` + "Seleccionando productos" |

---

## Smart Wait Annotations — Resumen por paso

| Paso | Elemento esperado                  | Constante       | Rationale                                        |
|------|------------------------------------|-----------------|--------------------------------------------------|
| 1    | home_card_button                   | MEDIUM (15s)    | App boot + auth + home load                      |
| 2    | lbl_minimoCompra (Turbo Home)      | MEDIUM (15s)    | Network call para cargar tienda                  |
| 3    | lbl_minimoCompletado               | SHORT (5s)      | Banner aparece local tras acumular total          |
| 4    | lbl_cartProductName                | SHORT (5s)      | Canasta ya cargada en cache                      |
| 5    | lbl_programaTuPedidoTitle          | MEDIUM (15s)    | Nueva pantalla scheduling — puede requerir network |
| 6    | lbl_timeSlot_first                 | SHORT (5s)      | Slots se renderizan localmente tras tap de fecha  |
| 7    | btn_continuarScheduling            | SHORT (5s)      | Botón aparece local tras seleccionar slot         |
| 8    | lbl_scheduledTime (Checkout)       | MEDIUM (15s)    | Checkout requiere network call                   |
| 10   | container_cashModal                | MEDIUM (15s)    | Modal Efectivo desde backend                     |
| 11   | lbl_reconoceEsfuerzo               | MEDIUM (15s)    | Pantalla propina navegación                      |
| 12   | container_orderTracking            | LONG (30s)      | Creación de pedido en backend                    |

---

## Compatibilidad multi-dispositivo

| Paso | Elemento                          | Motivo coordenadas                                               | Base         | Escalado via           |
|------|-----------------------------------|------------------------------------------------------------------|--------------|------------------------|
| 1    | Cerrar banner ubicación           | Compose sin accessibility node                                   | 1080×2340    | `DeviceResolutionPage` |
| 2    | Tap tarjeta Turbo                 | `home_card_button` Compose no expuesto                           | 1080×2340    | `DeviceResolutionPage` |
| 3    | Botón "+" post-primer-add         | Compose NAF counter                                              | 1080×2340    | `DeviceResolutionPage` |
| 5    | Cerrar scheduling screen          | Compose sin resource-id                                          | 1080×2340    | `DeviceResolutionPage` |
| 6    | Pill fecha futura                 | Compose — usar text primero; coords como fallback                | 1080×2340    | `DeviceResolutionPage` |
| 7    | Time slot rows                    | Compose — usar text primero; coords como fallback                | 1080×2340    | `DeviceResolutionPage` |
| 8    | Botón "Continuar" scheduling      | Compose — intentar content-desc="Continuar"; coords como fallback| 1080×2340    | `DeviceResolutionPage` |
| 12   | "Hacer pedido" propina            | Compose NAF sin accessibility                                    | 1080×2340    | `DeviceResolutionPage` |

**Resolución base:** 1080×2340 (SM-S928B) — es la resolución base de `DeviceResolutionPage`.

---

## CustomKeywords y setUp a reutilizar

| Keyword / TC existente            | Ruta                                                           | Uso en este flujo                          |
|-----------------------------------|----------------------------------------------------------------|--------------------------------------------|
| `openRappi` (TC)                  | `Test Cases/android/openRappi.tc`                              | setUp                                      |
| `TurboStorePage` (si ya creado)   | `Keywords/com/rappi/page/android/TurboStorePage.groovy`        | Navegación + addProductsUntilMinimum       |
| `TurboCartPage` (si ya creado)    | `Keywords/com/rappi/page/android/TurboCartPage.groovy`         | Canasta + btn irAPagar                     |
| `TurboCheckoutPage` (si ya creado)| `Keywords/com/rappi/page/android/TurboCheckoutPage.groovy`     | Verificar Efectivo + Continuar + PRO modal + NUEVO: verifyScheduledTime |
| `TurboCashModalPage` (si ya creado)| `Keywords/com/rappi/page/android/TurboCashModalPage.groovy`   | Radio + Hacer pedido                       |
| `TurboTipPage` (si ya creado)     | `Keywords/com/rappi/page/android/TurboTipPage.groovy`          | Propina + Hacer pedido final               |
| `TurboOrderTrackingPage` (si ya creado)| `Keywords/com/rappi/page/android/TurboOrderTrackingPage.groovy` | Validar tracking                     |
| `UtilsPage`                       | `Keywords/com/rappi/page/common/UtilsPage.groovy`              | Scroll + validaciones                      |
| `DeviceResolutionPage`            | `Keywords/com/rappi/page/common/DeviceResolutionPage.groovy`   | Escalar coordenadas Compose elements       |

---

## Instrucciones para BMO-TestCreator

### setUp a usar
```groovy
WebUI.callTestCase(findTestCase('Test Cases/android/openRappi'), [:], FailureHandling.STOP_ON_FAILURE)
```

### NUEVO Page class a crear (prioridad máxima)
```
TurboSchedulingPage.groovy
Ubicación: Keywords/com/rappi/page/android/

Métodos requeridos:
  - waitForScreen()                        → waitVisible(lbl_programaTuPedidoTitle, MEDIUM)
  - selectFutureDate(String dayText)       → tap text=dayText en el pill de fecha; fallback coords DeviceResolutionPage
  - selectTimeSlot(String slotText)        → tap text=slotText en la lista; fallback coords DeviceResolutionPage
  - waitForContinuarButton()               → waitVisible(btn_continuarScheduling, SHORT)
  - tapContinuar()                         → tap content-desc="Continuar" / fallback: tapAtPosition(DeviceResolutionPage.scaleX(540), DeviceResolutionPage.scaleY(2140))
  - closeScreen()                          → tapAtPosition(DeviceResolutionPage.scaleX(981), DeviceResolutionPage.scaleY(201))
```

### ACTUALIZAR CheckoutPage (si ya existe)
```
TurboCheckoutPage.groovy
Agregar método:
  - verifyScheduledTimeVisible()           → waitVisible(lbl_scheduledTime, SHORT; locator: text contains "de abril" o regex)
```

### NUEVO @Keyword en TurboSteps
```groovy
@Keyword
void scheduleAndContinue(String dateText = 'jue', String slotText = '8:00 am') {
    TurboSchedulingPage.waitForScreen()
    TurboSchedulingPage.selectFutureDate(dateText)
    TurboSchedulingPage.selectTimeSlot(slotText)
    TurboSchedulingPage.waitForContinuarButton()
    TurboSchedulingPage.tapContinuar()
}
```

### Notas especiales para TestCreator
- `TurboSchedulingPage.selectFutureDate()`: no hardcodear "jue abr 16". Usar la SEGUNDA pill visible (índice 1) como "fecha futura". Si el texto exacto cambia cada semana, usar `Mobile.findElements(By.XPATH, "//pill[@index='1']")` o capturar por posición.
- `selectTimeSlot()`: el primer slot "8:00 am - 9:00 am" es el más consistente (siempre aparece primero). Usar `text contains "8:00 am"` como locator primario.
- `btn_continuarScheduling`: Puede compartir `content-desc="Continuar"` con el botón de Checkout. Distinguir por pantalla (verificar lbl_programaTuPedidoTitle visible primero).
- La pantalla de scheduling es FULL SCREEN (no bottom sheet) — el back presses/swipe down devuelve a Canasta.

---

## Instrucciones para BMO-Explorer

- **Validar empíricamente:**
  1. Confirmar que `text="Programa tu pedido"` es el locator correcto del título (o si hay resource-id)
  2. Capturar UIAutomator dump de la pantalla scheduling para confirmar class, resource-id y bounds exactos del pill de fecha futura y de los time slots
  3. Confirmar que `content-desc="Continuar"` aplica para el btn de scheduling (vs checkout Continuar)
  4. Verificar class del `lbl_scheduledTime` en Checkout — y si tiene resource-id propio
  5. Validar que tap en pill `(470, 745)` es estable o si varía por dispositivo

- **Preguntas abiertas (marcar como resueltas tras validación):**
  - ⚠️ ¿El pill de fecha futura tiene resource-id explayable en `adb shell uiautomator dump`?
  - ⚠️ ¿`btn_continuarScheduling` tiene `content-desc="Continuar"` en UIAutomator dump?
  - ⚠️ ¿El texto de fecha en Checkout tiene resource-id o solo es `text`?
  - ⚠️ ¿Hay más de 2 fechas disponibles en algunos días (3+ pills)?
