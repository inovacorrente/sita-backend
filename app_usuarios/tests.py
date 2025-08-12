from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class UsuarioCustomTests(TestCase):
    """
    Testes automatizados para o modelo de usuário customizado e autenticação JWT.

    Abrange os seguintes cenários:
    - Criação de usuário comum e superusuário
    - Garantia de unicidade de matrícula, e-mail e CPF
    - Autenticação via token JWT (login bem-sucedido, falhas por matrícula/senha inválida e usuário inativo)
    - Validação de restrições de campos obrigatórios

    Observação sobre erros:
    Os testes de autenticação que utilizam reverse('usuarios:token_obtain_pair') falham caso o namespace 'usuarios' não esteja registrado nas URLs do projeto.
    Para corrigir, utilize reverse('token_obtain_pair') ou registre o namespace corretamente.
    """

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'teste@exemplo.com',
            'nome_completo': 'Usuário Teste',
            'data_nascimento': '2000-01-01',
            'cpf': '11111111111',
            'password': 'senha123'
        }
        # Cria um usuário padrão para os testes
        self.usuario = User.objects.create_user(**self.user_data)

    def test_criacao_usuario(self):
        """
        Testa a criação de um usuário comum.
        Verifica se os campos essenciais estão corretos e se a matrícula é gerada automaticamente.
        """
        self.assertEqual(self.usuario.email, self.user_data['email'])
        self.assertTrue(self.usuario.check_password(self.user_data['password']))
        self.assertFalse(self.usuario.is_staff)
        self.assertFalse(self.usuario.is_superuser)
        self.assertIsNotNone(self.usuario.matricula)

    def test_criacao_superusuario(self):
        """
        Testa a criação de um superusuário.
        Verifica se as flags de superusuário e staff estão ativadas.
        """
        admin = User.objects.create_superuser(
            email='admin@exemplo.com',
            nome_completo='Administrador',
            data_nascimento='2000-01-01',
            password='admin123'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_matricula_unica(self):
        """
        Testa se a matrícula gerada é única entre dois usuários distintos.
        """
        outro_usuario = User.objects.create_user(
            email='outro@exemplo.com',
            nome_completo='Outro Usuário',
            data_nascimento='2000-01-01',
            cpf='22222222222',
            password='senha456'
        )
        self.assertNotEqual(self.usuario.matricula, outro_usuario.matricula)

    def test_email_unico(self):
        """
        Testa se o sistema impede a criação de usuários com e-mail duplicado, levantando exceção.
        """
        with self.assertRaises(Exception):
            User.objects.create_user(
                email=self.user_data['email'],
                nome_completo='Outro',
                data_nascimento='2000-01-01',
                cpf='33333333333',
                password='123'
            )

    def test_cpf_unico(self):
        """
        Testa se o sistema impede a criação de usuários com CPF duplicado, levantando exceção.
        """
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='novo@exemplo.com',
                nome_completo='Outro',
                data_nascimento='2000-01-01',
                cpf=self.user_data['cpf'],
                password='123'
            )

    def test_login_sucesso_token(self):
        """
        Testa se o login via Token JWT retorna sucesso e os tokens de acesso/refresh quando as credenciais estão corretas.
        Observação: Falha se o namespace 'usuarios' não estiver registrado nas URLs.
        """
        url = reverse('token_obtain_pair')
        data = {
            'matricula': self.usuario.matricula,
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data['data'])
        self.assertIn('refresh_token', response.data['data'])

    def test_login_falha_matricula_invalida(self):
        """
        Testa se o login falha quando a matrícula informada não existe.
        Observação: Falha se o namespace 'usuarios' não estiver registrado nas URLs.
        """
        url = reverse('token_obtain_pair')
        data = {
            'matricula': 'matricula-invalida',
            'password': 'senha123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_falha_senha_errada(self):
        """
        Testa se o login falha quando a senha está incorreta.
        Observação: Falha se o namespace 'usuarios' não estiver registrado nas URLs.
        """
        url = reverse('token_obtain_pair')
        data = {
            'matricula': self.usuario.matricula,
            'password': 'senha_errada'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_usuario_inativo(self):
        """
        Testa se um usuário inativo não consegue autenticar via JWT.
        Observação: Falha se o namespace 'usuarios' não estiver registrado nas URLs.
        """
        self.usuario.is_active = False
        self.usuario.save()

        url = reverse('token_obtain_pair')
        data = {
            'matricula': self.usuario.matricula,
            'password': self.user_data['password']
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
