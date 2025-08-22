# Generated manually to populate identificador_unico_veiculo field

from django.db import migrations


def populate_identificador_unico_veiculo(apps, schema_editor):
    """
    Popula o campo identificador_unico_veiculo para registros existentes
    baseado no veiculo associado via GenericForeignKey.
    """
    BannerIdentificacao = apps.get_model('app_veiculos', 'BannerIdentificacao')

    banners = BannerIdentificacao.objects.filter(
        identificador_unico_veiculo__isnull=True
    )

    for banner in banners:
        if banner.content_type and banner.object_id:
            try:
                # Obter o modelo do veículo
                model_class = banner.content_type.model_class()
                veiculo = model_class.objects.get(id=banner.object_id)

                # Atualizar o identificador único
                if hasattr(veiculo, 'identificador_unico_veiculo'):
                    banner.identificador_unico_veiculo = (
                        veiculo.identificador_unico_veiculo
                    )
                    banner.save()
                    print(f"Banner {banner.id}: "
                          f"{veiculo.identificador_unico_veiculo}")

            except Exception as e:
                print(f"Erro ao processar banner {banner.id}: {e}")


def reverse_populate_identificador_unico_veiculo(apps, schema_editor):
    """
    Operação reversa: limpa o campo identificador_unico_veiculo.
    """
    BannerIdentificacao = apps.get_model('app_veiculos', 'BannerIdentificacao')
    BannerIdentificacao.objects.update(identificador_unico_veiculo=None)


class Migration(migrations.Migration):

    dependencies = [
        ('app_veiculos', '0003_add_identificador_unico_veiculo'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(
            populate_identificador_unico_veiculo,
            reverse_populate_identificador_unico_veiculo
        ),
    ]
