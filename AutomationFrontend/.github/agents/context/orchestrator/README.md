# Orchestrator Context Store

Esta carpeta guarda el estado del pipeline de QA-Automatizador por cada ejecución.

## Convencion de nombre de archivo

- `<run-id>.md` donde run-id = `QA-<YYYYMMDD>-<flujo-slug>`
- Ejemplo: `QA-20260408-geant-busqueda.md`

## Ciclo de vida del pipeline

```
Phase: FASE_1          → FlowPlanner generando plan
Phase: FASE_2_VALIDATE → Explorer validando plan
Phase: FASE_2_CAPTURE  → Explorer capturando objetos
Phase: FASE_3          → TestCreator creando automatización
Phase: FASE_4          → Debugger aplicando fix (opcional)
Phase: COMPLETED       → Pipeline exitoso
Phase: FAILED          → Pipeline detenido, requiere intervención
```

## Regla operativa

- QA-Automatizador crea un archivo por ejecución (no sobrescribe existentes).
- Cada fase actualiza el estado del archivo antes de avanzar.
- Si el pipeline se reinicia con el mismo run-id, leer estado actual y continuar desde la fase pendiente.
- Máximo 3 intentos de plan antes de escalar al usuario.
