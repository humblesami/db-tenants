import sys
import traceback
from psycopg2 import connect

from django.conf import settings
from django.core.management import BaseCommand
from django.core.management import call_command

from dj_utils import methods


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            dest='name',
        )

        parser.add_argument(
            '--apps',
            dest='apps',
        )

        parser.add_argument(
            '--create',
            dest='create',
        )

    def handle(self, *args, **kwargs):
        try:
            db_key = kwargs.get('name')
            tenant_apps = kwargs.get('apps')

            for app_name in settings.SHARED_APPS:
                cmd_str = 'migrate'
                try:
                    arr = app_name.split('.')
                    app_name = arr[len(arr) - 1]
                    call_command(cmd_str, app_name, database=db_key)
                except:
                    message = methods.get_error_message()
                    if 'does not have migrations.' in message:
                        pass
                    else:
                        raise

            for app_name in tenant_apps:
                cmd_str = 'migrate'
                call_command(cmd_str, app_name, database=db_key)

            print('---Done----')
        except:
            error_message = methods.get_error_message()
            print('Error ' + error_message)
            raise
