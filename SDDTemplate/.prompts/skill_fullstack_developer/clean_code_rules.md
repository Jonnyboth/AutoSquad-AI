# Reglas de Código Limpio — `skill_fullstack_developer`

## 1. Planificación y diseño técnico antes de codear
Toda tarea no trivial empieza con una decisión explícita de diseño: qué se va a construir, qué módulos toca, y por qué se eligió ese enfoque sobre las alternativas. Escribir el diseño primero evita el patrón "codeo y luego pienso", que produce abstracciones incorrectas y retrabajo. Ver el paso 1 del flujo en [system.md](system.md).

## 2. Nomenclatura — la regla más estricta de esta skill

### Variables
- Cortas pero **descriptivas y sin ambigüedad**: el nombre debe decir qué contiene, no un tipo genérico. Prohibidos `data`, `info`, `temp`, `flag`, `x` salvo en scopes de 1-2 líneas (ej. índices de loop).
- Prefiere `userEmail` sobre `email` si hay más de un tipo de email en el mismo scope; prefiere `retryCount` sobre `count` si hay ambigüedad sobre qué se está contando.
- Booleanos siempre como pregunta afirmativa: `isActive`, `hasPermission`, `canRetry` — nunca `flag`, `check`, `status` a secas.
- Constantes en mayúsculas con guion bajo (`MAX_RETRY_ATTEMPTS`); nunca números o strings mágicos sueltos en el código.

### Clases
- Nombre **general** (sustantivo, sin verbos) que describa con precisión la **función principal** de la clase, no su implementación interna. Ejemplo: `PaymentProcessor` (qué hace) en vez de `StripeApiWrapperV2` (cómo lo hace por dentro).
- Evita sufijos vacíos de significado (`Manager`, `Helper`, `Util`) salvo que no exista un sustantivo de dominio mejor. Si una clase termina en `Manager`, pregúntate primero si el nombre correcto es el sustantivo del dominio que administra (`OrderManager` → mejor `OrderRepository` o `OrderLifecycle`, según lo que realmente hace).
- Una clase, una responsabilidad (SRP): si el nombre necesita una "y" para describirla (`UserAndSessionHandler`), hay que dividirla.

### Funciones / métodos
- **Siempre nombradas como una acción** (verbo o frase verbal): `calculateTotal`, `sendEmail`, `validateInput`, `fetchUserById`. Nunca sustantivos sueltos (`total`, `email`, `validation`) para algo que ejecuta lógica.
- Funciones que devuelven booleano usan prefijo de pregunta: `isValid()`, `hasExpired()`.
- Una función hace una cosa; si el nombre necesita "y"/"o" para describirla, divídela.
- Guía de tamaño: ~20-30 líneas; no es una regla dura, pero si crece más es señal de que mezcla responsabilidades.

## 3. Principios generales (SOLID + KISS/YAGNI)
- **S**ingle Responsibility, **O**pen/Closed, **L**iskov Substitution, **I**nterface Segregation, **D**ependency Inversion — aplican especialmente al diseñar clases/módulos nuevos, no como checklist burocrático sino para justificar la estructura elegida en el paso de diseño técnico.
- KISS: la solución más simple que cumple el requisito, no la más "elegante" o extensible a futuro sin necesidad probada (YAGNI).
- Sin comentarios que expliquen el "qué" (el código ya lo dice con buenos nombres); solo comentarios que expliquen un "por qué" no obvio (una restricción externa, un workaround, una decisión no evidente).

## 4. Legibilidad y estructura
- Indentación y formato consistentes con el linter/formatter ya configurado en el proyecto — no reinventar reglas de estilo.
- Evita anidamiento profundo (>3 niveles); usa early returns/guard clauses.
- Un archivo, una responsabilidad clara; si un archivo mezcla capas (ej. lógica de negocio + acceso a datos + HTTP), sepáralo.
