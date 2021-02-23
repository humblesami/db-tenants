from django.core.management.commands.migrate import Command as MigrationCommand


class Command(MigrationCommand):
    def handle(self, *args, **options):
        res = super().handle(args, options)
        return res
