import psycopg

from .config import settings


def get_conn():
    return psycopg.connect(settings.database_url)


# Alias used by locations service
get_db_connection = get_conn
