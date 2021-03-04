import sys
import traceback
from django.conf import settings
from django.core.management import call_command
from dj_utils.management.commands.reset import Command as ResetCommand


class Command(ResetCommand):

    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            default_config = settings.DATABASES['default']
            settings.DATABASES ['default'] = default_config
            self.drop_create_db(default_config, root_dir)
            self.re_init_migrations()
            self.migrate_db('default')

            fixture_path = self.get_dj_utils_path()
            fixture_path += '/fixtures/tenants.json'
            call_command('loaddata', fixture_path)

            print('---Done----')
        except:
            eg = traceback.format_exception(*sys.exc_info())
            error_message = ''
            cnt = 0
            for er in eg:
                cnt += 1
                if not 'lib/python' in er and not 'lib\site-packages' in er:
                    error_message += " " + er
            print('Error ' + error_message)
