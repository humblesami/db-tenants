import os
import sys
import traceback
from django.conf import settings
from dj_utils.management.commands.reset import Command as ResetCommand

from tenants.models import Tenant


class Command(ResetCommand):

    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            self.set_module_path()

            modes_dict = {'drop_create_db': 1, 'make': 2, 'migrate': 3}
            selected_mode = 'migrate'
            mode = modes_dict[selected_mode]
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
            self.all_dbs.append('default')

            for tenant_dict in tenant_names:
                new_config = default_config.copy()
                new_config['NAME'] = tenant_dict['name']
                if modes_dict[selected_mode] == 1:
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
