# storage-management

## Development Setup

### Prerequisites

- Python 3.10 (or newer)
- [Poetry](https://python-poetry.org/)
- Access to a PostgreSQL database.

These instructions assume you have a PostgreSQL database running on `localhost:5432` with a database named `storage_management` and that the username and password are both `postgres`. These can be overridden using the `.env` file.

If you are running Docker (or Docker Desktop) you can use the following command to quickly deploy a PostgreSQL database server:

```shell
docker run -p 5432:5432 --name storage-management-postgres -e POSTGRES_PASSWORD=postgres -d postgres
```

### Steps

1. Install the required packages: `poetry install`
2. Load into the virtual environment: `poetry shell`
3. Create a `.env` file using `.env.example` as a reference.
4. Run database migrations: `python manage.py migrate`
5. Create an admin user: `python manage.py createsuperuser`
6. Start development server: `python manage.py runserver`

## End-User Workflow

### User creates ticket

- Only if user_id.banned_until = null or user_id.banned_unit < t.now (not banned or ban elapsed)
- Only if user_id has no tickets with finished_at = null (active tickets)
- Only if spot_id has no tickets with finished_at null (no active tickets)
- created_at set to t.now
- expires_at set to t+7d

### User closes ticket

- Only if finished_at = null (ticket is still active)
- If t.now <= expires_at, user_id.banned_until set to 7d - (t.now - created_at)
- If t.now > expires_at, user_id.banned_until set to t+14d

### Scheduled checks

Run every 5 minutes, iterate over each ticket with finished_at = null (active tickets)

- If t+48h > expires_at and there is no notification of type "48hour", send a "48 hour" notification
- If t+24h > expires_at and there is no notification of type "24hour", send a "24 hour" notification
- If t.now > expires_at and there is no notificaiton of type "expired", send an "expired" notification
- If t+48h > expires_at+7d and there is no notification of type "48hour_expired", send a "48 hour forfiture" notification
- If t+24h > expires_at+7d and there is no notification of type "24hour_expired", send a "24 hour forfiture" notification
- If t.now > expires_at+7d and there is no notificaiton of type "forfiture", send a "forfiture" notification
