# Database migrations (Alembic)

Generate a new migration after changing the models:

```bash
alembic revision --autogenerate -m "describe your change"
```

Apply migrations:

```bash
alembic upgrade head
```

The database URL is read from the `DATABASE_URL` environment variable via
`app.core.config`, so make sure your `.env` is configured first.
