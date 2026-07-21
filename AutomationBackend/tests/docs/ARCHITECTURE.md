# Arquitectura del Framework

## 1. Objetivo

Framework de automatización **solo-API** (sin Selenium/Appium) construido sobre
`pytest` + `requests`, pensado para:

- Validar contratos de respuesta (schema), no solo status codes.
- Evitar duplicación de payloads/rutas entre tests.
- Permitir ejecución paralela y multi-ambiente (dev/qa/prod) sin tocar código.
- Dejar trazabilidad completa de cada petición (cURL + tiempos) en el reporte.

## 2. Capas y responsabilidad única

```
┌─────────────────────────────────────────────────────────────┐
│ tests/                  → QUÉ se prueba (casos de negocio)   │
├─────────────────────────────────────────────────────────────┤
│ services/                → CÓMO se ejecuta la operación      │
│  (Service Object Pattern: AuthService, UsersService)          │
├─────────────────────────────────────────────────────────────┤
│ builders/  │  models/     → CON QUÉ datos (payloads tipados) │
│ utils/data_generator                                          │
├─────────────────────────────────────────────────────────────┤
│ core/http_client          → CÓMO se transporta (HTTP crudo)  │
│ core/session_manager, core/logger, core/exceptions             │
├─────────────────────────────────────────────────────────────┤
│ config/                   → DÓNDE se ejecuta (ambiente/rutas)│
└─────────────────────────────────────────────────────────────┘
```

Cada capa solo conoce la inmediatamente inferior. Un test **nunca** importa
`requests` directamente; un `service` **nunca** decide contra qué ambiente
corre. Esto permite cambiar de proveedor HTTP, de ambiente o de esquema de
datos sin tocar los tests.

## 3. Flujo de una petición (ejemplo: crear usuario)

```
test_create_user
   │
   ├─> UserBuilder().with_last_name("QA-Automation").build()  # builders/ -> CreateUserRequest (Pydantic)
   │
   └─> users_service.create_user(payload)              # services/
          │
          └─> http_client.post(UsersEndpoints.BASE, ...)  # core/http_client.py
                 │
                 ├─ arma el PreparedRequest real
                 ├─ imprime el cURL exacto (core/http_client._log_as_curl)
                 ├─ envía con reintento si es GET (tenacity)
                 └─ loguea status + latencia (core/logger.py)
```

## 4. Patrones de diseño aplicados

| Patrón | Dónde | Por qué |
|---|---|---|
| **Service Object** | `services/auth_service.py`, `services/users_service.py` | Equivalente al Page Object Model pero para APIs: centraliza la lógica de negocio de cada dominio, los tests no conocen rutas ni payloads crudos. |
| **Builder** | `builders/user_builder.py` | Payloads complejos se arman de forma legible y encadenable (`with_first_name().with_last_name()`), con valores por defecto aleatorios (Faker) para no repetir datos fijos entre tests. |
| **Facade / Wrapper** | `core/http_client.py` | Oculta los detalles de `requests.Session`, retry y logging cURL detrás de una interfaz simple (`get/post/put/patch/delete`). |
| **Singleton por sesión de pytest** | `session_manager` (fixture `scope="session"`) | Un solo login por corrida completa de la suite, no por test. |
| **DTO tipado (Pydantic)** | `models/` | Reemplaza diccionarios sueltos; valida tipos en tiempo de armado del payload y de parseo de la respuesta (contract testing liviano). |

## 5. Gestión de ambientes

`config/environment.py` lee la variable `ENV` (`dev`/`qa`/`prod`, default `qa`)
y resuelve el `BASE_URL` correspondiente desde `.env`. No hay ramas `if env ==
"prod"` dispersas en el código: todo pasa por `get_environment()`, inyectado
como fixture `environment` en `conftest.py`.

## 6. Autenticación

`core/session_manager.py` hace login una sola vez (vía `AuthService`) y cachea
el token en el `HttpClient` compartido (`requests.Session` con header
`Authorization` seteado). La fixture `authenticated_client` expone ese cliente
ya autenticado a cualquier test que lo necesite.

## 7. Resiliencia de red

`http_client._request_with_retry` reintenta (backoff exponencial, máx. 3
intentos) únicamente en `GET`, por ser idempotente. `POST/PUT/PATCH/DELETE` no
se reintentan automáticamente: reintentar una operación no-idempotente ante un
timeout puede duplicar efectos secundarios (ej. crear el mismo usuario dos
veces) y enmascarar un bug real de latencia del backend.

## 8. Observabilidad / Reporte

- **Consola** (`core/console_reporter.py`, vía `-s` en `pytest.ini`): imprime en
  vivo cada request, response y aserción con color ANSI.
- **Archivo** (`core/logger.py`): nivel `WARNING+` en consola (para no
  duplicar el output de `console_reporter`), `DEBUG` completo (incluye cURL)
  en `reports/test_execution.log`.
- **HTML** (`core/html_report.py`, dashboard propio sin dependencias externas):
  `conftest.py` recolecta resultado + detalle de cada test vía
  `pytest_runtest_logreport`, y al terminar la corrida (`pytest_sessionfinish`)
  agrupa los tests por carpeta (deducida del nodeid) y escribe un reporte por
  carpeta en `tests/<carpeta>/reports/`, con fecha y hora en el nombre —
  cada corrida queda en el historial, no sobrescribe la anterior. Incluye
  tarjetas de resumen, gráfica de dona filtrable y filas expandibles con el
  mismo detalle de request/response/aserciones que la consola.
- El cURL (log de archivo) se imprime a partir del `PreparedRequest` real, no
  reconstruido a mano, así siempre refleja exactamente lo que salió por el socket.

## 9. Extender el framework

Para agregar un nuevo dominio (ej. `products`):

1. `config/endpoints.py` → agregar `ProductsEndpoints`.
2. `models/product_model.py` → DTOs de request/response.
3. `builders/product_builder.py` → si el payload es complejo.
4. `services/products_service.py` → métodos de negocio (`create_product`, ...).
5. `tests/test_products_api.py` → casos de prueba, marcados `smoke`/`regression`.

No se toca `core/` ni `config/environment.py` para agregar un dominio nuevo:
esa es la señal de que la separación de capas está funcionando.
