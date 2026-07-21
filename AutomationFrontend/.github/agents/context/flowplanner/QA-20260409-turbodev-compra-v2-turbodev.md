# QA-20260409-turbodev-compra-v2-turbodev

## Metadatos del plan

| Campo          | Valor                              |
|----------------|------------------------------------|
| PlanStatus     | Approved                           |
| ApprovedBy     | BMO-Explorer                       |
| ApprovalDate   | 2026-04-09                         |
| ApprovalNotes  | Flujo V2 completo validado en dispositivo SM-S928B (R5CY111XY3E) Android 16. Todos los pasos ejecutables. Hallazgos clave: (1) Popup "Por favor especifica el monto de tu pago" aparece correctamente tras tap Continuar en checkout con Efectivo; (2) Las 3 opciones de radio son interactuables (RadioButton expuesto en UIAutomator); (3) Al seleccionar "No necesitaré cambio" el botón CTA cambia de "Ingresar valor" a "Hacer pedido" (ambos con content-desc estable); (4) Tras tap "Hacer pedido" en popup → navega a Propina del Rappitendero; (5) Tras seleccionar propina y tap "Hacer pedido" en propina → "Estamos creando tu pedido" confirmado; (6) Contenedor del popup tiene resource-id com.grability.rappi:id/checkout_cash_modal_view_container — locator estable. |
| RejectionNotes |                                    |
| Versión        | V2 (basado en V1 QA-20260409-turbodev-compra-turbodev) |
| Fecha          | 2026-04-09                         |
| Plataforma     | android                            |
| Dispositivo    | SM-S928B (R5CY111XY3E) Android 16  |
| Resolución     | 1080x2340 px                       |
| Agente autor   | BMO-Explorer                       |

---

## Objetivo del caso

Validar el flujo completo de compra en una tienda **TurboDev** (V2) incluyendo el **popup de pago en efectivo** que aparece entre checkout y propina. Flujo: Home → TurboDev store → Agregar productos → Canasta → Checkout → **Popup Pago Efectivo** → Propina → Hacer Pedido → Confirmación.

---

## Diferencias V2 vs V1

| Aspecto | V1 | V2 |
|---------|----|----|
| Paso entre Checkout y Propina | Directo (Continuar → Propina) | Popup "Por favor especifica el monto de tu pago" intermedio |
| Objetos nuevos | — | 9 .rs en Object Repository/android/PagoEfectivo/ |
| Pasos funcionales | 8 | 10 (pasos 7 y 8 son nuevos) |

---

## Punto de entrada (setUp)

```
openRappi
```

La app debe lanzarse desde estado cerrado o desde home de Rappi.

---

## Precondiciones

