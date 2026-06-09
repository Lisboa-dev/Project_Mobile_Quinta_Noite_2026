import os


class Settings:
    database_url = os.getenv(
        "ANALYTIC_DATABASE_URL",
        "postgresql://postgres:password@analytic-postgres:5432/analyticdb",
    ).replace("+psycopg2", "")
    rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    user_events_exchange = os.getenv("USER_EVENTS_EXCHANGE", "users.events")
    agenda_events_exchange = os.getenv("RABBITMQ_EXCHANGE", "agenda.events")
    events_queue = os.getenv("ANALYTIC_EVENTS_QUEUE", "analytic.events")
    routing_keys = [key.strip() for key in os.getenv("ANALYTIC_EVENT_ROUTING_KEYS", "#").split(",") if key.strip()]


settings = Settings()
