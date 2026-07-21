# Resumen por Módulo

Referencia rápida de qué hace cada archivo y cuándo tocarlo.

## `config/`

| Archivo | Resumen |
|---|---|
| `environment.py` | Lee `ENV` (dev/qa/prod) y variables de `.env`; devuelve un `EnvironmentConfig` inmutable con `base_url`, credenciales y `timeout`. Único punto donde se decide "contra qué servidor corremos". Tocar solo si se agrega un nuevo ambiente o variable de configuración global. |
| `endpoints.py` | Constantes de rutas relativas agrupadas por dominio (`AuthEndpoints`, `UsersEndpoints`). Si el backend cambia una ruta, se corrige en un solo lugar. Tocar al agregar un endpoint nuevo. |

## `core/`

| Archivo | Resumen |
|---|---|
| `http_client.py` | Envoltorio sobre `requests.Session`. Expone `get/post/put/patch/delete` tipados, delega en `console_reporter` la impresión de cada request/response (consola + buffer HTML) y reintenta automáticamente los `GET` ante errores de conexión/timeout (backoff exponencial, 3 intentos). El cURL equivalente sigue logueándose en el archivo (`DEBUG`). |
| `session_manager.py` | Hace login una única vez por corrida y cachea el token en el `HttpClient` compartido. Fixture `authenticated_client` en `conftest.py` depende de esto. |
| `logger.py` | Configura logging dual: consola (`WARNING+`, para no interferir con `console_reporter`) + archivo `reports/test_execution.log` (`DEBUG`, incluye el cURL completo). Evita duplicar handlers si pytest reimporta el módulo. |
| `exceptions.py` | Excepciones propias: `ApiRequestError` (fallos de red), `ApiAssertionError` (fallos de aserción de negocio), `SchemaValidationError` (contrato de respuesta incumplido). |
| `console_reporter.py` | Fuente única de datos del reporte: imprime en consola (color ANSI) el request/response/aserciones de cada test y, en paralelo, acumula esos mismos eventos como datos estructurados (`reset_buffer`/`pop_buffer_items`) que `conftest.py` recolecta al final de cada test. También imprime el arte de bienvenida por archivo (`print_module_banner`). |
| `html_report.py` | Generador del reporte HTML propio (dashboard morado oscuro con tarjetas, dona filtrable y filas expandibles). `generate_report(path, title, generated_at, data)` escribe un único archivo HTML autocontenido (CSS + JS vanilla inline, sin dependencias externas ni build) a partir del diccionario `{"environment": ..., "tests": [...]}` armado en `conftest.py`. |

## `models/`

| Archivo | Resumen |
|---|---|
| `auth_model.py` | DTOs Pydantic `LoginRequest`/`LoginResponse`. Tipa y valida el contrato de `/login` en tiempo de ejecución (ej. `EmailStr` rechaza un email mal formado antes de siquiera llamar al backend). |
| `user_model.py` | DTOs `CreateUserRequest`/`UserResponse` del dominio de usuarios. |

Regla: si el test necesita armar o leer un payload, primero se define (o
reutiliza) un modelo aquí — no se pasan diccionarios sueltos entre capas.

## `services/`

| Archivo | Resumen |
|---|---|
| `auth_service.py` | Lógica de negocio de autenticación: arma el `LoginRequest`, llama `http_client`, valida status 200 y devuelve el token ya parseado (`LoginResponse.token`). Es lo único que sabe que `/login` existe. |
| `users_service.py` | Operaciones CRUD de usuarios (`create_user`, `get_user`, `update_user`, `delete_user`, `list_users`) sobre `HttpClient`. Los tests llaman estos métodos, nunca `http_client.post(...)` directo. |

Regla: un `service` por dominio de negocio. Si un test necesita orquestar dos
servicios (ej. crear usuario y luego loguearse), esa orquestación vive en el
test, no dentro de un service.

## `builders/`

| Archivo | Resumen |
|---|---|
| `user_builder.py` | Builder encadenable para `CreateUserRequest`. Genera datos aleatorios por defecto (Faker) y permite sobreescribir solo el campo relevante al caso de prueba (`UserBuilder().with_last_name("QA-Automation").build()`). Evita hardcodear payloads completos en cada test. |

## `utils/`

| Archivo | Resumen |
|---|---|
| `assertions.py` | Aserciones reutilizables: `assert_status_code`, `assert_response_time`, `assert_json_schema` (valida contra JSON Schema con `jsonschema`), `assert_body_contains`, `assert_header_present`. Todas lanzan `ApiAssertionError`/`SchemaValidationError` con mensaje descriptivo (incluye el body real recibido). |
| `data_generator.py` | Wrappers sobre `Faker` (`random_first_name`, `random_last_name`, `random_email`, `random_age`, `random_password`). Punto único de generación de datos dinámicos, usado por los `builders/`. |

## `tests/` (casos de prueba)

Organizados por nivel de prueba, un subdirectorio por tipo. Cada uno hereda las
fixtures de `tests/conftest.py` (no se duplican). Ver [`tests/README.md`](../tests/README.md)
para los comandos de ejecución por carpeta.

| Carpeta | Archivo | Resumen |
|---|---|---|
| `conftest.py` (raíz de `tests/`) | — | Fixtures de dominio: `users_service`, `auth_service`. |
| `smoke/` | `test_auth_smoke.py`, `test_users_smoke.py` | Casos críticos de humo (login exitoso, creación de usuario). Se ejecutan como carpeta completa. |
| `regression/` | `test_auth_regression.py`, `test_users_regression.py` | Casos de borde: credenciales inválidas/incompletas, usuario inexistente, paginación. Se ejecutan como carpeta completa. |
| `component/` | `test_auth_component.py`, `test_users_component.py` | Contrato de un servicio aislado (estructura del JWT, schema de usuario). Se ejecutan archivo por archivo. |
| `e2e/` | `test_user_lifecycle_e2e.py` | Flujo de negocio completo encadenado: crear → consultar → actualizar → eliminar usuario. Se ejecuta archivo por archivo. |

## Raíz del proyecto

| Archivo | Resumen |
|---|---|
| `conftest.py` | Fixtures de infraestructura compartidas por toda la suite: `environment`, `http_client` (sin auth), `session_manager`, `authenticated_client`. Todas con `scope="session"`. También define: `--no-html-report` (boolean para activar/desactivar el HTML), `pytest_runtest_logreport` (recolecta resultado + items de `console_reporter` por test) y `pytest_sessionfinish`, que agrupa los tests por carpeta (`smoke`/`regression`/`component`/`e2e`, deducida del nodeid) y llama a `html_report.generate_report` una vez por carpeta, guardando en `tests/<carpeta>/reports/` con fecha y hora en el nombre (y el nombre del archivo de test si la corrida tocó uno solo) — así cada corrida queda en el historial en vez de sobrescribir. |
| `pytest.ini` | Config de ejecución: `-v -s` (stdout sin capturar, para ver el reporte en vivo), marcadores `smoke`/`regression`/`component`/`e2e`, convención de nombres de archivos/funciones de test. |
| `requirements.txt` | Dependencias fijadas por versión exacta para builds reproducibles. |
| `.env.example` | Plantilla de variables de entorno (URLs por ambiente, credenciales, timeout). Se copia a `.env` (git-ignorado) y se completa con valores reales. |
