package com.mercadolibre.steps.web

import com.kms.katalon.core.annotation.Keyword
import com.kms.katalon.core.util.KeywordUtil
import com.mercadolibre.page.web.DetallePage

public class DetalleSteps {

    DetallePage detallePage = new DetallePage()

    @Keyword
    def assertProductTitleVisible() {
        detallePage.assertProductTitleVisible()
    }

    @Keyword
    def clickAgregarCarrito() {
        detallePage.clickAgregarCarrito()
    }

    @Keyword
    def verifyAddToCartOutcome() {
        Map result = detallePage.verifyAddToCartOutcome()
        KeywordUtil.logInfo("verifyAddToCartOutcome -> ${result}")
    }
}
