from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria os grupos padrão do sistema.'

    def handle(self, *args, **options):
        """
        Método principal executado quando o comando é chamado via terminal.

        Cria grupos padrão no sistema caso ainda não existam. Os grupos são:
        - FISCAL
        - ATENDENTE ADMINISTRATIVO
        - ADMINISTRADOR
        - TAXISTA
        - MOTOTAXISTA
        - MOTOTRISTACONDUTOR

        Para cada grupo:
        - Se o grupo não existir, será criado e uma mensagem de sucesso será exibida.
        - Se já existir, será exibida uma mensagem de aviso.
        """
        grupos = [
            'FISCAL',
            'ATENDENTE ADMINISTRATIVO',
            'ADMINISTRADOR',
            'TAXISTA',
            'MOTOTAXISTA',
            'MOTOTRISTACONDUTOR',
        ]

        # Itera sobre a lista de nomes de grupos
        for nome in grupos:
            grupo, criado = Group.objects.get_or_create(name=nome)
            if criado:
                # Mensagem de sucesso para grupo recém-criado
                self.stdout.write(
                    self.style.SUCCESS(f'Grupo "{nome}" criado.')
                )
            else:
                # Aviso caso o grupo já exista
                self.stdout.write(
                    self.style.WARNING(f'Grupo "{nome}" já existe.')
                )
