import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI

// Run: QA-20260710-mercadolibre-camara-carrito
// Plan: .github/orchestrator/runs/QA-20260710-mercadolibre-camara-carrito.md
//
// Flujo: buscar "camara" en mercadolibre.com.co, entrar al detalle del primer producto
// organico relevante y hacer clic en "Agregar al carrito".
//
// NOTA DE ALCANCE: este entorno no cuenta con credenciales de prueba de MercadoLibre. El
// paso final verifica el comportamiento determinista validado en la exploracion para una
// sesion invitada (prompt de login), no el estado real del carrito. Ver
// com.mercadolibre.page.web.DetallePage.verifyAddToCartOutcome() para el detalle completo.

// ─── PRECONDICION ─────────────────────────────────────────────
WebUI.comment('Abrir MercadoLibre Colombia')
WebUI.openBrowser('https://www.mercadolibre.com.co/')

// ─── PASOS DEL TEST ───────────────────────────────────────────
WebUI.comment('STEP 1: Verificar que la home cargo (buscador visible)')
CustomKeywords.'com.mercadolibre.steps.web.HomeSteps.verifyHomeLoaded'()

WebUI.comment('STEP 2: Cerrar banner de cookies si aparece (OPTIONAL)')
CustomKeywords.'com.mercadolibre.steps.web.HomeSteps.acceptCookiesIfPresent'()

WebUI.comment('STEP 3: Buscar "camara"')
CustomKeywords.'com.mercadolibre.steps.web.HomeSteps.searchProduct'('camara')

WebUI.comment('STEP 4: Verificar que los resultados cargaron (detecta muro anti-bot si aparece)')
CustomKeywords.'com.mercadolibre.steps.web.ResultadosSteps.assertResultsLoaded'()

WebUI.comment('STEP 5: Cerrar popup de ubicacion si aparece (OPTIONAL)')
CustomKeywords.'com.mercadolibre.steps.web.ResultadosSteps.dismissLocationPopupIfPresent'()

WebUI.comment('STEP 6: Entrar al detalle del primer producto organico (no patrocinado)')
CustomKeywords.'com.mercadolibre.steps.web.ResultadosSteps.openFirstProduct'()

WebUI.comment('STEP 7: Verificar que el detalle del producto cargo (titulo visible)')
CustomKeywords.'com.mercadolibre.steps.web.DetalleSteps.assertProductTitleVisible'()

WebUI.comment('STEP 8: Clic en Agregar al carrito')
CustomKeywords.'com.mercadolibre.steps.web.DetalleSteps.clickAgregarCarrito'()

WebUI.comment('🔎🔎🔎  ASSERT 1  🔎🔎🔎  resultado de Agregar al carrito')
CustomKeywords.'com.mercadolibre.steps.web.DetalleSteps.verifyAddToCartOutcome'()

// ─── POSTCONDICION ────────────────────────────────────────────
WebUI.comment('Cerrar navegador')
WebUI.closeBrowser()
