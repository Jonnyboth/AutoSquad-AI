package com.mercadolibre.utils

import com.kms.katalon.core.annotation.Keyword
import com.kms.katalon.core.configuration.RunConfiguration

/**
 * Lee variables del .env global del proyecto (symlink en la raiz de
 * AutomationFrontend hacia ~/.config/autosquad-ai/global.env). Katalon no
 * soporta dotenv nativamente, asi que este keyword parsea el archivo a mano.
 * Prioriza variables ya exportadas en el entorno del sistema sobre las del .env.
 */
public class EnvLoader {

    private static Map<String, String> cache

    private static synchronized Map<String, String> load() {
        if (cache != null) {
            return cache
        }
        Map<String, String> values = [:]
        File envFile = new File(RunConfiguration.getProjectDir(), '.env')
        if (envFile.exists()) {
            envFile.eachLine { line ->
                String trimmed = line.trim()
                if (trimmed && !trimmed.startsWith('#') && trimmed.contains('=')) {
                    int idx = trimmed.indexOf('=')
                    values[trimmed.substring(0, idx).trim()] = trimmed.substring(idx + 1).trim()
                }
            }
        }
        cache = values
        return cache
    }

    @Keyword
    static String get(String key, String defaultValue = '') {
        String fromSystemEnv = System.getenv(key)
        if (fromSystemEnv != null) {
            return fromSystemEnv
        }
        return load().get(key, defaultValue)
    }
}
