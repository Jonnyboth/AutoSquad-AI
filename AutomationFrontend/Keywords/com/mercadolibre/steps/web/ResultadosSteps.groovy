package com.mercadolibre.steps.web

import com.kms.katalon.core.annotation.Keyword
import com.mercadolibre.page.web.ResultadosPage

public class ResultadosSteps {

    ResultadosPage resultadosPage = new ResultadosPage()

    @Keyword
    def assertResultsLoaded() {
        resultadosPage.assertResultsLoaded()
    }

    @Keyword
    def dismissLocationPopupIfPresent() {
        resultadosPage.dismissLocationPopupIfPresent()
    }

    @Keyword
    def openFirstProduct() {
        resultadosPage.openFirstProduct()
    }
}
