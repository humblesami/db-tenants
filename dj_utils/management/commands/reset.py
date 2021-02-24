import os
import sys
import importlib
import traceback
from pathlib import Path

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'setting up db i.e. create db or drop db for dev purpose'
    all_dbs = []

    def drop_create_db(self, db_config, root_dir):
        db_engine = db_config['ENGINE']
        arr = db_engine.split('.')
        if len(arr):
            db_engine = arr[len(arr) - 1]

        if db_engine == 'sqlite':
            db_path = Path.as_posix(root_dir) + '/db.sqlite3'
            if os.path.exists(db_path):
                os.remove(db_path)
            return 'done'

        default_db = 'postgres'
        if db_engine == 'mysql':
            default_db = db_engine

        db_host_connection = connect(
            database=default_db,
            user=db_config['USER'],
            password=db_config['PASSWORD'],
        )
        db_host_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        if type (db_host_connection) is str:
            return db_host_connection

        db_cursor = db_host_connection.cursor()
        db_name = db_config['NAME']

        # stmt = 'REVOKE CONNECT ON DATABASE '+db_name+' FROM public'
        # db_cursor.execute(stmt)
        stmt = "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity"
        stmt += " WHERE pg_stat_activity.datname = '"+db_name+"'"
        db_cursor.execute(stmt)

        stmt = 'DROP DATABASE if exists ' + db_name
        db_cursor.execute(stmt)
        stmt = 'CREATE DATABASE ' + db_name
        db_cursor.execute(stmt)
        db_cursor.close()
        db_host_connection.close()

        print("Database " + db_config['NAME'] + " created")

    def re_init_migrations(self):
        cmd_str = 'makemigrations'
        # cmd_str = 'python manage.py ' + cmd_str
        call_command(cmd_str)

    def migrate_all(self):
        for db_key in self.all_dbs:
            print("migrating " + db_key)
            cmd_str = 'migrate'
            call_command(cmd_str, database=db_key)
            # Pinter@rt5
            cmd_str = 'loaddata ' + self.module_path + '/fixtures/data.json'
            call_command(cmd_str)
            print("done with " + db_key)

    def set_module_path(self):
        module_path = os.path.dirname(__file__)
        module_path = os.path.dirname(module_path)
        module_path = os.path.dirname(module_path)
        self.module_path = module_path

    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            self.set_module_path()

            for db_key in settings.DATABASES:
                self.all_dbs.append(db_key)
                self.drop_create_db(settings.DATABASES[db_key], root_dir)

            self.re_init_migrations()
            self.migrate_all()
        except:
            eg = traceback.format_exception(*sys.exc_info())
            error_message = ''
            cnt = 0
            for er in eg:
                cnt += 1
                if not 'lib/python' in er and not 'lib\site-packages' in er:
                    error_message += " " + er
            print('Error ' + error_message)
