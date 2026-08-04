[![test-status-image]][test-status]
[![Coverage Status](https://coveralls.io/repos/github/gorandp/notifications_challenge/badge.svg?branch=main)](https://coveralls.io/github/gorandp/notifications_challenge?branch=main)

# Notifications Challenge

A simple notification service that can send SMS, Email and Push notifications
as required by the user.

If you want a quick try of the application, go to https://notif.gorandp.com/
and register a new account.

If you want to see the API reference, go to https://notif-api.gorandp.com/docs

- Backend: FastAPI
- Host: Google Cloud Platform: Cloud Run + Cloud Build + Artifact Registry
- Frontend: React ([repository](https://github.com/gorandp/notifications_challenge_front))
- Testing: Pytest
- Architecture: Clean architecture
- Database: PostgreSQL (hosted at [Neon](https://neon.com/))
- Migrations: Alembic


## Features

- Users CRUD (Create, Read, Update, Delete)
- Channels CRUD (SMS, Email, Push)
- Notifications CRUD and send


## Run/test API with Docker

### Pre-requisites

- Docker installed without SUDO permission: https://www.docker.com/
- Docker compose installed (usually installed along with Docker Desktop)
- Ports free: 8000 (app), 5432 (postgres)

### Run

```sh
# Start
docker compose -f docker-compose.yml up --build
# To end it
docker compose down
```

You can visit the API at http://localhost:8000/docs

### Test

```sh
# Start
docker compose -f docker-compose.test.yml up --build
# To end it
docker compose down
```


## Run/test API locally (bare machine - no Docker)

### Pre-requisites

- uv: https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
- (optional) nvm (to install Wrangler via npm): https://github.com/nvm-sh/nvm#installing-and-updating
- Port free: 8000
- PostgreSQL installed

### Run with FastAPI

1. Run `uv sync` ([Don`t have uv? Install it from here](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer))
2. Create a `.env` file with the following variables
  - `JWT_SECRET` variable set to a random string
  - `DB_CONNECTION_STRING` url of the postgresql database (postgresql+psycopg://user:password@localhost/notifdb)
3. Run `uv run fastapi run src/main.py`

You can visit the API at http://localhost:8000/docs

### Test

1. Run `uv sync`
2. Create a `.env` file with the following variable
  - `DB_CONNECTION_STRING` url of the postgresql database (postgresql+psycopg://user_test:password_test@localhost/notifdb_test). It is suggested that the database name differs with the production database name.
3. Run `uv run pytest`
  - Or run `uv run coverage run -m pytest` and then `uv run coverage html` to get the coverage report

## Migrations

While developing, schema changes may be needed. To reflect that in the database, it is used Alembic to generate the migrations which shows what to change in the database schema. And those migrations can be also run with alembic.

As a prerequisite, it is needed to update the `.env` file with the database connection string.

Scripts:

- Generate new revision/migration: `uv run alembic revision --autogenerate -m "Message"`
- Apply all migrations: `uv run alembic upgrade head`
- Current migration state: `uv run alembic current`
- Revisions history: `uv run alembic history`

Notice that `uv` is used in every script, but if you have an environment without uv and all packages installed (like a production environment or a virtual envionment), you can run the exact same scripts removing `uv run` from them.


## Seeder

If you want to get an already working app with data, you can seed your DB running the following script (setting DB_CONNECTION_STRING beforehand):

```sh
uv run populate_db.py
```


## Areas to improve

- Select queries should get only the fields that are needed for each request to be more efficient in data transfers


## Techs

- FastAPI
- Docker
- OpenAPI
- PostgreSQL


## Decisions made

- Clean architecture was chosen in order to be able to handler further changes in the future in a proper way. [Reference](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- Docker: To make it portable
- Pytest/Testing/E2E: Pytest is one of the most used testing framework of Python as well as unittest, so it is easy to find fixes and people that know how to use it. E2E testing was done because it evaluates the whole chain of work in few tests, meaning it is more flexible to internal changes but enforces that the results are always the same.
- PostgreSQL: Industry standard for most web applications. Handle concurrent connections well.
- Alembic: Used to generate and run migrations, which ease the tracking of the schema changes over time and apply incremental changes safely.


## Route

- http://localhost:8000/docs


## Env vars

You can look at a `.env` example at `.env.example`.


[test-status-image]: https://github.com/gorandp/notifications_challenge/actions/workflows/test.yml/badge.svg
[test-status]: https://github.com/gorandp/notifications_challenge/actions/workflows/test.yml
