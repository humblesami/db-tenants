import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE
import tenant_arguments

con = psycopg2.connect(
    dbname='postgres',
    user='odoo',
    password='123'
)

con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) # <-- ADD THIS LINE
cur = con.cursor()
close_db_sessions_sql = """
    SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity
    WHERE pg_stat_activity.datname='"""+tenant_arguments.db_to_drop+"""'
"""
cur.execute(close_db_sessions_sql)
# Use the psycopg2.sql module instead of string concatenation
# in order to avoid sql injection attacs.
drop_db_sql = "DROP DATABASE if exists {}"
drop_db_sql = drop_db_sql.format(tenant_arguments.db_to_drop)
cur.execute(drop_db_sql)
