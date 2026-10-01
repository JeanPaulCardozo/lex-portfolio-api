# Lex Portfolio API

Backend REST API for **Lex Portfolio**, a lawyer's portfolio site. Built with
FastAPI, SQLAlchemy and PostgreSQL. It is the real backend that will replace
the mock/localStorage data layer used by the [lex-portfolio](../lex-portfolio)
frontend, following the contract described in that project's `API_CONTRACT.md`.

**Languages / Idiomas:** [Español](#español) · [English](#english)

---

## Español

### Qué es esto

API para el portafolio de una abogada: perfil, áreas de práctica, casos,
trayectoria, publicaciones y testimonios, más autenticación con JWT para el
panel de administración. El sitio público (estático) consume los endpoints de
solo lectura sin autenticación; el panel de administración usa un token
Bearer para crear, editar y borrar contenido.

### Stack

- **FastAPI** (`fastapi[standard]`) sobre **Python 3.14**
- **SQLAlchemy 2.0** (ORM) + **Alembic** (migraciones)
- **PostgreSQL** (Supabase en desarrollo) — se usan tipos nativos de Postgres
  (`ARRAY`, `JSONB`, `ENUM`), así que no es compatible con SQLite
- **JWT** vía `python-jose`, contraseñas con `passlib[bcrypt]`
- **slowapi** para rate-limiting (`/auth/login` y `/testimonials/submit`: 5 intentos por minuto)
- **CORS** restringido por origen (`CORSMiddleware` en `main.py`) — solo el dominio del frontend puede llamar a la API desde el navegador
- **uv** como gestor de paquetes y entorno virtual
- **pytest** + `httpx`/`TestClient` para las pruebas

### Estructura del proyecto

```
src/lex_portfolio_api/
├── main.py                # app de FastAPI, registra todos los routers
├── database.py            # engine, sessionmaker, get_db()
├── core/
│   ├── dependencies.py    # get_current_user / get_current_user_optional
│   ├── security.py        # hash/verify de contraseñas, JWT
│   ├── limiter.py         # instancia de slowapi
│   └── slugify.py         # slug a partir de un título/nombre
├── models/                 # entidades de SQLAlchemy
├── schemas/                 # modelos de Pydantic (entrada/salida)
├── routers/                # endpoints de FastAPI por recurso
└── services/                 # lógica de acceso a datos (consultas, altas, etc.)

alembic/versions/            # migraciones, en el orden en que se aplicaron
tests/                       # pruebas con pytest (ver más abajo)
```

### Puesta en marcha

1. Instala dependencias:
   ```powershell
   uv sync
   ```
2. Copia `src/lex_portfolio_api/.env_example` a
   `src/lex_portfolio_api/.env` y completa los valores (ver tabla abajo).
3. Aplica las migraciones:
   ```powershell
   uv run alembic upgrade head
   ```
4. Levanta el servidor de desarrollo:
   ```powershell
   uv run python -m fastapi dev src/lex_portfolio_api/main.py
   ```
   (se usa `python -m fastapi` en vez de `fastapi` a secas porque, en Windows
   con Smart App Control activado, el `.exe` generado en `.venv/Scripts/` puede
   quedar bloqueado por la política de control de aplicaciones — pasar por
   `python.exe`, que sí está firmado, evita el bloqueo).

### Variables de entorno

| Variable | Para qué sirve |
|---|---|
| `DATABASE_URL` | Cadena de conexión completa a Postgres |
| `POSTGRES_USER`, `POSTGRES_PASS`, `POSTGRES_DB` | Credenciales individuales (si no usas `DATABASE_URL` directo) |
| `SECRET_KEY` | Clave para firmar los JWT — **nunca** la subas al repo |
| `ALGORITHM` | Algoritmo de firma del JWT (por defecto `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de validez del token (por defecto `30`) |

### Pruebas

Las pruebas corren contra la **misma base de datos** de `DATABASE_URL` — no
hay una base en memoria, porque varios modelos usan tipos exclusivos de
Postgres que SQLite no soporta (`ARRAY`, `JSONB`, `ENUM` nativo). Cada prueba
queda envuelta en una transacción que se revierte al final, así que no se
guarda nada de forma permanente, sin importar cuántos `commit()` haga el
código de la aplicación. También se resetea el *rate limiter* antes de cada
prueba, para que varias pruebas de login seguidas no choquen con el límite de
5 por minuto.

```powershell
uv run pytest
```

### Resumen de endpoints

Autenticación vía header `Authorization: Bearer <token>`, obtenido en
`POST /auth/login`. Rutas sin marcar como "público" requieren ese header.

| Recurso | Rutas |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Perfil | `GET /profile/`, `PATCH /profile/` (upsert) |
| Áreas de práctica | `GET /practice-areas/`, `GET /practice-areas/{slug}`, `POST /practice-areas/`, `PATCH /practice-areas/{id}`, `DELETE /practice-areas/{id}` |
| Casos | `GET /cases/` (filtros `practice_area_id`, `year`, `result_type`, `query`), `GET /cases/{slug}`, `POST /cases/`, `PATCH /cases/{id}`, `DELETE /cases/{id}` |
| Trayectoria | `GET /experience/`, `POST /experience/`, `PATCH /experience/{id}`, `DELETE /experience/{id}` |
| Publicaciones | `GET /publications/`, `POST /publications/`, `PATCH /publications/{id}`, `DELETE /publications/{id}` |
| Testimonios | `GET /testimonials/` (**público**, solo aprobados, sin email) · `GET /testimonials/?all=1` (privado, todos) · `POST /testimonials/submit` (**público**, el visitante propone uno, siempre queda `pending`) · `POST /testimonials/`, `PATCH /testimonials/{id}`, `PATCH /testimonials/{id}/status`, `DELETE /testimonials/{id}` |

Notas puntuales:

- Los **casos** se relacionan con un área de práctica por `practice_area_id`
  (no por nombre), para evitar inconsistencias.
- El campo `result_type` de los casos y `kind` de las publicaciones son enums:
  el *nombre* en Python está en inglés (`judgment`, `article`, ...), pero el
  *valor* que viaja por la API sigue en español (`"sentencia"`,
  `"articulo"`, ...) para no romper el contrato existente con el frontend.
- Los campos de fecha "año-mes" (`start_date`/`end_date` de trayectoria) y de
  fecha completa (`date` de publicaciones) se guardan como texto validado
  (`"AAAA-MM"` / `"AAAA-MM-DD"`), no como tipo `DATE` — se valida formato y que
  no sea una fecha futura en el schema de Pydantic.
- Un testimonio enviado desde `/testimonials/submit` **ignora** cualquier
  `status` que venga en el cuerpo: siempre se guarda como pendiente de
  revisión.

### Ejemplo rápido de uso

Un recorrido completo con `curl`: crear un usuario, loguearte, usar el token
para crear contenido, y consultar lo público sin token.

**1. Registrarte** (una sola vez; luego solo haces login):
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "abogada@example.com", "password": "unaClaveSegura123"}'
```

**2. Iniciar sesión** — nota que este endpoint recibe *form data*, no JSON
(es el estándar OAuth2 que usa FastAPI), y el campo del correo se llama
`username` aunque sea un email:
```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=abogada@example.com&password=unaClaveSegura123"
```
Respuesta:
```jsonc
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```
Guarda ese `access_token` — lo vas a necesitar en cada ruta privada, en el
encabezado `Authorization: Bearer <token>`.

**3. Crear una ruta privada** (ejemplo: un área de práctica), usando el token:
```bash
curl -X POST http://localhost:8000/practice-areas/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Derecho laboral",
    "summary": "Reclamaciones y despidos",
    "description": "...",
    "fags": []
  }'
```
La respuesta trae el `id` que acaba de asignar la base de datos — lo vas a
necesitar para crear un caso relacionado a esa área (`practice_area_id`).

**4. Consultar una ruta pública, sin token** (lo que vería el sitio público):
```bash
curl http://localhost:8000/testimonials/
```

**5. Enviar un testimonio como visitante, sin token** (lo que haría el
formulario público del sitio):
```bash
curl -X POST http://localhost:8000/testimonials/submit \
  -H "Content-Type: application/json" \
  -d '{
    "author": "Laura Méndez",
    "author_role": "Sector comercio",
    "quote": "Me explicó todo con claridad.",
    "rating": 5,
    "email": "laura@example.com"
  }'
```
Queda guardado como pendiente de revisión; el titular lo aprueba desde el
panel con `PATCH /testimonials/{id}/status`.

**Documentación interactiva:** con el servidor corriendo, FastAPI genera sola
una página para probar todos los endpoints desde el navegador, en
`http://localhost:8000/docs` (Swagger UI) — ahí puedes autenticarte una vez
(botón "Authorize") y probar las rutas privadas sin tener que copiar el token
a mano en cada `curl`.

---

## English

### What this is

The API behind a lawyer's portfolio site: profile, practice areas, cases,
work experience, publications and testimonials, plus JWT authentication for
the admin panel. The public (static) site consumes the read-only endpoints
without authentication; the admin panel uses a Bearer token to create, edit
and delete content.

### Stack

- **FastAPI** (`fastapi[standard]`) on **Python 3.14**
- **SQLAlchemy 2.0** (ORM) + **Alembic** (migrations)
- **PostgreSQL** (Supabase in development) — several models use
  Postgres-only types (`ARRAY`, `JSONB`, native `ENUM`), so SQLite is not an
  option
- **JWT** via `python-jose`, password hashing with `passlib[bcrypt]`
- **slowapi** for rate limiting (`/auth/login` and `/testimonials/submit`: 5 attempts per minute)
- **CORS** restricted by origin (`CORSMiddleware` in `main.py`) — only the frontend's domain can call the API from a browser
- **uv** as the package/virtualenv manager
- **pytest** + `httpx`/`TestClient` for the test suite

### Project layout

```
src/lex_portfolio_api/
├── main.py                # FastAPI app, registers every router
├── database.py            # engine, sessionmaker, get_db()
├── core/
│   ├── dependencies.py    # get_current_user / get_current_user_optional
│   ├── security.py        # password hashing/verification, JWT
│   ├── limiter.py         # slowapi instance
│   └── slugify.py         # slug generation from a title/name
├── models/                 # SQLAlchemy entities
├── schemas/                 # Pydantic models (request/response shapes)
├── routers/                # FastAPI endpoints per resource
└── services/                 # data-access logic (queries, creates, etc.)

alembic/versions/            # migrations, in the order they were applied
tests/                       # pytest suite (see below)
```

### Getting started

1. Install dependencies:
   ```powershell
   uv sync
   ```
2. Copy `src/lex_portfolio_api/.env_example` to
   `src/lex_portfolio_api/.env` and fill in the values (see table below).
3. Apply migrations:
   ```powershell
   uv run alembic upgrade head
   ```
4. Start the dev server:
   ```powershell
   uv run python -m fastapi dev src/lex_portfolio_api/main.py
   ```
   (`python -m fastapi` instead of plain `fastapi` because, on Windows with
   Smart App Control enabled, the `.exe` wrapper generated in
   `.venv/Scripts/` can get blocked by the application control policy —
   going through `python.exe`, which is signed, avoids the block).

### Environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Full Postgres connection string |
| `POSTGRES_USER`, `POSTGRES_PASS`, `POSTGRES_DB` | Individual credentials (if not using `DATABASE_URL` directly) |
| `SECRET_KEY` | Key used to sign JWTs — **never** commit this |
| `ALGORITHM` | JWT signing algorithm (defaults to `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes (defaults to `30`) |

### Tests

Tests run against the **same database** as `DATABASE_URL` — there is no
in-memory fallback, since several models use Postgres-only types that
SQLite cannot create (`ARRAY`, `JSONB`, native `ENUM`). Each test is wrapped
in a transaction that gets rolled back at the end, so nothing is ever
persisted permanently no matter how many times the application code calls
`commit()`. The rate limiter is also reset before every test, so several
login tests in a row don't trip the 5-per-minute limit.

```powershell
uv run pytest
```

### Endpoint overview

Authentication is a `Authorization: Bearer <token>` header, obtained from
`POST /auth/login`. Any route not marked "public" requires that header.

| Resource | Routes |
|---|---|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Profile | `GET /profile/`, `PATCH /profile/` (upsert) |
| Practice areas | `GET /practice-areas/`, `GET /practice-areas/{slug}`, `POST /practice-areas/`, `PATCH /practice-areas/{id}`, `DELETE /practice-areas/{id}` |
| Cases | `GET /cases/` (filters: `practice_area_id`, `year`, `result_type`, `query`), `GET /cases/{slug}`, `POST /cases/`, `PATCH /cases/{id}`, `DELETE /cases/{id}` |
| Experience | `GET /experience/`, `POST /experience/`, `PATCH /experience/{id}`, `DELETE /experience/{id}` |
| Publications | `GET /publications/`, `POST /publications/`, `PATCH /publications/{id}`, `DELETE /publications/{id}` |
| Testimonials | `GET /testimonials/` (**public**, approved only, no email) · `GET /testimonials/?all=1` (private, all of them) · `POST /testimonials/submit` (**public**, a visitor proposes one, always saved as pending) · `POST /testimonials/`, `PATCH /testimonials/{id}`, `PATCH /testimonials/{id}/status`, `DELETE /testimonials/{id}` |

A few specific notes:

- **Cases** relate to a practice area through `practice_area_id` (not by
  name), to avoid inconsistencies.
- The case `result_type` and publication `kind` fields are enums: the
  Python *member name* is in English (`judgment`, `article`, ...), but the
  *value* that actually travels over the API stays in Spanish
  (`"sentencia"`, `"articulo"`, ...) so the existing contract with the
  frontend doesn't break.
- "Year-month" date fields (experience `start_date`/`end_date`) and
  full-date fields (publication `date`) are stored as validated strings
  (`"YYYY-MM"` / `"YYYY-MM-DD"`), not as a `DATE` type — format and
  not-in-the-future checks happen in the Pydantic schema.
- A testimonial sent through `/testimonials/submit` **ignores** any
  `status` present in the request body: it is always saved pending review.

### Quick usage example

A full walkthrough with `curl`: create a user, log in, use the token to
create content, and query public data without a token.

**1. Register** (one time only; after that you just log in):
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "lawyer@example.com", "password": "aSecurePassword123"}'
```

**2. Log in** — note this endpoint takes *form data*, not JSON (it's the
standard OAuth2 flow FastAPI uses), and the email field is called
`username` even though it's an email address:
```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=lawyer@example.com&password=aSecurePassword123"
```
Response:
```jsonc
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```
Save that `access_token` — you'll need it on every private route, in the
`Authorization: Bearer <token>` header.

**3. Call a private route** (example: create a practice area) using the token:
```bash
curl -X POST http://localhost:8000/practice-areas/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Labor law",
    "summary": "Claims and wrongful termination",
    "description": "...",
    "fags": []
  }'
```
The response includes the `id` the database just assigned — you'll need it
to create a case related to that area (`practice_area_id`).

**4. Call a public route, no token** (what the public site would see):
```bash
curl http://localhost:8000/testimonials/
```

**5. Submit a testimonial as a visitor, no token** (what the site's public
form would do):
```bash
curl -X POST http://localhost:8000/testimonials/submit \
  -H "Content-Type: application/json" \
  -d '{
    "author": "Laura Mendez",
    "author_role": "Commerce sector",
    "quote": "They explained everything clearly.",
    "rating": 5,
    "email": "laura@example.com"
  }'
```
It's saved pending review; the lawyer approves it from the admin panel via
`PATCH /testimonials/{id}/status`.

**Interactive docs:** with the server running, FastAPI auto-generates a page
to try every endpoint from the browser, at `http://localhost:8000/docs`
(Swagger UI) — authenticate once there (the "Authorize" button) and test
private routes without copying the token by hand into every `curl` call.
