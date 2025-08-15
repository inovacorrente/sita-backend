from django.test import TestCase
from rest_framework.test import APIClient
from datetime import date

from app_usuarios.models import UsuarioCustom
from .models import Condutor


class CondutorModelTest(TestCase):
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
        self.usuario = UsuarioCustom.objects.create_user(**self.user_data)

    def test_create_condutor(self):
        # Cria uma instância de Condutor
        condutor = Condutor.objects.create(
            usuario=self.usuario,  # Campo obrigatório: associe o usuário criado no setUp
            categoria_cnh='B',
            data_validade_cnh=date(2025, 1, 1),
            data_emissao_cnh=date(2020, 1, 1)
        )

        # Verifica se o condutor foi criado corretamente
        self.assertEqual(condutor.usuario, self.usuario)
        self.assertEqual(condutor.categoria_cnh, 'B')
        self.assertEqual(condutor.data_validade_cnh, date(2025, 1, 1))
        self.assertEqual(condutor.data_emissao_cnh, date(2020, 1, 1))

        # Verifica se os campos automáticos foram preenchidos
        self.assertIsNotNone(condutor.data_criacao)
        self.assertIsNotNone(condutor.data_atualizacao)

        # Verifica o método __str__
        self.assertEqual(
            str(condutor),
            f'Condutor: {self.usuario.nome_completo} - {condutor.categoria_cnh}'
        )
