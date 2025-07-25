
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from faker import Faker

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuários e associa aos grupos informados.'

    def handle(self, *args, **options):
        fake = Faker('pt_BR')
        admin_email = 'admin@exemplo.com'
        if not User.objects.filter(email=admin_email).exists():
            usuarios_para_criar = [
                {
                    'email': admin_email,
                    'nome_completo': 'Administrador do Sistema',
                    'cpf': fake.unique.cpf().replace('.', '').replace('-', ''),
                    'telefone': '11999999999',
                    'password': 'admin123',
                    'grupos': ['ADMINISTRADOR'],
                    'is_superuser': True,
                    'is_staff': True
                }
            ]
        else:
            usuarios_para_criar = []
            self.stdout.write(self.style.WARNING(f'Usuário admin já existe.'))
        grupos_faker = [
            'FISCAL',
            'ATENDENTE ADMINISTRATIVO',
            'ADMINISTRADOR',
            'TAXISTA',
            'MOTOTAXISTA',
            'MOTOTRISTACONDUTOR',
        ]
        # Cria apenas usuários fake
        for grupo in grupos_faker:
            for i in range(2):
                nome = fake.name()
                email = fake.unique.email()
                cpf = fake.unique.cpf().replace('.', '').replace('-', '')
                telefone = fake.phone_number()[:15]
                usuarios_para_criar.append({
                    'email': email,
                    'nome_completo': nome,
                    'cpf': cpf,
                    'telefone': telefone,
                    'password': 'senha123',
                    'grupos': [grupo]
                })

        for dados in usuarios_para_criar:
            grupos = dados.pop('grupos', [])
            password = dados.pop('password')
            is_superuser = dados.pop('is_superuser', False)
            is_staff = dados.pop('is_staff', False)

            # Verifica unicidade de e-mail e CPF
            if User.objects.filter(email=dados['email']).exists():
                self.stdout.write(self.style.WARNING(
                    f'Usuário com e-mail {dados["email"]} já existe.'))
                continue
            if User.objects.filter(cpf=dados['cpf']).exists():
                self.stdout.write(self.style.WARNING(
                    f'Usuário com CPF {dados["cpf"]} já existe.'))
                continue

            # Gera matrícula manualmente antes de criar o usuário
            from app_usuarios.utils import gerar_matricula_para_usuario

            class TempUser:
                def __init__(self, grupos, email, nome_completo, is_superuser):
                    self._grupos = grupos
                    self.email = email
                    self.nome_completo = nome_completo
                    self.is_superuser = is_superuser

                @property
                def groups(self):
                    class GroupList:
                        def __init__(self, nomes):
                            self._nomes = nomes

                        def all(self):
                            class G:
                                def __init__(self, name):
                                    self.name = name
                            return [G(name) for name in self._nomes]
                    return GroupList(self._grupos)

            temp_user = TempUser(
                grupos, dados['email'], dados['nome_completo'], is_superuser)
            dados['matricula'] = gerar_matricula_para_usuario(temp_user, User)

            usuario = User.objects.create(
                email=dados['email'],
                nome_completo=dados['nome_completo'],
                cpf=dados['cpf'],
                telefone=dados['telefone'],
                matricula=dados['matricula']
            )
            usuario.set_password(password)
            usuario.is_superuser = is_superuser
            usuario.is_staff = is_staff
            usuario.save()
            self.stdout.write(self.style.SUCCESS(
                f'Usuário {usuario.email} criado.'))
            for nome_grupo in grupos:
                grupo, _ = Group.objects.get_or_create(name=nome_grupo)
                usuario.groups.add(grupo)
            usuario.save()
            self.stdout.write(self.style.SUCCESS(
                f'Grupos {grupos} associados ao usuário {usuario.email}.'))
