"""
Comando para corrigir URLs dos QR codes em banners existentes.
"""
from django.core.management.base import BaseCommand

from app_veiculos.models import BannerIdentificacao
from utils.commons.urls import get_veiculo_info_url


class Command(BaseCommand):
    help = 'Corrige URLs dos QR codes em banners existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simula as correções sem salvar',
        )
        parser.add_argument(
            '--regenerate-files',
            action='store_true',
            help='Regenera os arquivos de banner com QR code',
        )

    def handle(self, *args, **options):
        """Executa a correção das URLs."""

        dry_run = options['dry_run']
        regenerate_files = options['regenerate_files']

        self.stdout.write("\n=== CORREÇÃO DE URLs ===")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "MODO DRY-RUN - Nenhuma alteração será salva"
                )
            )

        banners = BannerIdentificacao.objects.all()
        total_banners = banners.count()

        self.stdout.write(f"Total de banners encontrados: {total_banners}")

        if total_banners == 0:
            self.stdout.write("Nenhum banner encontrado.")
            return

        banners_corrigidos = 0
        banners_com_erro = 0

        for banner in banners:
            try:
                veiculo = banner.get_veiculo()
                if not veiculo:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Banner {banner.id}: Veículo não encontrado"
                        )
                    )
                    banners_com_erro += 1
                    continue

                # Gerar nova URL correta
                identificador = veiculo.identificador_unico_veiculo
                nova_url = get_veiculo_info_url(identificador)

                # Verificar se precisa correção
                if banner.qr_url != nova_url:
                    self.stdout.write(
                        f"Banner {banner.id} ({veiculo.placa}):"
                    )
                    self.stdout.write(f"  URL atual:  {banner.qr_url}")
                    self.stdout.write(f"  URL correta: {nova_url}")

                    if not dry_run:
                        banner.qr_url = nova_url

                        if regenerate_files:
                            self.stdout.write(
                                "  Regenerando arquivo do banner..."
                            )
                            banner.gerar_banner()
                        else:
                            banner.save()

                        self.stdout.write(
                            self.style.SUCCESS("  ✓ Corrigido")
                        )
                    else:
                        self.stdout.write("  [DRY-RUN] Seria corrigido")

                    banners_corrigidos += 1
                else:
                    self.stdout.write(
                        f"Banner {banner.id} ({veiculo.placa}): "
                        f"URL já está correta"
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Erro ao processar banner {banner.id}: {e}"
                    )
                )
                banners_com_erro += 1

        self.stdout.write("\n=== RESUMO ===")
        self.stdout.write(f"Total de banners: {total_banners}")
        self.stdout.write(f"Banners corrigidos: {banners_corrigidos}")
        self.stdout.write(f"Banners com erro: {banners_com_erro}")

        if not dry_run and banners_corrigidos > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {banners_corrigidos} banners foram corrigidos"
                )
            )
        elif dry_run and banners_corrigidos > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Execute sem --dry-run para corrigir "
                    f"{banners_corrigidos} banners"
                )
            )

        self.stdout.write("\n=== FIM CORREÇÃO ===\n")
        self.stdout.write("\n=== FIM CORREÇÃO ===\n")
