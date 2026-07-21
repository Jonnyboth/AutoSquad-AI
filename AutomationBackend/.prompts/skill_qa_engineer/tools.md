# Herramientas de `skill_qa_engineer`

Esta skill integra con **AIO Tests** (Jira Cloud) mediante dos artefactos equivalentes en esta misma carpeta:

1. [aio_tests_client.py](aio_tests_client.py) — cliente CLI/librería Python, usa `requests` directo contra la API REST de AIO Tests.
2. [aio_tests_api.py](aio_tests_api.py) — servicio **FastAPI** que envuelve ese mismo cliente y lo expone como endpoints HTTP locales (útil si otro proceso/agente quiere invocar por HTTP en vez de por CLI).

Ambos comparten la misma configuración (`.env`) y la misma lógica de autenticación/errores.

## 0. Configuración previa (obligatoria)

1. Copia `.env.example` a `.env` en esta carpeta y completa los valores reales:

   ```bash
   cp .env.example .env
   ```

   | Variable | Descripción |
   |---|---|
   | `AIO_API_TOKEN` | Token de AIO Tests (sin el prefijo `AioAuth `; el script lo agrega automáticamente al armar la cabecera `Authorization`) |
   | `PROJECT_KEY` | Clave del proyecto Jira, por defecto `TP` |
   | `AIO_BASE_URL` | URL base de la API de AIO Tests (región EU o US según tu instancia) |

2. Instala dependencias:

   ```bash
   pip install -r .prompts/skill_qa_engineer/requirements.txt
   ```

**Endpoints confirmados.** La base URL (`https://tcms.aiojiraapps.com/aio-tcms`) y los paths usados en `aio_tests_client.py` fueron verificados contra el OpenAPI oficial que AIO Tests publica en `https://tcms.aiojiraapps.com/aio-tcms/aiotcms-static/api-docs/` (spec en `.../api/v1/openapi.json`), y contra la documentación pública en [aiosupport.atlassian.net/wiki/spaces/AioTests/pages/2025619567](https://aiosupport.atlassian.net/wiki/spaces/AioTests/pages/2025619567). El parámetro `jiraProjectId` de la API acepta tanto la key del proyecto (`TP`) como su ID numérico, así que no hace falta resolver el ID manualmente.

## 1. Vía CLI — `aio_tests_client.py`

### Crear un Caso de Prueba
```bash
python3 .prompts/skill_qa_engineer/aio_tests_client.py create --json-file caso.json
```
donde `caso.json` sigue la estructura descrita en [test_spec.md](test_spec.md).

### Actualizar un Caso de Prueba existente
```bash
python3 .prompts/skill_qa_engineer/aio_tests_client.py update --id 1234 --json '{"description": "Nueva descripción del caso"}'
```

### Obtener un Caso de Prueba puntual
```bash
python3 .prompts/skill_qa_engineer/aio_tests_client.py get --id 1234
```

### Listar Casos de Prueba del proyecto (para mantenimiento)
```bash
python3 .prompts/skill_qa_engineer/aio_tests_client.py list --max-results 100
```

### Buscar por título (evitar duplicados antes de crear)
```bash
python3 .prompts/skill_qa_engineer/aio_tests_client.py search --title-contains "login"
```

También puede importarse como módulo:
```python
from aio_tests_client import create_test_case, update_test_case, get_test_case, list_test_cases, search_test_cases
```

## 2. Vía HTTP — `aio_tests_api.py` (FastAPI)

Levantar el servicio local:
```bash
cd .prompts/skill_qa_engineer
uvicorn aio_tests_api:app --reload --port 8000
```

Documentación interactiva (Swagger UI) generada automáticamente: `http://127.0.0.1:8000/docs`.

### Endpoints expuestos

| Método | Path | Descripción |
|---|---|---|
| `GET` | `/health` | Verifica que el servicio está arriba y qué `project_key`/`base_url` usa por defecto |
| `POST` | `/test-cases` | Crea un nuevo Caso de Prueba |
| `PUT` | `/test-cases/{test_case_id}` | Actualiza (parcial o totalmente) un Caso de Prueba existente |
| `GET` | `/test-cases/{test_case_id}` | Obtiene el detalle de un Caso de Prueba puntual |
| `GET` | `/test-cases?max_results=&start_at=` | Lista/pagina los Casos de Prueba del proyecto |

### Ejemplo — crear vía HTTP
```bash
curl -X POST http://127.0.0.1:8000/test-cases \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Login exitoso con credenciales válidas",
    "description": "Valida que un usuario registrado pueda iniciar sesión correctamente.",
    "precondition": "El usuario existe previamente y está activo.",
    "priority": "High",
    "labels": ["login", "smoke"],
    "steps": [
      {"step": "Navegar a la pantalla de login", "test_data": "URL: /login", "expected_result": "Se muestra el formulario con usuario y contraseña"},
      {"step": "Ingresar credenciales válidas y presionar Ingresar", "test_data": "usuario: qa_user@ejemplo.com", "expected_result": "El sistema redirige al dashboard principal"}
    ]
  }'
```

### Ejemplo — actualizar vía HTTP
```bash
curl -X PUT http://127.0.0.1:8000/test-cases/1234 \
  -H "Content-Type: application/json" \
  -d '{"priority": "Low"}'
```

## Manejo de errores (ambas vías)

| Código HTTP | Significado en este contexto |
|---|---|
| `200` / `201` | Operación exitosa (lectura / creación) |
| `400` | JSON inválido o payload sin campos para actualizar |
| `401` | `AIO_API_TOKEN` inválido, expirado o cabecera `Authorization` ausente |
| `403` | El token no tiene permisos sobre el proyecto/recurso |
| `404` | Proyecto o Caso de Prueba (ID) no existe |
| `429` | Rate limiting de AIO Tests alcanzado |
| `500` / `502` / `503` | Error del servidor de AIO Tests o de red al contactarlo |

El cliente CLI imprime el error por consola (`logger.error`) y termina con `sys.exit(1)`. El servicio FastAPI traduce esos mismos errores a `HTTPException` con el código correspondiente.
