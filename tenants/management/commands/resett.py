import sys
import traceback
from django.conf import settings
from tenants.models import Tenant
from dj_utils.management.commands.reset import Command as ResetCommand


class Command(ResetCommand):

    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            default_config = settings.DATABASES['default']
            tenants_list = []
            try:
                query = "select id,name from tenants_tenant"
                tenants_list = self.exec_query_on_default(default_config, query, 1)
            except:
                eg = traceback.format_exception(*sys.exc_info())
                error_message = ''
                cnt = 0
                for er in eg:
                    cnt += 1
                    if not 'lib/python' in er and not 'lib\site-packages' in er:
                        error_message += " " + er
                if not ('relation "tenants_tenant" does not exist' in error_message):
                    raise

            settings.DATABASES ['default'] = default_config

            for tenant_obj in tenants_list:
                t_name = tenant_obj[1]
                new_config = default_config.copy()
                new_config['NAME'] = t_name
                if t_name == 'default':
                    print('Can not be named default')
                    return
                settings.DATABASES[t_name] = new_config
                self.drop_create_db(new_config, root_dir)
                self.migrate_db(t_name)

            self.drop_create_db(default_config, root_dir)
            self.re_init_migrations()

            self.migrate_db('default')


            for tenant_obj in tenants_list:
                t_name = tenant_obj[1]
                if not Tenant.objects.filter(name=t_name):
                    Tenant.objects.create(name=t_name)

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
