import sys
import traceback
from django.conf import settings
from django.core.management import call_command

from tenants.models import Tenant, TenantApp
from dj_utils.management.commands.reset import Command as ResetCommand


class Command(ResetCommand):

    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            default_config = settings.DATABASES['default']
            tenants_list = []
            try:
                query = "select id,name from tenants_tenant"
                tenants_tuple = self.exec_query_on_default(default_config, query, 1)

                for obj in tenants_tuple:
                    tenant_id_str = str(obj[0])
                    query = "select name from tenants_tenantapp where tenant_id="+tenant_id_str
                    apps_list = self.exec_query_on_default(default_config, query, 1)
                    app_names_list = []
                    for app in apps_list:
                        app_names_list.append(app[0])
                    tenant_dict_obj = {
                        'id': obj[0],
                        'name': obj[1],
                        'apps': app_names_list,
                    }
                    tenants_list.append(tenant_dict_obj)
            except:
                eg = traceback.format_exception(*sys.exc_info())
                error_message = ''
                cnt = 0
                for er in eg:
                    cnt += 1
                    if not 'lib/python' in er and not 'lib\site-packages' in er:
                        error_message += " " + er
                db_not_found = 'database "'+default_config['NAME']+'" does not exist' in error_message
                tenant_table_error = 'relation "tenants_tenant" does not exist' in error_message
                tenant_app_table_error = 'relation "tenants_tenant_app" does not exist' in error_message
                if not db_not_found and not tenant_table_error and not tenant_app_table_error:
                    raise

            settings.DATABASES ['default'] = default_config

            for tenant_dict_obj in tenants_list:
                t_name = tenant_dict_obj['name']
                new_config = default_config.copy()
                new_config['NAME'] = t_name
                if t_name == 'default':
                    print('Can not be named default')
                    return
                settings.DATABASES[t_name] = new_config
                self.drop_create_db(new_config, root_dir)
                tenant_apps = tenant_dict_obj['apps']
                self.migrate_db(t_name, tenant_apps)

            self.drop_create_db(default_config, root_dir)
            self.re_init_migrations()

            self.migrate_db('default')

            if len(tenants_list):
                for tenant_obj in tenants_list:
                    t_name = tenant_obj['name']
                    if not Tenant.objects.filter(name=t_name):
                        t_obj = Tenant.objects.create(name=t_name)
                        for app in tenant_obj['apps']:
                            TenantApp.objects.create(name=app, tenant_id=t_obj.id)
            else:
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
