"""
Comando para gerar dados fake de veículos usando Faker.
Cria dados de teste para táxi, mototáxi e transporte municipal.
"""
import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from app_usuarios.models import UsuarioCustom
from app_veiculos.models import (MotoTaxiVeiculo, TaxiVeiculo,
                                 TransporteMunicipalVeiculo)

fake = Faker('pt_BR')  # Usar localização brasileira


class Command(BaseCommand):
    """
    Comando para criar dados fake de veículos.

    Uso:
        python manage.py criar_veiculos_fake --quantidade 10
        python manage.py criar_veiculos_fake --taxis 5 --mototaxis 3 \
            --transporte 2
    """

    help = 'Cria dados fake de veículos para testes'

    def add_arguments(self, parser):
        """Define argumentos do comando."""
        parser.add_argument(
            '--quantidade',
            type=int,
            default=10,
            help='Quantidade total de veículos a criar (distribuído)'
        )
        parser.add_argument(
            '--taxis',
            type=int,
            help='Quantidade específica de táxis'
        )
        parser.add_argument(
            '--mototaxis',
            type=int,
            help='Quantidade específica de mototáxis'
        )
        parser.add_argument(
            '--transporte',
            type=int,
            help='Quantidade específica de veículos de transporte municipal'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Remove todos os veículos existentes antes de criar novos'
        )

    def handle(self, *args, **options):
        """Executa o comando."""
        self.stdout.write(
            self.style.SUCCESS(
                '🚗 Iniciando criação de dados fake de veículos...'
            )
        )

        # Limpar dados existentes se solicitado
        if options['clear']:
            self.clear_veiculos()

        # Verificar se existem usuários
        usuarios = list(UsuarioCustom.objects.all())
        if not usuarios:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Nenhum usuário encontrado! '
                    'Execute o comando criar_usuarios_fake primeiro.'
                )
            )
            return

        # Definir quantidades
        if options['taxis'] or options['mototaxis'] or options['transporte']:
            # Quantidades específicas
            qtd_taxis = options['taxis'] or 0
            qtd_mototaxis = options['mototaxis'] or 0
            qtd_transporte = options['transporte'] or 0
        else:
            # Distribuir igualmente
            total = options['quantidade']
            qtd_taxis = total // 3
            qtd_mototaxis = total // 3
            qtd_transporte = total - qtd_taxis - qtd_mototaxis

        # Criar veículos
        with transaction.atomic():
            created_taxis = self.criar_taxis(usuarios, qtd_taxis)
            created_mototaxis = self.criar_mototaxis(usuarios, qtd_mototaxis)
            created_transporte = self.criar_transporte_municipal(
                usuarios, qtd_transporte
            )

        # Relatório final
        total_criados = created_taxis + created_mototaxis + created_transporte
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Criados {total_criados} veículos com sucesso!\n'
                f'   📋 Táxis: {created_taxis}\n'
                f'   🏍️  Mototáxis: {created_mototaxis}\n'
                f'   🚌 Transporte Municipal: {created_transporte}'
            )
        )

    def clear_veiculos(self):
        """Remove todos os veículos existentes."""
        self.stdout.write('🗑️  Removendo veículos existentes...')

        deleted_taxi = TaxiVeiculo.objects.count()
        deleted_mototaxi = MotoTaxiVeiculo.objects.count()
        deleted_transporte = TransporteMunicipalVeiculo.objects.count()

        TaxiVeiculo.objects.all().delete()
        MotoTaxiVeiculo.objects.all().delete()
        TransporteMunicipalVeiculo.objects.all().delete()

        total_deleted = deleted_taxi + deleted_mototaxi + deleted_transporte

        self.stdout.write(
            self.style.WARNING(
                f'🗑️  Removidos {total_deleted} veículos existentes'
            )
        )

    def criar_taxis(self, usuarios, quantidade):
        """Cria veículos de táxi."""
        if quantidade <= 0:
            return 0

        self.stdout.write(f'🚗 Criando {quantidade} táxis...')

        created = 0
        for _ in range(quantidade):
            try:
                usuario = random.choice(usuarios)

                taxi = TaxiVeiculo.objects.create(
                    usuario=usuario,
                    placa=self.gerar_placa(),
                    renavam=self.gerar_renavam(),
                    chassi=self.gerar_chassi(),
                    marca=self.escolher_marca_carro(),
                    modelo=self.escolher_modelo_carro(),
                    cor=self.escolher_cor(),
                    anoFabricacao=self.gerar_ano_fabricacao(),
                    anoLimiteFabricacao=self.gerar_ano_limite()
                )
                created += 1

                self.stdout.write(
                    f'   ✅ Táxi criado: {taxi.identificador_unico_veiculo} '
                    f'- {taxi.placa} ({usuario.nome_completo})'
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erro ao criar táxi: {str(e)}')
                )

        return created

    def criar_mototaxis(self, usuarios, quantidade):
        """Cria veículos de mototáxi."""
        if quantidade <= 0:
            return 0

        self.stdout.write(f'🏍️  Criando {quantidade} mototáxis...')

        created = 0
        for _ in range(quantidade):
            try:
                usuario = random.choice(usuarios)

                mototaxi = MotoTaxiVeiculo.objects.create(
                    usuario=usuario,
                    placa=self.gerar_placa(),
                    renavam=self.gerar_renavam(),
                    chassi=self.gerar_chassi(),
                    marca=self.escolher_marca_moto(),
                    modelo=self.escolher_modelo_moto(),
                    cor=self.escolher_cor(),
                    anoFabricacao=self.gerar_ano_fabricacao(),
                    anoLimiteFabricacao=self.gerar_ano_limite()
                )
                created += 1

                self.stdout.write(
                    f'   ✅ Mototáxi criado: '
                    f'{mototaxi.identificador_unico_veiculo} '
                    f'- {mototaxi.placa} ({usuario.nome_completo})'
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erro ao criar mototáxi: {str(e)}')
                )

        return created

    def criar_transporte_municipal(self, usuarios, quantidade):
        """Cria veículos de transporte municipal."""
        if quantidade <= 0:
            return 0

        self.stdout.write(f'🚌 Criando {quantidade} transportes municipais...')

        created = 0
        for _ in range(quantidade):
            try:
                usuario = random.choice(usuarios)

                transporte = TransporteMunicipalVeiculo.objects.create(
                    usuario=usuario,
                    placa=self.gerar_placa(),
                    renavam=self.gerar_renavam(),
                    chassi=self.gerar_chassi(),
                    marca=self.escolher_marca_onibus(),
                    modelo=self.escolher_modelo_onibus(),
                    cor=self.escolher_cor_onibus(),
                    anoFabricacao=self.gerar_ano_fabricacao(),
                    anoLimiteFabricacao=self.gerar_ano_limite(),
                    linha=self.gerar_linha_transporte(),
                    capacidade=self.gerar_capacidade()
                )
                created += 1

                self.stdout.write(
                    f'   ✅ Transporte criado: '
                    f'{transporte.identificador_unico_veiculo} '
                    f'- {transporte.placa} - Linha {transporte.linha} '
                    f'({usuario.nome_completo})'
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'   ❌ Erro ao criar transporte municipal: {str(e)}'
                    )
                )

        return created

    # ========================================================================
    # MÉTODOS AUXILIARES PARA GERAR DADOS
    # ========================================================================

    def gerar_placa(self):
        """Gera placa brasileira (Mercosul ou padrão antigo)."""
        if random.choice([True, False]):
            # Padrão Mercosul: AAA9A99
            chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            letras1 = ''.join(random.choices(chars, k=3))
            numero1 = random.randint(0, 9)
            letra2 = random.choice(chars)
            numeros2 = ''.join(random.choices('0123456789', k=2))
            return f"{letras1}{numero1}{letra2}{numeros2}"
        else:
            # Padrão antigo: AAA-9999
            letras = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
            numeros = ''.join(random.choices('0123456789', k=4))
            return f"{letras}{numeros}"

    def gerar_renavam(self):
        """Gera RENAVAM de 11 dígitos."""
        return ''.join(random.choices('0123456789', k=11))

    def gerar_chassi(self):
        """Gera chassi de 17 caracteres."""
        chars = 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789'  # Exclui I, O, Q
        return ''.join(random.choices(chars, k=17))

    def gerar_ano_fabricacao(self):
        """Gera ano de fabricação entre 2000 e ano atual."""
        ano_atual = datetime.now().year
        return random.randint(2000, ano_atual)

    def gerar_ano_limite(self):
        """Gera ano limite baseado no ano de fabricação."""
        return random.randint(2025, 2035)

    def escolher_marca_carro(self):
        """Escolhe marca aleatória de carro."""
        marcas = [
            'Toyota', 'Honda', 'Chevrolet', 'Ford', 'Volkswagen',
            'Hyundai', 'Nissan', 'Fiat', 'Renault', 'Peugeot',
            'Citroën', 'Kia', 'Mitsubishi', 'Suzuki', 'Chery'
        ]
        return random.choice(marcas)

    def escolher_modelo_carro(self):
        """Escolhe modelo aleatório de carro."""
        modelos = [
            'Corolla', 'Civic', 'Onix', 'Ka', 'Gol',
            'HB20', 'March', 'Uno', 'Sandero', '208',
            'C3', 'Picanto', 'Lancer', 'Swift', 'QQ'
        ]
        return random.choice(modelos)

    def escolher_marca_moto(self):
        """Escolhe marca aleatória de moto."""
        marcas = [
            'Honda', 'Yamaha', 'Suzuki', 'Kawasaki', 'BMW',
            'Ducati', 'Harley-Davidson', 'Triumph', 'KTM', 'Aprilia'
        ]
        return random.choice(marcas)

    def escolher_modelo_moto(self):
        """Escolhe modelo aleatório de moto."""
        modelos = [
            'CG 160', 'XRE 300', 'CB 600F', 'YZF-R3', 'GSX-R750',
            'Ninja 300', 'R1250GS', 'Panigale V4', 'Street 750', 'Bonneville'
        ]
        return random.choice(modelos)

    def escolher_marca_onibus(self):
        """Escolhe marca aleatória de ônibus."""
        marcas = [
            'Mercedes-Benz', 'Volvo', 'Scania', 'Iveco', 'MAN',
            'Volkswagen', 'Agrale', 'Ford'
        ]
        return random.choice(marcas)

    def escolher_modelo_onibus(self):
        """Escolhe modelo aleatório de ônibus."""
        modelos = [
            'Sprinter', 'B270F', '270 Bluetec 5', 'Daily', 'VW 17.230',
            'Volksbus 17.260', 'Agrale MA 10.0', 'Transit'
        ]
        return random.choice(modelos)

    def escolher_cor(self):
        """Escolhe cor aleatória."""
        cores = [
            'Branco', 'Prata', 'Preto', 'Azul', 'Vermelho',
            'Cinza', 'Bege', 'Marrom', 'Verde', 'Amarelo',
            'Dourado', 'Roxo', 'Rosa', 'Laranja'
        ]
        return random.choice(cores)

    def escolher_cor_onibus(self):
        """Escolhe cor típica de ônibus."""
        cores = [
            'Branco', 'Azul', 'Verde', 'Amarelo', 'Vermelho',
            'Laranja', 'Cinza', 'Prata'
        ]
        return random.choice(cores)

    def gerar_linha_transporte(self):
        """Gera linha de transporte municipal."""
        linhas = [
            'Linha 001 - Centro/Bairro A',
            'Linha 002 - Shopping/Bairro B',
            'Linha 003 - Hospital/Bairro C',
            'Linha 004 - Universidade/Bairro D',
            'Linha 005 - Aeroporto/Centro',
            'Linha 006 - Rodoviária/Bairro E',
            'Linha 007 - Circular Centro',
            'Linha 008 - Industrial/Residencial',
            'Linha 009 - Escolar Zona Norte',
            'Linha 010 - Escolar Zona Sul'
        ]
        return random.choice(linhas)

    def gerar_capacidade(self):
        """Gera capacidade do veículo de transporte."""
        capacidades = [20, 25, 30, 35, 40, 45, 50, 60, 70, 80]
        return random.choice(capacidades)
