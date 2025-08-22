"""
Comando para regenerar todos os banners com a nova estrutura de diretórios.
"""
from django.core.management.base import BaseCommand

from app_veiculos.models import BannerIdentificacao


class Command(BaseCommand):
    help = 'Regenera todos os banners com a nova estrutura de diretórios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simula a regeneração sem salvar arquivos',
        )

    def handle(self, *args, **options):
        """Executa a regeneração dos banners."""

        dry_run = options['dry_run']

        self.stdout.write("\n=== REGENERAÇÃO DE BANNERS ===")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "MODO DRY-RUN - Nenhum arquivo será gerado"
                )
            )

        banners = BannerIdentificacao.objects.all()
        total_banners = banners.count()

        self.stdout.write(f"Total de banners: {total_banners}")

        if total_banners == 0:
            self.stdout.write("Nenhum banner encontrado.")
            return

        regenerados = 0
        erros = 0

        for banner in banners:
            try:
                veiculo = banner.get_veiculo()
                if not veiculo:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Banner {banner.id}: Veículo não encontrado"
                        )
                    )
                    erros += 1
                    continue

                identificador = veiculo.identificador_unico_veiculo
                self.stdout.write(
                    f"Regenerando banner {banner.id} "
                    f"({veiculo.placa} - {identificador})"
                )

                if not dry_run:
                    # Regenerar o banner (isso vai usar a nova estrutura)
                    banner.gerar_banner()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Arquivo salvo em: "
                            f"{banner.arquivo_banner.name}"
                        )
                    )
                else:
                    self.stdout.write("  [DRY-RUN] Seria regenerado")

                regenerados += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Erro ao regenerar banner {banner.id}: {e}"
                    )
                )
                erros += 1

        self.stdout.write("\n=== RESUMO REGENERAÇÃO ===")
        self.stdout.write(f"Total de banners: {total_banners}")
        self.stdout.write(f"Regenerados: {regenerados}")
        self.stdout.write(f"Erros: {erros}")

        if not dry_run and regenerados > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {regenerados} banners regenerados com sucesso"
                )
            )
        elif dry_run and regenerados > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Execute sem --dry-run para regenerar "
                    f"{regenerados} banners"
                )
            )

        self.stdout.write("\n=== FIM REGENERAÇÃO ===\n")
        self.stdout.write("\n=== FIM REGENERAÇÃO ===\n")
