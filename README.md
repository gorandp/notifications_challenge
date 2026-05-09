[![test-status-image]][test-status]


# Notifications Challenge

A simple notification service that can send SMS, Email and Push notifications
as required by the user.

If you want a quick try of the application, go to https://notif.gorandp.com/
and register a new account.

If you want to see the API reference, go to https://notif-api.gorandp.com/docs

- Backend: FastAPI
- Hosting: Cloudflare Workers
- Frontend: React ([repository](https://github.com/gorandp/notifications_challenge_front))
- Testing: Pytest
- Architecture: Clean architecture


## Run API locally with FastAPI

1. Clone this repo
2. Run `uv sync`
3. Create a `.env` file with the following variables
  - `JWT_SECRET` variable set to a random string
  - `DB_CONNECTION_STRING` variable set to the location of the sqlite database, or leave it empty and will create a `dev.db` in the root dir (if you want to use the Cloudflare D1 local db, locate it in `.wrangler/state/v3/d1/miniflare-D1DatabaseObject/<LONGHASH>.sqlite`, which is created after running the API with pywrangler and doing at least 1 HTTP request to any API endpoint)
4. Run `uv run fastapi run src/main.py`


## Run API locally with Pywrangler

1. Clone this repo
2. Run `uv sync` ([Don`t have uv? Install it from here](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer))
3. Run `npm install` (to install Wrangler)
4. Create a `.env` file with the following variables
  - `JWT_SECRET` variable set to a random string
5. Run `npm run dev` or `uv run pywrangler dev`


## Clean Architecture

https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html



[test-status-image]: https://github.com/gorandp/notifications_challenge/actions/workflows/test.yml/badge.svg
[test-status]: https://github.com/gorandp/notifications_challenge/actions/workflows/test.yml
