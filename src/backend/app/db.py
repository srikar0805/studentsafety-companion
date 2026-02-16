import psycopg

from .config import settings


def get_conn():
    return psycopg.connect(settings.database_url)
