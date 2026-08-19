# Herramientas de `skill_fullstack_developer`

Esta skill trabaja directamente sobre el código del repositorio y su empaquetado. Herramientas habilitadas:

## Lectura y escritura de código
- `Read` / `Write` / `Edit` — leer y modificar archivos de código, `Dockerfile`, `docker-compose.yml`, workflows de CI.
- `Grep` / `Glob` — localizar lógica existente antes de reescribirla (evitar duplicación, ver [clean_code_rules.md](clean_code_rules.md) §3).

## Ejecución y verificación
- `Bash` — instalar dependencias, correr linters/formatters, correr la suite de tests local, y comandos Docker:
  ```bash
  docker build -t <servicio>:<tag> .
  docker compose up --build
  docker compose logs -f <servicio>
  ```
- Nunca ejecutar `docker system prune -a`, `docker rm -f $(docker ps -aq)` u otros comandos destructivos sin confirmación explícita del usuario — pueden afectar contenedores/datos de otros proyectos en la misma máquina.

## Verificación de pipeline
- Si el repo usa GitHub Actions (`.github/workflows/*.yml`), revisar el workflow existente antes de modificarlo; no crear un segundo workflow paralelo para el mismo propósito.

## 📎 Ver también
- [system.md](system.md) — Rol y flujo de trabajo de esta skill.
- [clean_code_rules.md](clean_code_rules.md) — Reglas de nomenclatura y principios de diseño.
- [docker_cicd_practices.md](docker_cicd_practices.md) — Estándar de Dockerfile, compose y pipeline CI/CD.
