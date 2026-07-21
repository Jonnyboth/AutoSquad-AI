package com.kms.katalon.core.testcase

/**
 * Stub de TestCaseEntity de Katalon.
 * Usado por findTestCase() y WebUI.callTestCase().
 */
class TestCaseEntity {
    String path   // "Test Cases/android/openRappi"
    String name   // "openRappi"

    @Override
    String toString() { "TestCase(${path})" }
}
