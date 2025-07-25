
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria os grupos padrão do sistema.'

    def handle(self, *args, **options):
        grupos = [
            'ADMINISTRADOR',
            'ATENDENTE ADMINISTRATIVO',
            'FISCAL',
            'TAXISTA',
            'MOTOTAXISTA',
            'MOTOTRISTACONDUTOR',
        ]
        for nome in grupos:
            grupo, criado = Group.objects.get_or_create(name=nome)
            if criado:
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{nome}" criado.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Grupo "{nome}" já existe.')
                )
