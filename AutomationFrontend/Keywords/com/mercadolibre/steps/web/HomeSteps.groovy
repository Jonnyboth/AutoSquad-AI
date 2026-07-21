package com.mercadolibre.steps.web

import com.kms.katalon.core.annotation.Keyword
import com.mercadolibre.page.web.HomePage

public class HomeSteps {

    HomePage homePage = new HomePage()

    @Keyword
    def verifyHomeLoaded() {
        homePage.verifyHomeLoaded()
    }

    @Keyword
    def acceptCookiesIfPresent() {
        homePage.acceptCookiesIfPresent()
    }

    @Keyword
    def searchProduct(String term) {
        homePage.searchProduct(term)
    }
}
