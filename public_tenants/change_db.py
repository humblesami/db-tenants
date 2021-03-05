import threading
from django.conf import settings

THREAD_LOCAL = threading.local()


def get_current_db_name():
    res = getattr(THREAD_LOCAL, "DB", None)
    return res


def set_db_for_router(db, default_config=None):
    dbs = settings.DATABASES
    if db and db != 'default' and db != dbs['default']['NAME']:
        if not default_config:
            default_config = dbs['default']
        if not dbs.get(db):
            tenant_config = default_config.copy()
            tenant_config['NAME'] = db
            dbs[db] = tenant_config
    setattr(THREAD_LOCAL, "DB", db)