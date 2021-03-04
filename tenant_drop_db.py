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
# Use the psycopg2.sql module instead of string concatenation
# in order to avoid sql injection attacs.
cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(tenant_arguments.db_to_drop)))
