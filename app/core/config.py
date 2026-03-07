import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/workouts",
    )
    AUTO_CREATE_TABLES: bool = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"


settings = Settings()
