from django.contrib.auth.models import User
from django.db import models
from django.db.utils import ConnectionDoesNotExist, ConnectionHandler


class CustomConnectionHandler(ConnectionHandler):
    def ensure_defaults(self, alias):
        """
        Put the defaults into the settings dictionary for a given connection
        where no settings is provided.
        """
        try:
            conn = self.databases[alias]
        except KeyError:
            raise ConnectionDoesNotExist("The connection---- %s doesn't exist" % alias)

        conn.setdefault('ATOMIC_REQUESTS', False)
        conn.setdefault('AUTOCOMMIT', True)
        conn.setdefault('ENGINE', 'django.db.backends.dummy')
        if conn['ENGINE'] == 'django.db.backends.' or not conn['ENGINE']:
            conn['ENGINE'] = 'django.db.backends.dummy'
        conn.setdefault('CONN_MAX_AGE', 0)
        conn.setdefault('OPTIONS', {})
        conn.setdefault('TIME_ZONE', None)
        for setting in ['NAME', 'USER', 'PASSWORD', 'HOST', 'PORT']:
            conn.setdefault(setting, '')


class DefaultClass(models.Model):
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_query_name='%(app_label)s_%(class)s_created_by',
        related_name='%(app_label)s_%(class)s_created_by'
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='%(app_label)s_%(class)s_updated_by',
        related_query_name='%(app_label)s_%(class)s_updated_by'
    )

    class Meta:
        abstract = True
