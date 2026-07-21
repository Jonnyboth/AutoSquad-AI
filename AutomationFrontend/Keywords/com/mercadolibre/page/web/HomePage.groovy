package com.mercadolibre.page.web

import static com.kms.katalon.core.testobject.ObjectRepository.findTestObject
import com.kms.katalon.core.webui.keyword.WebUiBuiltInKeywords as WebUI
import com.kms.katalon.core.model.FailureHandling
import com.kms.katalon.core.testobject.TestObject

/**
 * Interacciones puras de UI en la home de MercadoLibre: verificar que el sitio cargó, cerrar el
 * banner de cookies (opcional) y disparar una búsqueda desde el buscador del header.
 *
 * La apertura del navegador (WebUI.openBrowser) es responsabilidad del Script (precondición del
 * TC), igual que Mobile.startExistingApplication() en los flujos Android - no se duplica aqui.
 */
public class HomePage {

    public void verifyHomeLoaded() {
        TestObject searchBox = findTestObject('Object Repository/web/MercadoLibre/Home/inp_searchBox')
        WebUI.waitForElementVisible(searchBox, 15, FailureHandling.STOP_ON_FAILURE)
    }

    // El banner de cookies solo aparece si el navegador no tiene ya el consentimiento
    // guardado - se maneja siempre como OPTIONAL, nunca bloquea el flujo.
    public void acceptCookiesIfPresent() {
        TestObject cookieBtn = findTestObject('Object Repository/web/MercadoLibre/Home/btn_acceptCookies')
        boolean visible = WebUI.waitForElementVisible(cookieBtn, 5, FailureHandling.OPTIONAL)
        if (visible) {
            WebUI.click(cookieBtn, FailureHandling.OPTIONAL)
        }
    }

    public void searchProduct(String term) {
        TestObject searchBox = findTestObject('Object Repository/web/MercadoLibre/Home/inp_searchBox')
        TestObject searchBtn = findTestObject('Object Repository/web/MercadoLibre/Home/btn_search')
        WebUI.setText(searchBox, term, FailureHandling.STOP_ON_FAILURE)
        WebUI.click(searchBtn, FailureHandling.STOP_ON_FAILURE)
    }
}
