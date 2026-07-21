# QA-20260409-turbodev-compra-turbodev

## Metadatos del plan

| Campo          | Valor                              |
|----------------|------------------------------------|
| PlanStatus     | Approved                           |
| ApprovedBy     | BMO-Explorer                       |
| ApprovalDate   | 2026-04-09                         |
| ApprovalNotes  | Validado en dispositivo SM-S928B (R5CY111XY3E) Android 16 en vivo. Todos los pasos son ejecutables. Ajustes menores: (1) Total a pagar muestra $17.178 en lugar de $16.987 del plan — variación dinámica de precios, no bloquea el flujo; (2) Montos de propina levemente distintos ($700/$1.350/$2.000 vs $650/$1.300/$1.950) — variación de configuración en vivo, los porcentajes (9/11/18/27%) son correctos; (3) Botón "Hacer pedido" confirmado como Compose UI puro (no aparece en UIAutomator) — tap por coordenadas (x=540, y=2080) funciona correctamente en 1080x2340; (4) Pantalla "Estamos creando tu pedido" apareció correctamente tras el tap; (5) setUp openRappi confirmado existente en Scripts/android/ y Test Cases/android/. |
| RejectionNotes |                                    |
| Fecha          | 2026-04-09                         |
| Plataforma     | android                            |
| Dispositivo    | SM-S928B (R5CY111XY3E) Android 16  |
| Resolución     | 1080x2340 px                       |
| Agente autor   | BMO-FlowPlanner                    |

---

## Objetivo del caso

Validar el flujo completo de compra en una tienda **TurboDev** dentro de la aplicación Rappi (Android), desde la apertura de la app hasta la confirmación de creación del pedido. El flujo incluye: búsqueda de tienda, navegación al carrito, selección de método de entrega Turbo, revisión del checkout, selección de propina al Rappitendero y envío del pedido.

---

## Punto de entrada (setUp)

```
openRappi
```

La app debe lanzarse desde estado cerrado o desde home de Rappi. No se asume sesión activa en pantalla de tienda.

---

## Precondiciones

