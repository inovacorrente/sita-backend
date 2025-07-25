
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from app_usuarios.utils import gerar_grupos_padrao


class Command(BaseCommand):
    help = 'Cria os grupos padrão do sistema.'

    def handle(self, *args, **options):
        grupos = gerar_grupos_padrao()
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