1. Dispositivo Android conectado con app Rappi instalada (com.grability.rappi).
2. Usuario con sesión iniciada.
3. Dirección de entrega configurada (Cl. 93 #19-58, Bogotá, Colombia).
4. Método de pago: **Efectivo**.
5. Carrito vacío al inicio (o se vacía antes del setUp).
6. Conexión a internet activa.
7. Tienda **Nitro.** disponible en la zona de cobertura.

---

## Datos de prueba

| Campo              | Valor                                      |
|--------------------|--------------------------------------------|
| Dirección entrega  | Cl. 93 #19-58, Bogotá, Colombia            |
| Tienda             | Nitro. (TurboDev)                          |
| Cantidad productos | 33 Productos en carrito                    |
| Método de pago     | Efectivo                                   |
| Opción pago cash   | "No necesitaré cambio"                     |
| Propina elegida    | "Me salvas el día" — 18% / $1.350          |
| Total a pagar      | ~$15.860 (variable por precios dinámicos)  |
| Tiempo estimado    | 15 - 17 minutos con Turbo                  |

---

## Pasos funcionales validados en dispositivo

### PASO 1 — Abrir la app Rappi
- **Acción:** Lanzar app com.grability.rappi desde estado inicial.
- **Resultado esperado:** Pantalla home de Rappi cargada con barra de búsqueda visible.
- **Estado:** ✅ Validado (heredado de V1).

### PASO 2 — Navegar a tienda TurboDev (Nitro.)
- **Acción:** Desde el home, localizar y tap en la tienda Nitro. (TurboDev).
- **Resultado esperado:** Pantalla de tienda Nitro. abierta con productos visibles.
- **Estado:** ✅ Validado (heredado de V1).

### PASO 3 — Agregar productos al carrito
- **Acción:** Seleccionar y agregar productos a la canasta.
- **Resultado esperado:** Carrito actualizado con los productos seleccionados (33 productos).
- **Estado:** ✅ Validado (heredado de V1).

### PASO 4 — Acceder al carrito
- **Acción:** Tap en el ícono/botón de carrito o "Ver pedido".
- **Resultado esperado:** Pantalla de resumen del carrito visible con productos listados.
- **Estado:** ✅ Validado (heredado de V1).

### PASO 5 — Iniciar checkout
- **Acción:** Tap en "Continuar" desde el carrito.
- **Resultado esperado:** Pantalla de checkout con dirección, detalles, tiempo, método de pago y total.
- **Estado:** ✅ Validado (heredado de V1).

### PASO 6 — Revisar y confirmar datos del checkout
- **Acción:** Verificar dirección, método de pago (Efectivo), tiempo estimado, total. Tap "Continuar".
- **Resultado esperado:** Tras tap "Continuar" → aparece popup/bottom sheet "Por favor, especifica el monto de tu pago".
- **Componentes usados:** Object Repository/android/Checkout/ (16 archivos existentes).
- **Estado:** ✅ Validado en dispositivo V2.

### PASO 7 — (NUEVO V2) Popup de Pago en Efectivo
- **Acción:** Aparece bottom sheet con título "Por favor, especifica el monto de tu pago". Tres opciones radio:
  - "No necesitaré cambio" — "Tengo el valor exacto a pagar"
  - "Necesitaré cambio" — "Indicaré el pago exacto para el cambio que recibiré" (default seleccionado)
  - "Aún no lo sé" — "Puede que mi Rappi no tenga el cambio necesario"
- **Resultado esperado:** Popup visible con contenedor `checkout_cash_modal_view_container`. Botón CTA depende de selección.
- **Componentes usados:** Object Repository/android/PagoEfectivo/ (9 archivos NUEVOS).
- **Estado:** ✅ Validado en dispositivo V2.

### PASO 8 — (NUEVO V2) Seleccionar "No necesitaré cambio" y tap "Hacer pedido"
- **Acción:** Tap en radio "No necesitaré cambio". El botón CTA cambia de "Ingresar valor" a "Hacer pedido". Tap en "Hacer pedido".
- **Resultado esperado:** Navegación a pantalla de Propina del Rappitendero.
- **Locators confirmados:**
  - RadioButton: `//android.widget.TextView[@text='No necesitaré cambio']/preceding-sibling::android.widget.RadioButton` — FUNCTIONAL, clickable=true
  - Botón: `//*[@content-desc='Hacer pedido']` — FUNCTIONAL, content-desc estable
- **Estado:** ✅ Validado en dispositivo V2.

### PASO 9 — Seleccionar propina al Rappitendero
- **Acción:** Seleccionar opción "Me salvas el día" (18% / $1.350).
- **Resultado esperado:** Bottom sheet de propina con opciones: Muchas gracias (9%/$700), Pa'l chesco (11%/$800), Me salvas el día (18%/$1.350), ¡Eres mi héroe! (27%/$2.000), Personalizar (Otro). Botón "Hacer pedido" visible.
- **Componentes usados:** Object Repository/android/PropinaTendero/ (13 archivos existentes).
- **Estado:** ✅ Validado en dispositivo V2.

### PASO 10 — Tap en "Hacer pedido" (propina) → Confirmación
- **Acción:** Tap en "Hacer pedido" en bottom sheet de propina.
- **Coordenadas:** x=540, y=2080 (Compose UI, mismo comportamiento que V1).
- **Resultado esperado:** Pantalla "Estamos creando tu pedido" con Nitro., 33 Productos, dirección, tiempo Turbo, Efectivo.
- **Resultado observado:** ✅ Pantalla "Estamos creando tu pedido" apareció correctamente.
- **Estado:** ✅ Validado en dispositivo V2.

---

## Componentes exploratorios capturados — Popup Pago Efectivo (NUEVO V2)

### Dump UIAutomator del popup (estado inicial — "Necesitaré cambio" seleccionado)

| class | text | resource-id | content-desc | bounds | clickable | checked |
|-------|------|-------------|-------------|--------|-----------|---------|
| ComposeView | — | com.grability.rappi:id/checkout_cash_modal_view_container | — | [0,806][1080,2205] | false | — |
| TextView | Por favor, especifica el monto de tu pago | — | — | [68,874][855,1059] | false | — |
| TextView | Así tu Rappi podrá tener el cambio exacto para ti | — | — | [68,1070][1012,1186] | false | — |
| RadioButton | — | — | — | [29,1332][164,1467] | true | false |
| TextView | No necesitaré cambio | — | — | [163,1348][1052,1399] | false | — |
| TextView | Tengo el valor exacto a pagar | — | — | [163,1410][1052,1446] | false | — |
| RadioButton | — | — | — | [29,1558][164,1693] | false | true |
| TextView | Necesitaré cambio | — | — | [163,1574][1052,1625] | false | — |
| TextView | Indicaré el pago exacto para el cambio que recibiré | — | — | [163,1636][1052,1672] | false | — |
| RadioButton | — | — | — | [29,1784][164,1919] | true | false |
| TextView | Aún no lo sé | — | — | [163,1800][1052,1851] | false | — |
| TextView | Puede que mi Rappi no tenga el cambio necesario | — | — | [163,1862][1052,1898] | false | — |
| View | — | — | Ingresar valor | [135,1991][945,2149] | false | — |
| Button | — | — | — | [135,1991][945,2149] | false | — |

### Dump UIAutomator del popup (estado "No necesitaré cambio" seleccionado)

| class | text | resource-id | content-desc | bounds | clickable | checked |
|-------|------|-------------|-------------|--------|-----------|---------|
| RadioButton | — | — | — | [29,1332][164,1467] | false | true |
| View | — | — | Hacer pedido | [135,1991][945,2149] | false | — |

(Resto de elementos idénticos al estado inicial)

---

## dumps_capturados

- popup_initial: /tmp/v2_popup_pago.xml
- popup_hacer_pedido: /tmp/v2_popup_hacer_pedido.xml
- propina: /tmp/v2_propina.xml

## Screenshots capturados

- v2_popup_pago_initial.png — Popup con "Necesitaré cambio" seleccionado, botón "Ingresar valor"
- v2_popup_no_cambio_hacer_pedido.png — Popup con "No necesitaré cambio" seleccionado, botón "Hacer pedido"
- v2_propina_after_popup.png — Pantalla propina tras salir del popup
- v2_estamos_creando_pedido.png — Confirmación "Estamos creando tu pedido"

---

## Archivos .rs NUEVOS creados (V2) — Object Repository/android/PagoEfectivo/

| Archivo .rs | Nombre | Locator tipo | Locator principal |
|-------------|--------|-------------|-------------------|
| ctr_cashModalContainer.rs | ctr_cashModalContainer | resource-id | com.grability.rappi:id/checkout_cash_modal_view_container |
| lbl_cashModalTitle.rs | lbl_cashModalTitle | text | "Por favor, especifica el monto de tu pago" |
| lbl_cashModalSubtitle.rs | lbl_cashModalSubtitle | text | "Así tu Rappi podrá tener el cambio exacto para ti" |
| rdo_noNecesitareCambio.rs | rdo_noNecesitareCambio | XPath contextual | RadioButton preceding-sibling de text "No necesitaré cambio" |
| rdo_necesitareCambio.rs | rdo_necesitareCambio | XPath contextual | RadioButton preceding-sibling de text "Necesitaré cambio" |
| rdo_aunNoLoSe.rs | rdo_aunNoLoSe | XPath contextual | RadioButton preceding-sibling de text "Aún no lo sé" |
| btn_hacerPedidoCash.rs | btn_hacerPedidoCash | content-desc | "Hacer pedido" |
| btn_ingresarValor.rs | btn_ingresarValor | content-desc | "Ingresar valor" |
| lbl_noNecesitareCambioDesc.rs | lbl_noNecesitareCambioDesc | text | "Tengo el valor exacto a pagar" |

---

## Riesgos y mitigaciones (V2)

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|--------|-------|---------|------------|
| 1 | Botón "Hacer pedido" en propina es Compose puro (no en UIAutomator) | Alta | Alto | Tap por coordenadas (540, 2080). Heredado de V1. |
| 2 | RadioButtons del popup pueden cambiar orden o texto | Baja | Medio | Locator por XPath contextual (text del label adyacente). Estable. |
| 3 | content-desc del botón CTA cambia según opción seleccionada | Alta | Medio | Dos .rs separados: btn_hacerPedidoCash y btn_ingresarValor. Page debe usar el correcto. |
| 4 | Popup podría no aparecer si el método de pago no es Efectivo | Media | Alto | Precondición: método de pago = Efectivo obligatorio para V2. |
| 5 | Error "Ocurrió un problema" al crear pedido en ambiente de prueba | Media | Medio | Heredado de V1. Verificar ambiente con cuenta/dirección válida. |
| 6 | Variación de coordenadas en diferentes resoluciones (propina) | Media | Medio | Heredado de V1. Ajustar: x=(540/1080)*W, y=(2080/2340)*H. |

---

## Cobertura de objetos

### Objetos existentes (NO recreados)
- Object Repository/android/TurboDev/ — 2 archivos
- Object Repository/android/Checkout/ — 16 archivos
- Object Repository/android/Canasta/ — 3 archivos
- Object Repository/android/PropinaTendero/ — 13 archivos

### Objetos NUEVOS (creados por BMO-Explorer V2)
- Object Repository/android/PagoEfectivo/ — 9 archivos

### Total de objetos para flujo V2: 43
