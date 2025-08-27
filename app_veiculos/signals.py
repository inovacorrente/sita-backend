"""
Sinais (signals) para o app de veículos do sistema SITA.
Contém handlers para limpeza automática de arquivos e outras operações.
"""
import logging
import os

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import BannerIdentificacao


@receiver(pre_delete, sender=BannerIdentificacao)
def remove_banner_files_on_delete(sender, instance, **kwargs):
    """
    Remove arquivos de banner e pasta vazia quando o objeto BannerIdentificacao
    é deletado. Este sinal garante que os arquivos sejam removidos mesmo em
    operações de delete em batch (como queryset.delete()).
    """
    logger = logging.getLogger(__name__)

    if instance.arquivo_banner:
        try:
            arquivo_path = instance.arquivo_banner.path
            if os.path.exists(arquivo_path):
                # Obter diretório do arquivo antes de removê-lo
                diretorio = os.path.dirname(arquivo_path)

                # Remover o arquivo
                os.remove(arquivo_path)
                logger.info(
                    f"Arquivo de banner removido via signal: {arquivo_path}"
                )

                # Tentar remover o diretório se estiver vazio
                try:
                    if (os.path.exists(diretorio) and
                            not os.listdir(diretorio)):
                        os.rmdir(diretorio)
                        logger.info(
                            f"Diretório vazio removido via signal: {diretorio}"
                        )
                except OSError as e:
                    logger.debug(
                        f"Não foi possível remover diretório via signal "
                        f"{diretorio}: {e}"
                    )

        except (ValueError, FileNotFoundError) as e:
            logger.warning(
                f"Erro ao remover arquivo de banner via signal: {e}"
            )
