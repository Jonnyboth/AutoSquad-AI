package com.mercadolibre.page.web

import static com.kms.katalon.core.testobject.ObjectRepository.findTestObject
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI
import com.kms.katalon.core.model.FailureHandling
import com.kms.katalon.core.testobject.TestObject
import com.kms.katalon.core.util.KeywordUtil

/**
 * Interacciones puras de UI en la página de resultados de búsqueda de MercadoLibre.
 */
public class ResultadosPage {

    // MercadoLibre presenta ocasionalmente un muro anti-bot (reCAPTCHA / verificación de cuenta)
    // ante tráfico automatizado. No es un error de locator: es una protección externa del sitio
    // que no se puede resolver por código. Se detecta explícitamente para dar un mensaje claro
    // en vez de un timeout genérico de "elemento no encontrado".
    public boolean isBlockedByAntiBot() {
        boolean captchaWall = WebUI.verifyTextPresent('Por seguridad, completa este paso', false)
        boolean robotCheck  = WebUI.verifyTextPresent('No soy un robot', false)
        // Variante adicional observada en el paso "4-Correr Tests" del pipeline (no vista durante
        // la exploracion inicial): un gate generico "Para continuar, ingresa a tu cuenta" con
        // botones "Soy nuevo"/"Ya tengo cuenta" y un trace-id, que aparece en vez de los resultados
        // de busqueda. A diferencia del prompt de login especifico de "Agregar al carrito" (que
        // dice "Para agregar al carrito, ingresa a tu cuenta"), este aparece mucho antes en el
        // flujo y bloquea incluso ver resultados de busqueda como usuario invitado.
        // Se detecta por "Soy nuevo" + "Ya tengo cuenta" (botones de esa pantalla) en vez del texto
        // completo del encabezado: el encabezado se renderiza partido en varias lineas/indentado en
        // el HTML fuente, por lo que un match literal de substring con espacios fallaba.
        boolean loginWallOnResults = WebUI.verifyTextPresent('Soy nuevo', false) &&
                                      WebUI.verifyTextPresent('Ya tengo cuenta', false)
        return captchaWall || robotCheck || loginWallOnResults
    }

    public void assertResultsLoaded() {
        TestObject firstProduct = findTestObject('Object Repository/web/MercadoLibre/Resultados/item_firstProduct')
        boolean visible = WebUI.waitForElementVisible(firstProduct, 15, FailureHandling.OPTIONAL)
        if (visible) return

        WebUI.takeScreenshot()
        if (isBlockedByAntiBot()) {
            KeywordUtil.markFailedAndStop(
                'MercadoLibre presento un muro anti-bot (reCAPTCHA / verificacion de cuenta) en la ' +
                'pagina de resultados. No es un error de locator ni de codigo: es una proteccion del ' +
                'sitio contra trafico automatizado que no se puede resolver programaticamente. ' +
                'Reintentar mas tarde - no es un caso para ajustar locators.'
            )
            return
        }
        KeywordUtil.markFailedAndStop(
            'Los resultados de busqueda no cargaron en 15s y no se detecto ninguno de los patrones ' +
            'de muro anti-bot conocidos. Ver screenshot en runner/reports/ para diagnostico.'
        )
    }

    // El popup "Conoce el envio a tu ubicacion" aparece de forma intermitente - siempre OPTIONAL.
    public void dismissLocationPopupIfPresent() {
        TestObject laterBtn = findTestObject('Object Repository/web/MercadoLibre/Resultados/btn_dismissLocationPopup')
        boolean visible = WebUI.waitForElementVisible(laterBtn, 5, FailureHandling.OPTIONAL)
        if (visible) {
            WebUI.click(laterBtn, FailureHandling.OPTIONAL)
        }
    }

    // a[href*="/p/MCO"] resuelve siempre al primer resultado ORGANICO (no patrocinado) - los
    // resultados "Ad" en este layout usan enlaces de redireccion de tracking en vez de enlaces
    // directos al PDP, ver Object Repository/web/MercadoLibre/Resultados/item_firstProduct.rs
    public void openFirstProduct() {
        TestObject firstProduct = findTestObject('Object Repository/web/MercadoLibre/Resultados/item_firstProduct')
        // click() del runner solo espera presencia en el DOM (presenceOfElementLocated), no
        // visibilidad ni "clickable" - se fuerza visibilidad + scroll antes del clic porque el
        // elemento puede quedar tapado/fuera de viewport tras cerrar el popup de ubicacion.
        WebUI.waitForElementVisible(firstProduct, 15, FailureHandling.STOP_ON_FAILURE)
        WebUI.scrollToElement(firstProduct, FailureHandling.OPTIONAL)
        WebUI.click(firstProduct, FailureHandling.STOP_ON_FAILURE)
    }
}
