import sys
import traceback
from django.conf import settings

from tenants.models import Tenant
from dj_utils.management.commands.reset import Command as ResetCommand


class Command(ResetCommand):

    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            modes_dict = {'drop_create_db': 1, 'make': 2, 'migrate': 3}
            mode = 3
            default_config = settings.DATABASES['default']
            tenant_names = []

            try:
                tenant_names = Tenant.objects.values_list('name', flat=True)
                tenant_names = list(tenant_names)
            except:
                tenant_names = []
                pass

            if mode == 1:
                self.drop_create_db(default_config, root_dir)
            self.all_dbs.append(default_config['NAME'])

            for tenant_dict in tenant_names:
                new_config = default_config.copy()
                new_config['NAME'] = tenant_dict['name']
                if mode == 1:
                    self.drop_create_db(new_config, root_dir)
                self.all_dbs.append(new_config['NAME'])

            if mode == 2:
                self.re_init_migrations()
            if mode == 3:
                self.migrate_all()
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
