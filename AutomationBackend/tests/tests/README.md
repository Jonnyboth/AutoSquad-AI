# Ejecución de tests por carpeta

Todos los comandos se corren desde la raíz del proyecto (`AutomationBackend/tests/`), con el venv activo.

| Carpeta | Contenido | Cómo se ejecuta |
|---|---|---|
| `smoke/` | Casos críticos, deben pasar siempre | A nivel de carpeta completa |
| `regression/` | Suite completa de regresión | A nivel de carpeta completa |
| `component/` | Un servicio/endpoint aislado | Archivo por archivo |
| `e2e/` | Flujos de negocio completos | Archivo por archivo |

## Smoke (carpeta completa)

```bash
pytest tests/smoke/
```

## Regression (carpeta completa)

```bash
pytest tests/regression/
```

## Component (archivo por archivo)

```bash
pytest tests/component/test_auth_component.py
pytest tests/component/test_users_component.py
```

## E2E (archivo por archivo)

```bash
pytest tests/e2e/test_user_lifecycle_e2e.py
```

## Suite completa (todas las carpetas)

```bash
pytest
```

## Reporte HTML (con historial, por carpeta)

Cualquiera de los comandos anteriores genera un reporte HTML por defecto,
dentro de la carpeta `reports/` de cada carpeta de test tocada — cada corrida
crea un archivo nuevo (no sobrescribe), con fecha y hora en el nombre:

```
tests/smoke/reports/20260709_001112.html
tests/component/reports/test_auth_component_20260709_001041.html
```

Si el comando corrió un solo archivo (caso típico de `component/`/`e2e/`), el
nombre lleva `{archivo}_{fecha}_{hora}.html`; si corrió la carpeta completa
(`smoke/`/`regression/`), el nombre es solo `{fecha}_{hora}.html`.

Para desactivarlo, agrega `--no-html-report`:

```bash
pytest tests/smoke/ --no-html-report
```

## Salida en consola

Por defecto (`-s` en `pytest.ini`) se imprime en vivo, por cada test: el
request (body incluido), el response (status + body) y cada aserción con
`✔ SUCCESS ASSERTION` o `✘ FAILED ASSERTION`. Al iniciar cada archivo se
muestra además un arte de bienvenida.
