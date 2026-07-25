# AutoSquad-AI

Plantilla de **Súper Agente Orquestador** (Scrum Master AI) para conducir el ciclo de vida
completo de un proyecto ágil — planeación, diseño, construcción y QA — delegando cada fase a
skills de IA especializadas, integradas de forma nativa con herramientas reales de gestión de
proyectos (Jira, AIO Tests) y de automatización de pruebas (Playwright, Appium, Katalon).

No está atado a ningún dominio de negocio: los ejemplos de este repositorio (autenticación,
recordatorios, etc.) son ilustrativos. Clona el módulo que necesites y adapta las skills a tu
propio proyecto.

## Cómo funciona

```mermaid
flowchart TD
    U["Usuario"] -->|"pide una tarea"| SA["Súper Agente Orquestador\n(super_agent_*.md, uno por módulo)"]

    SA -->|"1. Planeación"| PM["skill_project_manager\nHU en formato BDD"]
    SA -->|"2. Diseño"| UX["skill_ui_ux_designer\nPrototipos responsivos"]
    SA -->|"3. Construcción"| DEV["skill_fullstack_developer\nCódigo + SOLID"]
    SA -->|"4. Verificación"| QA["skill_qa_engineer\nCasos de prueba + bugs"]

    PM -->|"MCP Atlassian / REST"| JIRA[("Jira Cloud\nBacklog")]
    QA -->|"MCP aio-tests / REST"| AIO[("AIO Tests\nCasos de prueba")]
    QA -->|"exploración guiada"| AUTO["Playwright / Appium /\nmobile-mcp / Katalon"]

    SA -.->|"refleja estado"| BL["docs/BACKLOG.md"]
```

Cada skill vive como una carpeta de *prompts* en `.prompts/<skill>/` con:
- `system.md` — rol, estándar de calidad y flujo de trabajo obligatorio de esa skill.
- `tools.md` — cómo se integra con el sistema externo real (MCP, API REST, CLI de respaldo).
- `examples.md` / `test_spec.md` / etc. — plantillas de invocación y ejemplos rellenos.

Cada orquestador de módulo no improvisa: si una skill referenciada en su catálogo no tiene su
carpeta implementada todavía, se detiene y lo informa en vez de simular su comportamiento (ver
la regla crítica en cada `super_agent_*.md`).

## Estructura del repositorio

Cada módulo tiene su propio orquestador con nombre identificable (ya no comparten el genérico
`super_agent.md`), para poder invocar el de cualquier módulo sin ambigüedad desde una única
sesión abierta en la raíz del repositorio:

| Módulo | Rol | Orquestador | Skills implementadas |
|---|---|---|---|
| [`FuncionalQaPm/`](FuncionalQaPm) | Gestión funcional de backlog y QA manual/exploratorio | [`super_agent_Qa_PM.md`](FuncionalQaPm/.prompts/super_agent_Qa_PM.md) | `skill_project_manager`, `skill_qa_engineer` |
| [`AutomationBackend/`](AutomationBackend) | Automatización de pruebas de backend (pytest) | [`super_agent_automation_backend.md`](AutomationBackend/.prompts/super_agent_automation_backend.md) | `skill_qa_engineer` |
| [`SDDTemplate/`](SDDTemplate) | Plantilla de desarrollo dirigido por especificación (backend + frontend) | [`super_agent_sdd_template.md`](SDDTemplate/.prompts/super_agent_sdd_template.md) | `skill_fullstack_developer`, `skill_ui_ux_designer` |
| [`AutomationFrontend/`](AutomationFrontend) | Proyecto Katalon Studio de automatización de UI (web/móvil) | — (sin orquestador todavía) | — (proyecto de automatización, no de orquestación) |

> Cada módulo evolucionó de forma independiente, así que hoy ningún módulo tiene las 4 skills
> completas a la vez. Para un ciclo de vida punta a punta, combina las carpetas `.prompts/`
> que necesites en un mismo proyecto.

## Ejecutar todo desde la raíz (instancia única)

La raíz del repositorio tiene su propio [`.mcp.json`](.mcp.json), que agrega los servidores MCP
de los 3 módulos con orquestador (Zephyr, Atlassian, Playwright, aisquare-playwright, mobile-mcp,
aio-tests-mcp, y una variante de `appium-mcp` por módulo). Al abrir una sesión de Claude Code con
`AutoSquad-AI` como carpeta raíz del workspace, las herramientas de los 3 módulos quedan
disponibles en la misma sesión — no hace falta reabrir el editor dentro de cada subcarpeta.

Para trabajar como el QA/PM, el de automatización de backend o el de SDD, dile al agente que siga
las instrucciones del archivo `super_agent_*.md` correspondiente de la tabla de arriba; las
herramientas MCP de ese módulo ya están conectadas. Cada módulo conserva también su propio
`.mcp.json` local, así que sigue funcionando igual si alguien prefiere abrir Claude Code aislado
dentro de esa subcarpeta en vez de en la raíz.

## Integraciones reales configuradas

- **Jira Cloud**: creación de Historias de Usuario y reporte de bugs vía el MCP de Atlassian
  (`com.atlassian/atlassian-mcp-server`), con un script Python de contingencia (REST API) si el
  MCP no está disponible en la sesión.
- **AIO Tests** (gestión de casos de prueba sobre Jira Cloud): creación/actualización/búsqueda
  de Casos de Prueba vía MCP dedicado o cliente REST propio (`aio_tests_client.py`), con triage
  anti-duplicados obligatorio antes de crear un caso nuevo.
- **Automatización de exploración**: `playwright-mcp` / `aisquare-playwright` para web,
  `appium-mcp` / `mobile-mcp` para móvil, usados por `skill_qa_engineer` cuando un requerimiento
  es ambiguo y necesita evidencia real antes de diseñar un caso de prueba.

## Puesta en marcha

1. Elige el módulo (o combinación de módulos) que se ajuste a tu proyecto.
2. Copia `.prompts/<skill>/.env.example` a `.env` en cada skill que lo requiera y completa tus
   propias credenciales (Jira, AIO Tests) — **nunca** commitees el `.env` real.
3. Abre el proyecto con tu agente (Claude Code, Copilot, etc.) desde la raíz `AutoSquad-AI` y
   activa el `super_agent_*.md` del módulo con el que quieras trabajar (ver tabla arriba) como
   punto de entrada; él te guiará sobre qué skill activar según la fase en la que estés.
4. Personaliza `docs/BACKLOG.md` con el backlog real de tu propio proyecto Jira — el que viene
   en este repo es solo un ejemplo del formato esperado.

## Convenciones comunes a todas las skills

- Todo el contenido generado (HUs, casos de prueba, bugs) se redacta en español.
- Ninguna skill marca una tarea como `Done` sin pasar por verificación de QA.
- Ninguna skill inventa datos, IDs o campos de configuración que no haya podido confirmar
  contra la herramienta real — ante un error o un dato no verificable, se detiene e informa.
