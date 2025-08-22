"""
Comando de management para testar a geração de banners com URLs dinâmicas.
"""
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from app_veiculos.models import (BannerIdentificacao, MotoTaxiVeiculo,
                                 TaxiVeiculo, TransporteMunicipalVeiculo)


class Command(BaseCommand):
    help = 'Testa a geração de banners com URLs dinâmicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--identificador',
            type=str,
            help='Identificador específico do veículo para testar'
        )
        parser.add_argument(
            '--regenerar',
            action='store_true',
            help='Regenera banners existentes'
        )

    def handle(self, *args, **options):
        identificador = options.get('identificador')
        regenerar = options.get('regenerar', False)

        if identificador:
            # Testar veículo específico
            self.testar_veiculo_especifico(identificador, regenerar)
        else:
            # Testar todos os veículos
            self.testar_todos_veiculos(regenerar)

    def testar_veiculo_especifico(self, identificador, regenerar):
        """Testa geração de banner para veículo específico."""
        veiculo = None
        content_type = None

        # Buscar em todos os tipos de veículo
        for model_class in [TaxiVeiculo, MotoTaxiVeiculo,
                            TransporteMunicipalVeiculo]:
            try:
                veiculo = model_class.objects.get(
                    identificador_unico_veiculo=identificador
                )
                content_type = ContentType.objects.get_for_model(model_class)
                break
            except model_class.DoesNotExist:
                continue

        if not veiculo:
            self.stdout.write(
                self.style.ERROR(
                    f'Veículo {identificador} não encontrado'
                )
            )
            return

        # Verificar se já existe banner
        banner = BannerIdentificacao.objects.filter(
            content_type=content_type,
            object_id=veiculo.id
        ).first()

        if banner and not regenerar:
            self.stdout.write(
                self.style.WARNING(
                    f'Banner já existe para {identificador}. '
                    f'Use --regenerar para recriar.'
                )
            )
            self.mostrar_info_banner(banner)
            return

        # Criar ou regenerar banner
        if not banner:
            banner = BannerIdentificacao.objects.create(
                content_type=content_type,
                object_id=veiculo.id
            )
            action = 'criado'
        else:
            action = 'regenerado'

        try:
            banner.gerar_banner()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Banner {action} com sucesso para {identificador}'
                )
            )
            self.mostrar_info_banner(banner)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Erro ao gerar banner para {identificador}: {str(e)}'
                )
            )

    def testar_todos_veiculos(self, regenerar):
        """Testa geração de banners para todos os veículos."""
        total_veiculos = 0
        banners_criados = 0
        banners_regenerados = 0
        erros = 0

        for model_class in [TaxiVeiculo, MotoTaxiVeiculo,
                            TransporteMunicipalVeiculo]:
            veiculos = model_class.objects.all()[:5]  # Limitar para teste
            content_type = ContentType.objects.get_for_model(model_class)

            for veiculo in veiculos:
                total_veiculos += 1
                identificador = veiculo.identificador_unico_veiculo

                # Verificar se já existe banner
                banner = BannerIdentificacao.objects.filter(
                    content_type=content_type,
                    object_id=veiculo.id
                ).first()

                if banner and not regenerar:
                    self.stdout.write(f'  - {identificador}: Banner já existe')
                    continue

                # Criar ou regenerar banner
                if not banner:
                    banner = BannerIdentificacao.objects.create(
                        content_type=content_type,
                        object_id=veiculo.id
                    )
                    action = 'criado'
                    banners_criados += 1
                else:
                    action = 'regenerado'
                    banners_regenerados += 1

                try:
                    banner.gerar_banner()
                    self.stdout.write(
                        f'  ✓ {identificador}: Banner {action}'
                    )
                except Exception as e:
                    erros += 1
                    self.stdout.write(
                        f'  ✗ {identificador}: Erro - {str(e)}'
                    )

        # Resumo
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total de veículos processados: {total_veiculos}')
        self.stdout.write(f'Banners criados: {banners_criados}')
        self.stdout.write(f'Banners regenerados: {banners_regenerados}')
        self.stdout.write(f'Erros: {erros}')

    def mostrar_info_banner(self, banner):
        """Mostra informações detalhadas do banner."""
        veiculo = banner.veiculo
        identificador = veiculo.identificador_unico_veiculo
        proprietario = veiculo.usuario.get_full_name()
        arquivo = banner.arquivo_banner.name if banner.arquivo_banner else "N/A"

        self.stdout.write('\nDetalhes do Banner:')
        self.stdout.write(f'  - ID: {banner.id}')
        self.stdout.write(f'  - Veículo: {identificador}')
        self.stdout.write(f'  - Placa: {veiculo.placa}')
        self.stdout.write(f'  - Tipo: {veiculo.__class__.__name__}')
        self.stdout.write(f'  - Proprietário: {proprietario}')
        self.stdout.write(f'  - Arquivo: {arquivo}')
        self.stdout.write(f'  - QR URL: {banner.qr_url}')
        self.stdout.write(f'  - Ativo: {"Sim" if banner.ativo else "Não"}')
        self.stdout.write(f'  - Criado em: {banner.data_criacao}')
        self.stdout.write(f'  - Atualizado em: {banner.data_atualizacao}')
