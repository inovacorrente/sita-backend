import random
from datetime import date, timedelta

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from app_condutores.models import Condutor
from app_usuarios.models import UsuarioCustom


class Command(BaseCommand):
    help = (
        "Gera condutores para usuários já existentes no grupo CONDUTOR.\n"
        "- Prioriza somente usuários existentes e que ainda não são "
        "condutores.\n"
        "- Se houver menos usuários disponíveis que a quantidade pedida, "
        "serão gerados apenas para os disponíveis (sem erro).\n"
        "- Opcionalmente, use --criar-usuarios para completar a quantidade.\n"
        "Uso: python manage.py gerar_condutores --quantidade 10 "
        "[--criar-usuarios]"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade', type=int, default=10,
            help='Quantidade de condutores a serem gerados.'
        )
        parser.add_argument(
            '--criar-usuarios', action='store_true', dest='criar_usuarios',
            help=(
                'Cria usuários do grupo CONDUTOR caso não existam '
                'suficientes para atingir a quantidade.'
            )
        )

    def handle(self, *args, **options):
        faker = Faker('pt_BR')
        quantidade = options['quantidade']
        criar_usuarios = options['criar_usuarios']

        # Garantir existência do grupo CONDUTOR
        try:
            grupo_condutor = Group.objects.get(name='CONDUTOR')
        except Group.DoesNotExist:
            raise CommandError(
                'Grupo CONDUTOR não encontrado. Execute o comando que cria '
                'os grupos.'
            )

        # Apenas usuários do grupo CONDUTOR que ainda não são condutores
        elegiveis_qs = (
            UsuarioCustom.objects
            .filter(groups=grupo_condutor, condutor__isnull=True)
            .order_by('?')  # aleatoriza seleção
        )

        disponiveis = elegiveis_qs.count()
        if disponiveis == 0 and not criar_usuarios:
            self.stdout.write(self.style.WARNING(
                'Nenhum usuário disponível no grupo CONDUTOR sem vínculo de '
                'Condutor.'
            ))
            return

        alvo_iniciais = list(elegiveis_qs[:quantidade])

        if len(alvo_iniciais) < quantidade and not criar_usuarios:
            self.stdout.write(self.style.WARNING(
                'Quantidade solicitada maior que a quantidade de usuários '
                'disponíveis. Gerando apenas para os elegíveis.'
            ))

        # Completar com criação de usuários (opcional)
        novos_usuarios = []
        while criar_usuarios and (
            len(alvo_iniciais) + len(novos_usuarios)
        ) < quantidade:
            nome = faker.name()
            cpf = faker.cpf().replace('.', '').replace('-', '')
            email = faker.unique.email()
            data_nascimento = faker.date_of_birth(
                minimum_age=18,
                maximum_age=70
            )
            telefone = faker.msisdn()[:11]

            u = UsuarioCustom.objects.create_user(
                email=email,
                nome_completo=nome,
                cpf=cpf,
                data_nascimento=data_nascimento,
                telefone=telefone,
                password='12345678'
            )
            u.groups.add(grupo_condutor)
            novos_usuarios.append(u)

        usuarios_alvo = alvo_iniciais + novos_usuarios

        criados = 0
        for usuario in usuarios_alvo:
            # Garantia extra: pular se já tiver condutor (concorrência)
            if Condutor.objects.filter(usuario=usuario).exists():
                self.stdout.write(self.style.WARNING(
                    f"Usuário {usuario.matricula} já é condutor. Pulando."
                ))
                continue

            categoria = random.choice(['A', 'B', 'C', 'D', 'E', 'AD'])
            emissao = faker.date_between(start_date='-10y', end_date='-1y')
            validade = emissao + timedelta(
                days=random.randint(365, 5 * 365)
            )
            if validade < date.today():
                validade = date.today() + timedelta(
                    days=random.randint(30, 365)
                )

            Condutor.objects.create(
                usuario=usuario,
                categoria_cnh=categoria,
                data_emissao_cnh=emissao,
                data_validade_cnh=validade,
            )
            criados += 1

        self.stdout.write(self.style.SUCCESS(
            'Condutores gerados com sucesso: '
            f'{criados} (solicitado: {quantidade}).'
        ))
