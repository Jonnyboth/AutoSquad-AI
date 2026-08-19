# Buenas Prácticas de CI/CD con Docker — `skill_fullstack_developer`

## 1. Dockerfile
- **Multi-stage builds**: una etapa `build` con las herramientas de compilación/instalación y una etapa `runtime` mínima (`-slim`/`-alpine` o distroless) que solo copia los artefactos finales — nunca enviar el toolchain completo a producción.
- **Pin de versiones**: imagen base con tag explícito y, cuando sea posible, digest (`node:20.11-slim@sha256:...`); nunca `latest`.
- **Usuario no-root**: crear y usar un usuario sin privilegios (`USER app`) para el proceso final — nunca correr como `root` en producción.
- **Cache de capas**: copiar primero los manifiestos de dependencias (`package.json`/`requirements.txt`) e instalar dependencias, y solo después copiar el resto del código — así el cache de Docker no se invalida en cada cambio de código.
- **`.dockerignore` obligatorio**: excluir `node_modules`, `.git`, `.env`, artefactos de build, tests — reduce el contexto de build y evita filtrar secretos.
- **Healthcheck**: definir `HEALTHCHECK` (o el equivalente en el orquestador) para que el contenedor reporte su estado real, no solo "está corriendo".
- **Sin secretos en la imagen**: nunca `COPY .env` ni credenciales embebidas — inyectar en runtime vía variables de entorno o un gestor de secretos.

## 2. docker-compose (entorno local/dev)
- Un servicio por responsabilidad (app, db, cache) — no todo-en-uno.
- Variables sensibles vía `.env` (no versionado; documentar en `.env.example`).
- Volúmenes nombrados para persistencia de datos; bind mounts solo para código en modo desarrollo (hot-reload).
- Redes explícitas en vez de depender del default cuando hay múltiples servicios con distintos niveles de exposición.

## 3. Pipeline de CI/CD
Etapas mínimas, en este orden — cada una debe bloquear la siguiente si falla:
1. **Lint/format check** — falla rápido, es la más barata.
2. **Tests** (unitarios + integración) — sin mockear infraestructura crítica si el proyecto ya tiene convención de tests de integración reales.
3. **Build de la imagen Docker** — usando el mismo `Dockerfile` que se usará en producción (no un build "especial" para CI).
4. **Escaneo de vulnerabilidades** de la imagen (ej. Trivy/Grype) antes de publicar.
5. **Push al registry** solo si todo lo anterior pasó, con tag inmutable (hash del commit o semver) — nunca sobrescribir `latest` como único tag.
6. **Deploy** — idealmente con posibilidad de rollback inmediato (mantener la imagen anterior disponible).

## 4. Reglas estrictas
- No mezclar la etapa de build/test con la que hace deploy — cada etapa debe poder fallar independientemente y quedar visible en el reporte del pipeline.
- No usar `--no-verify`, saltar tests, ni desactivar el escaneo de seguridad para "apurar" un release.
- Toda imagen que llega a producción debe haber pasado por el mismo pipeline — no builds manuales locales publicados directo al registry de producción.