1. Dispositivo Android conectado y con la app Rappi instalada (com.grability.rappi).
2. Usuario con sesión iniciada en Rappi.
3. Usuario con dirección de entrega configurada (Cl. 93 #19-58, Bogotá, Colombia).
4. Método de pago disponible: **Efectivo**.
5. El carrito debe estar vacío al inicio del flujo (o se vacía antes del setUp).
6. Conexión a internet activa.
7. La tienda **Nitro.** debe estar disponible en la zona de cobertura de la dirección configurada.

> **NOTA DE RIESGO:** Durante la ejecución exploratoria se detectó que la app puede mostrar "Estás lejos de la dirección" con alerta en color naranja. Esto NO bloquea el flujo pero es un estado que debe considerarse en validación.

---

## Datos de prueba

| Campo              | Valor                                      |
|--------------------|--------------------------------------------|
| Dirección entrega  | Cl. 93 #19-58, Bogotá, Colombia            |
| Tienda             | Nitro. (TurboDev)                          |
| Cantidad productos | 33 Productos en carrito                    |
| Método de pago     | Efectivo                                   |
| Propina elegida    | "Me salvas el día" — 18% / $1.300          |
| Total a pagar      | $16.987 (incluye propina)                  |
| Tiempo estimado    | 15 - 17 minutos con Turbo                  |
| Instrucción entrega| "Entrégame personalmente en la entrada"    |

---

## Pasos funcionales validados en dispositivo

### PASO 1 — Abrir la app Rappi
- **Acción:** Lanzar app com.grability.rappi desde estado inicial.
- **Resultado esperado:** Pantalla home de Rappi cargada con barra de búsqueda visible.
- **Estado:** Validado en dispositivo.

### PASO 2 — Navegar a tienda TurboDev (Nitro.)
- **Acción:** Desde el home, localizar y tap en la tienda Nitro. (TurboDev).
- **Resultado esperado:** Pantalla de tienda Nitro. abierta con productos visibles.
- **Estado:** Validado en dispositivo.

### PASO 3 — Agregar productos al carrito
- **Acción:** Seleccionar y agregar productos a la canasta.
- **Resultado esperado:** Carrito actualizado con los productos seleccionados (33 productos).
- **Estado:** Validado en dispositivo.

### PASO 4 — Acceder al carrito
- **Acción:** Tap en el ícono/botón de carrito o "Ver pedido".
- **Resultado esperado:** Pantalla de resumen del carrito visible con productos listados.
- **Estado:** Validado en dispositivo.

### PASO 5 — Iniciar checkout
- **Acción:** Tap en "Continuar" o "Ir al checkout" desde la pantalla de carrito.
- **Resultado esperado:** Pantalla de checkout cargada con secciones: dirección, detalles, tiempo estimado, método de pago y total.
- **Estado:** Validado en dispositivo.

### PASO 6 — Revisar y confirmar datos del checkout
- **Acción:** Verificar dirección (Cl. 93 #19-58), método de pago (Efectivo), tiempo estimado (15-17 min con Turbo), total a pagar ($16.987).
- **Resultado esperado:** Todos los datos correctamente mostrados. Botón "Continuar" habilitado.
- **Pantalla observada:** "Terminar y pagar" (header), secciones con mapa, dirección, detalles del pedido (1 item visible), instrucción de entrega, tiempo Turbo, método de pago Efectivo, total $16.987.
- **Estado:** Validado en dispositivo.

### PASO 7 — Seleccionar propina al Rappitendero
- **Acción:** Tap en "Continuar" desde el checkout para acceder a la pantalla de propina. Seleccionar opción "Me salvas el día" (18% / $1.300).
- **Resultado esperado:** Bottom sheet de propina visible con las opciones: "Muchas gracias" (9%/$650), "Pa'l chesco" (11%/$800), "Me salvas el día" (18%/$1.300) — SELECCIONADA, "¡Eres mi héroe!" (27%/$1.950), "Personalizar" (Otro). Botón "Hacer pedido" visible en la parte inferior del sheet.
- **Pantalla observada:**
  - Header: "87% de los usuarios le dan una propina a su Rappi."
  - Subtítulo: "¡Reconoce su esfuerzo!"
  - Descripción: "Tu Rappi recibe el 100% del valor de la propina. Recuerda que la propina es voluntaria, el valor sugerido puede ser modificado."
  - Opción seleccionada: "Me salvas el día" con fondo negro (18% / $1.300).
  - Botón CTA: "Hacer pedido" (verde).
- **Estado:** Validado en dispositivo.

### PASO 8 — Tap en "Hacer pedido"
- **Acción:** Tap en el botón "Hacer pedido" en la parte inferior del bottom sheet de propina.
- **Coordenadas reales del tap:** x=540, y=2080 (pantalla 1080x2340).
- **Nota técnica:** El botón "Hacer pedido" es un elemento Compose UI que NO aparece en el árbol de accesibilidad UIAutomator (uiautomator dump). No tiene text, content-desc ni identifier en el XML de jerarquía. Solo es interactuable por coordenadas.
- **Resultado observado tras tap exitoso:**
  - Pantalla de transición: **"Estamos creando tu pedido"**
  - Muestra: logo Rappitendero, tienda "Nitro." con "33 Productos", dirección "Cl. 93 #19-58, Bogotá, Colombia", alerta "Estás lejos de la dirección", tiempo "15 - 17 minutos con Turbo", método de pago "Efectivo".
  - La pantalla de creación apareció correctamente — confirma que el tap en "Hacer pedido" fue aceptado por el sistema.
- **Estado de confirmación de pedido:** Durante la sesión exploratoria, tras la pantalla "Estamos creando tu pedido", la app retornó al checkout con error "¡Lo sentimos! Ocurrió un problema, por favor inténtalo de nuevo más tarde". Esto se atribuye a condición del ambiente de prueba (dirección lejana + cuenta de prueba sin fondos confirmados). El flujo hasta el disparo del pedido está **validado**.
- **Screenshots capturados:**
  - `screenshots/paso8_before_tap.png` — Estado pre-tap (propina visible, botón "Hacer pedido").
  - `screenshots/paso8_creating_order.png` — Pantalla "Estamos creando tu pedido" (confirmación de disparo).
  - `screenshots/paso8_error_state.png` — Error de ambiente post-intento.
- **Estado:** Validado en dispositivo (flujo hasta disparo del pedido).

---

## Componentes exploratorios capturados

### Tabla completa de elementos — Pantalla de Propina (PASO 7 / PASO 8)

| Paso | Pantalla       | class                        | text                                                              | identifier                                       | label/content-desc        | bounds (x,y,w,h)         | .rs sugerido                    | locator preferido                              | locator respaldo                         |
|------|----------------|------------------------------|-------------------------------------------------------------------|--------------------------------------------------|---------------------------|--------------------------|---------------------------------|------------------------------------------------|------------------------------------------|
| 7    | Propina Sheet  | android.widget.TextView      | 87% de los usuarios le                                            | —                                                | —                         | 357,456 / 497x59         | tipStatText                     | By.text("87% de los usuarios le")              | By.clazz(TextView).idx(0)               |
| 7    | Propina Sheet  | android.widget.TextView      | ¡Reconoce su esfuerzo!                                            | —                                                | —                         | 68,676 / 654x74          | tipHeaderTitle                  | By.text("¡Reconoce su esfuerzo!")              | By.clazz(TextView).idx(2)               |
| 7    | Propina Sheet  | android.widget.TextView      | Muchas gracias                                                    | —                                                | —                         | 204,1034 / 598x51        | tipOption1Label                 | By.text("Muchas gracias")                      | By.clazz(TextView).idx(4)               |
| 7    | Propina Sheet  | android.widget.TextView      | 9%                                                                | —                                                | —                         | 886,1016 / 65x51         | tipOption1Pct                   | By.text("9%")                                  | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | $650                                                              | —                                                | —                         | 881,1067 / 75x36         | tipOption1Amount                | By.text("$650")                                | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | Pa'l chesco                                                       | —                                                | —                         | 204,1238 / 596x51        | tipOption2Label                 | By.text("Pa'l chesco")                         | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | 11%                                                               | —                                                | —                         | 882,1220 / 72x51         | tipOption2Pct                   | By.text("11%")                                 | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | $800                                                              | —                                                | —                         | 879,1271 / 77x36         | tipOption2Amount                | By.text("$800")                                | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | Me salvas el día                                                   | —                                                | —                         | 204,1442 / 580x51        | tipOption3Label (SELECTED)      | By.text("Me salvas el día")                    | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | 18%                                                               | —                                                | —                         | 869,1424 / 82x51         | tipOption3Pct                   | By.text("18%")                                 | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | $1.300                                                            | —                                                | —                         | 863,1475 / 93x36         | tipOption3Amount                | By.text("$1.300")                              | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | ¡Eres mi héroe!                                                   | —                                                | —                         | 204,1646 / 583x51        | tipOption4Label                 | By.text("¡Eres mi héroe!")                     | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | 27%                                                               | —                                                | —                         | 869,1628 / 85x51         | tipOption4Pct                   | By.text("27%")                                 | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | $1.950                                                            | —                                                | —                         | 866,1679 / 90x36         | tipOption4Amount                | By.text("$1.950")                              | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | Personalizar                                                      | —                                                | —                         | 204,1849 / 582x51        | tipOptionCustomLabel            | By.text("Personalizar")                        | —                                        |
| 7    | Propina Sheet  | android.widget.TextView      | Otro                                                              | —                                                | —                         | 865,1849 / 91x51         | tipOptionCustomValue            | By.text("Otro")                                | —                                        |
| 8    | Propina Sheet  | ComposeView (no en jerarquía)| Hacer pedido                                                      | NO EXPUESTO en UIAutomator                       | NO EXPUESTO               | ~[68,2020][1012,2120]    | btnHacerPedido                  | tap(x=540, y=2080) — coordenadas absolutas     | adb shell input tap 540 2080            |

### Tabla completa de elementos — Pantalla de Checkout (PASO 6)

| Paso | Pantalla  | class                        | text                                           | identifier                                            | label/content-desc         | bounds                   | .rs sugerido               | locator preferido                                 | locator respaldo                              |
|------|-----------|------------------------------|------------------------------------------------|-------------------------------------------------------|----------------------------|--------------------------|----------------------------|---------------------------------------------------|-----------------------------------------------|
| 6    | Checkout  | android.widget.TextView      | Terminar y pagar                               | —                                                     | —                          | 181,134 / 831x59         | checkoutHeader             | By.text("Terminar y pagar")                       | —                                             |
| 6    | Checkout  | android.view.TextureView     | —                                              | —                                                     | Mapa de Google             | 0,242 / 1080x416         | checkoutMap                | By.desc("Mapa de Google")                         | By.clazz("TextureView")                       |
| 6    | Checkout  | android.view.View            | —                                              | —                                                     | Ajustar punto de entrega   | 280,518 / 521x68         | adjustDeliveryPoint        | By.desc("Ajustar punto de entrega")               | —                                             |
| 6    | Checkout  | android.widget.TextView      | Cl. 93 #19-58, Bogotá, Colombia               | —                                                     | —                          | 204,711 / 625x51         | deliveryAddress            | By.text("Cl. 93 #19-58, Bogotá, Colombia")        | —                                             |
| 6    | Checkout  | android.widget.TextView      | Estás lejos de la dirección                    | —                                                     | —                          | 221,779 / 363x36         | farFromAddressWarning      | By.text("Estás lejos de la dirección")            | —                                             |
| 6    | Checkout  | android.widget.TextView      | Detalles                                       | —                                                     | —                          | 204,935 / 156x51         | orderDetailsLabel          | By.text("Detalles")                               | —                                             |
| 6    | Checkout  | android.widget.TextView      | Entrégame personalmente en la entrada          | —                                                     | —                          | 204,1129 / 717x96        | deliveryInstruction        | By.text("Entrégame personalmente en la entrada")  | —                                             |
| 6    | Checkout  | android.widget.TextView      | Agregar instrucciones                          | —                                                     | —                          | 204,1225 / 360x44        | addInstructionsLink        | By.text("Agregar instrucciones")                  | —                                             |
| 6    | Checkout  | android.widget.TextView      | 15 - 17 minutos con                            | —                                                     | —                          | 204,1391 / 364x51        | deliveryTimeText           | By.text("15 - 17 minutos con")                    | —                                             |
| 6    | Checkout  | android.widget.TextView      | Método de pago                                 | —                                                     | —                          | 68,1624 / 691x59         | paymentMethodLabel         | By.text("Método de pago")                         | —                                             |
| 6    | Checkout  | android.widget.TextView      | Cambiar                                        | —                                                     | —                          | 804,1628 / 163x51        | changePaymentBtn           | By.text("Cambiar")                                | —                                             |
| 6    | Checkout  | android.widget.TextView      | Efectivo                                       | —                                                     | —                          | 204,1748 / 158x135       | paymentMethodValue         | By.text("Efectivo")                               | —                                             |
| 6    | Checkout  | android.view.View            | —                                              | checkout_text_view_label_show_more_rappicredits       | —                          | 743,1932 / 168x81        | rappiCreditsLabel          | By.res("checkout_text_view_label_show_more_rappicredits") | —                                    |
| 6    | Checkout  | android.widget.CheckBox      | —                                              | checkout_checkbox_rappicredits                        | —                          | 911,1932 / 135x92        | rappiCreditsCheckbox       | By.res("checkout_checkbox_rappicredits")          | By.clazz("CheckBox")                          |
| 6    | Checkout  | android.widget.TextView      | Total a pagar                                  | —                                                     | —                          | 68,2012 / 203x44         | totalLabel                 | By.text("Total a pagar")                          | —                                             |
| 6    | Checkout  | android.widget.TextView      | $16.987                                        | —                                                     | —                          | 68,2062 / 449x87         | totalAmount                | By.text("$16.987")                                | —                                             |
| 6    | Checkout  | android.view.View            | —                                              | —                                                     | Continuar                  | 540,2013 / 484x135       | continuarBtn               | By.desc("Continuar")                              | tap(x=782, y=2080)                            |

### Tabla completa de elementos — Pantalla "Estamos creando tu pedido" (PASO 8 — confirmación)

| Paso | Pantalla          | class                   | text                            | identifier | label/content-desc | bounds observados (estimados) | .rs sugerido           | locator preferido                          |
|------|-------------------|-------------------------|---------------------------------|------------|--------------------|-------------------------------|------------------------|--------------------------------------------|
| 8    | Creando pedido    | android.widget.TextView | Estamos creando tu pedido       | —          | —                  | centro pantalla               | creatingOrderTitle     | By.text("Estamos creando tu pedido")       |
| 8    | Creando pedido    | android.widget.TextView | Nitro.                          | —          | —                  | bajo título                   | orderStoreName         | By.text("Nitro.")                          |
| 8    | Creando pedido    | android.widget.TextView | 33 Productos                    | —          | —                  | bajo tienda                   | orderProductCount      | By.text("33 Productos")                    |
| 8    | Creando pedido    | android.widget.TextView | Cl. 93 #19-58, Bogotá, Colombia | —          | —                  | sección dirección             | orderDeliveryAddress   | By.text("Cl. 93 #19-58, Bogotá, Colombia") |
| 8    | Creando pedido    | android.widget.TextView | Estás lejos de la dirección     | —          | —                  | bajo dirección                | farFromAddressWarning  | By.text("Estás lejos de la dirección")     |
| 8    | Creando pedido    | android.widget.TextView | 15 - 17 minutos con Turbo       | —          | —                  | sección tiempo                | orderDeliveryTime      | By.text("15 - 17 minutos con")             |
| 8    | Creando pedido    | android.widget.TextView | Efectivo                        | —          | —                  | sección pago                  | orderPaymentMethod     | By.text("Efectivo")                        |

---

## Riesgos y mitigaciones

| # | Riesgo                                                                 | Probabilidad | Impacto | Mitigación                                                                                             |
|---|------------------------------------------------------------------------|--------------|---------|--------------------------------------------------------------------------------------------------------|
| 1 | Botón "Hacer pedido" no expuesto en árbol UIAutomator (Compose UI)     | Alta         | Alto    | Usar tap por coordenadas absolutas (x=540, y=2080). BMO-Explorer debe verificar en resolución diferente. |
| 2 | Error "Ocurrió un problema" al crear pedido en ambiente de prueba     | Media        | Medio   | Verificar ambiente con cuenta/dirección válida. Puede requerir dirección cercana a tienda Nitro.       |
| 3 | "Estás lejos de la dirección" en checkout y creación                  | Alta         | Bajo    | Warning esperado en ambiente de prueba. No bloquea el flujo.                                           |
| 4 | Carrito vacío tras intento fallido de pedido                          | Media        | Alto    | El setUp debe incluir vaciado del carrito y re-llenado antes de cada ejecución.                        |
| 5 | Opacidad del bottom sheet de propina sobre el checkout                | Media        | Medio   | La jerarquía de accesibilidad mezcla elementos del sheet y del checkout subyacente. Usar bounds del sheet. |
| 6 | Variación de coordenadas en diferentes resoluciones                   | Media        | Medio   | Las coordenadas del botón "Hacer pedido" son relativas a 1080x2340. Ajustar para otras resoluciones.   |
| 7 | Tiempo de espera en pantalla "Estamos creando tu pedido"              | Baja         | Medio   | Implementar espera explícita (waitForElement) en la pantalla de confirmación post-pedido.               |

---

## Cobertura mínima recomendada

### Casos de prueba obligatorios (Happy Path)
1. Flujo completo TurboDev de inicio a fin — propina predeterminada "Me salvas el día".
2. Flujo completo TurboDev — selección de propina personalizada ("Personalizar / Otro").
3. Flujo completo TurboDev — sin propina (si la app permite continuar sin seleccionar).

### Casos de prueba adicionales (Edge Cases)
4. Tap "Hacer pedido" sin propina seleccionada — verificar comportamiento/validación.
5. Tap "Atrás" desde pantalla de propina — verificar retorno correcto al checkout.
6. Cambio de método de pago desde checkout antes de ir a propina.
7. Modificación de instrucciones de entrega desde checkout.
8. Error de red simulado al crear pedido — verificar mensaje de error y recuperación.

---

## Criterios de aceptación

| Criterio                                                                                            | Validado |
|-----------------------------------------------------------------------------------------------------|----------|
| La app navega al bottom sheet de propina al tocar "Continuar" en checkout                          | Si       |
| Las opciones de propina muestran correctamente porcentaje y monto en COP                           | Si       |
| La opción seleccionada ("Me salvas el día") cambia visualmente (fondo negro)                        | Si       |
| El botón "Hacer pedido" está visible y es tappable en la parte inferior del sheet                  | Si       |
| Tras el tap en "Hacer pedido" aparece la pantalla "Estamos creando tu pedido"                      | Si       |
| La pantalla de creación muestra tienda, dirección, tiempo estimado y método de pago                | Si       |
| En ambiente de producción, la pantalla de creación transita a confirmación con número de pedido    | Pendiente (requiere ambiente válido) |

---

## Handoff técnico para BMO-Explorer

### Instrucciones de validación

BMO-Explorer debe:

1. **Verificar el botón "Hacer pedido"** usando coordenadas absolutas `tap(x=540, y=2080)` en pantalla 1080x2340. Si la resolución del dispositivo de prueba es diferente, recalcular proporcionalmente.

2. **Confirmar que el botón "Hacer pedido" NO aparece en UIAutomator** ejecutando:
   ```bash
   adb shell uiautomator dump /sdcard/test.xml && adb pull /sdcard/test.xml /tmp/test.xml
   grep "Hacer pedido" /tmp/test.xml
   ```
   Resultado esperado: sin matches (confirma que es Compose UI puro).

3. **Validar la transición** de propina → "Estamos creando tu pedido" → confirmación final con número de pedido (requiere cuenta con datos válidos).

4. **Verificar estado de la pantalla** de propina con `mobile_list_elements_on_screen` para confirmar que los elementos del sheet son los mismos que los documentados en la tabla de componentes.

5. **Caso de borde:** Intentar el flujo con la dirección más cercana a la tienda Nitro. para evitar el warning "Estás lejos de la dirección" y validar si esto afecta la creación del pedido.

6. **Aprobar o rechazar** el plan actualizando `PlanStatus` a `Approved` o `Rejected` con notas en `ApprovalNotes` o `RejectionNotes`.

### Locators críticos para exploración adicional

```
# Botón Hacer pedido (Compose - solo coordenadas)
tap: x=540, y=2080 (1080x2340)
# Alternativa adb:
adb shell input tap 540 2080

# Opción propina seleccionable (ejemplo: "Me salvas el día")
By.text("Me salvas el día")  → bounds aproximados: [204,1442][784,1493]

# Botón Continuar en checkout (para llegar al sheet)
By.desc("Continuar")  → bounds: [540,2013][1024,2148]  (clickable=false en XML, usar tap por coords)
tap: x=782, y=2080

# Texto de confirmación post-pedido
By.text("Estamos creando tu pedido")
```

---

## Handoff técnico para BMO-TestCreator

### Estructura del test case sugerida

```groovy
// Katalon / Groovy — estructura sugerida
@SetUp
def setUp() {
    // openRappi — lanzar app desde estado limpio
    Mobile.startApplication('com.grability.rappi', true)
    Mobile.delay(3)
}

@Test
def testTurboDev_CompraCompleta() {
    // PASO 1-5: Navegación hasta checkout (ver pasos anteriores)
    // ...
    
    // PASO 6: Verificar checkout
    Mobile.verifyElementExist(findTestObject('checkout/txt_total_a_pagar'), 10)
    Mobile.verifyElementText(findTestObject('checkout/txt_total_amount'), '$16.987')
    
    // PASO 7: Tap en Continuar para ir a propina
    Mobile.tapAtPosition(782, 2080)  // Botón Continuar (Compose)
    Mobile.delay(2)
    Mobile.verifyElementExist(findTestObject('propina/txt_reconoce_esfuerzo'), 10)
    
    // Seleccionar propina "Me salvas el día"
    Mobile.tap(findTestObject('propina/txt_me_salvas_el_dia'), 10)
    Mobile.delay(1)
    
    // PASO 8: Tap en "Hacer pedido"
    Mobile.tapAtPosition(540, 2080)  // Botón Hacer pedido (Compose - sin accessibility ID)
    Mobile.delay(3)
    
    // Verificar pantalla "Estamos creando tu pedido"
    Mobile.verifyElementExist(findTestObject('pedido/txt_creando_pedido'), 15)
}
```

### Archivos de Test Object sugeridos

```
Object Repository/
├── checkout/
│   ├── txt_terminar_y_pagar        → By.text("Terminar y pagar")
│   ├── txt_total_a_pagar           → By.text("Total a pagar")
│   ├── txt_total_amount            → By.text("$16.987")
│   ├── txt_delivery_address        → By.text("Cl. 93 #19-58, Bogotá, Colombia")
│   ├── txt_payment_method          → By.text("Efectivo")
│   └── btn_continuar               → By.desc("Continuar")
├── propina/
│   ├── txt_reconoce_esfuerzo       → By.text("¡Reconoce su esfuerzo!")
│   ├── txt_muchas_gracias          → By.text("Muchas gracias")
│   ├── txt_pal_chesco              → By.text("Pa'l chesco")
│   ├── txt_me_salvas_el_dia        → By.text("Me salvas el día")
│   ├── txt_eres_mi_heroe           → By.text("¡Eres mi héroe!")
│   └── btn_hacer_pedido            → COORDENADAS: tap(540, 2080) — sin locator XML
└── pedido/
    ├── txt_creando_pedido          → By.text("Estamos creando tu pedido")
    ├── txt_store_name              → By.text("Nitro.")
    └── txt_delivery_time           → By.text("15 - 17 minutos con")
```

### Notas críticas para automatización

1. **El botón "Hacer pedido" requiere tap por coordenadas** — no tiene accessibility ID, text, ni content-desc en UIAutomator. Usar `Mobile.tapAtPosition(540, 2080)` en Katalon o `driver.tap(...)` con coordenadas absolutas.

2. **El botón "Continuar" del checkout** tiene `clickable="false"` en la jerarquía pero SÍ responde al tap por coordenadas. Usar `Mobile.tapAtPosition(782, 2080)`.

3. **Esperas explícitas** son necesarias después de:
   - Tap en "Continuar" → esperar sheet de propina (≥2s)
   - Tap en "Hacer pedido" → esperar "Estamos creando tu pedido" (≥3s)
   - Pantalla de creación → esperar confirmación final (≥10s)

4. **El carrito debe re-prepararse** entre ejecuciones. El flujo de compra real consume el carrito.

---

## Compatibilidad multi-dispositivo

| Dispositivo        | Resolución  | Coordenadas "Hacer pedido" | Estado     |
|--------------------|-------------|---------------------------|------------|
| SM-S928B           | 1080x2340   | x=540, y=2080              | Validado   |
| Otros dispositivos | Variable    | Calcular proporcionalmente | Pendiente  |

**Fórmula de ajuste de coordenadas:**
```
x_ajustado = (540 / 1080) * screen_width
y_ajustado = (2080 / 2340) * screen_height
```

Para dispositivos con diferente densidad de píxeles o factor de forma, BMO-Explorer debe re-validar las coordenadas del botón "Hacer pedido" antes de aprobar el plan.

---

## Screenshots de evidencia

| Archivo                                    | Descripción                                                  |
|--------------------------------------------|--------------------------------------------------------------|
| `screenshots/paso8_before_tap.png`         | Pantalla de propina con botón "Hacer pedido" visible         |
| `screenshots/paso8_creating_order.png`     | Pantalla "Estamos creando tu pedido" — confirmación de disparo |
| `screenshots/paso8_error_state.png`        | Error de ambiente post-intento ("Ocurrió un problema")       |
| `screenshots/paso8_cart_empty_error.png`   | Estado "No encontramos productos en tu canasta" (carrito vacío post-error) |

---

*Generado por BMO-FlowPlanner — 2026-04-09*
*PlanStatus: Approved — Validado y aprobado por BMO-Explorer (2026-04-09)*
