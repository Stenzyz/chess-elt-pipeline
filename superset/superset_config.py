import os

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql+psycopg2://"
    f"{os.environ.get('SUPERSET_USER')}:{os.environ.get('SUPERSET_PASSWORD')}"
    f"@superset-postgres:5432/{os.environ.get('SUPERSET_DB')}"
)
