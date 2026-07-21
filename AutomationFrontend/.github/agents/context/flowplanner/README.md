# FlowPlanner Context Store

Esta carpeta guarda hallazgos exploratorios por chat/caso para comunicación entre agentes BMO.

## Convencion de nombre de archivo

- `<run-id>-<flujo>.md` donde run-id = `QA-<YYYYMMDD>-<flujo-slug>`
- Ejemplo: `QA-20260408-open-store-geant.md`

## Contenido esperado

- PlanStatus (`Draft`, `Approved`, `Rejected`)
- ApprovedBy (`BMO-Explorer` — aprobación autónoma)
- ApprovalDate
- ApprovalNotes
- RejectionNotes (si fue rechazado)
- Objetivo del flujo
- Precondiciones
- Pasos validados en dispositivo
- Tabla de componentes capturados (class, text, identifier, label/content-desc, bounds, locator sugerido)
- Riesgos y bifurcaciones
- Instrucciones para BMO-Explorer y BMO-TestCreator

## Ciclo de vida del PlanStatus

```
BMO-FlowPlanner crea el archivo → PlanStatus: Draft
         ↓
BMO-Explorer valida en dispositivo real (autónomo)
         ↓
  ┌──────────────────────────────────┐
  │ Válido → PlanStatus: Approved    │  → BMO-TestCreator procede
  │          ApprovedBy: BMO-Explorer│
  └──────────────────────────────────┘
         ↓ (si hay issues)
  ┌──────────────────────────────────┐
  │ Inválido → PlanStatus: Rejected  │  → BMO-FlowPlanner ajusta (máx 3 intentos)
  │            RejectionNotes: ...   │
  └──────────────────────────────────┘
```

## Regla operativa

- BMO-FlowPlanner crea archivos nuevos de contexto (no sobrescribe existentes).
- BMO-FlowPlanner deja el plan en `Draft` — **NO espera aprobación del usuario**.
- BMO-Explorer es el único que puede cambiar `PlanStatus` a `Approved` o `Rejected`.
- BMO-TestCreator solo continúa si `PlanStatus: Approved`.
- QA-Automatizador orquesta el ciclo completo y gestiona retries.
