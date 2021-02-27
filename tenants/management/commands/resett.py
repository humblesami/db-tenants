import sys
import traceback
from django.conf import settings

from tenants.middlewares import THREAD_LOCAL
from tenants.models import Tenant
from dj_utils.management.commands.reset import Command as ResetCommand


class Command(ResetCommand):


    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            default_config = settings.DATABASES['default']
            tenants_list = []
            try:
                query = "select name from tenants_tenant"
                tenants_list = self.exec_query_on_default(default_config, query, 1)
            except:
                pass

            self.drop_create_db(default_config, root_dir)

            for tenant_dict in tenants_list:
                new_config = default_config.copy()
                new_config['NAME'] = tenant_dict['name']
                res = self.drop_create_db(new_config, root_dir)
                if res:
                    print(res)
                    return

            self.re_init_migrations()
            self.migrate_all()
            setattr(THREAD_LOCAL, "DB", default_config['NAME'])
            for tenant_dict in tenants_list:
                if not Tenant.objects.filter(name=tenant_dict['name']):
                    Tenant.objects.create(name=tenant_dict['name'])

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
