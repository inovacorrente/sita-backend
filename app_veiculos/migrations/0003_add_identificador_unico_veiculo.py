# Generated manually to add identificador_unico_veiculo field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_veiculos', '0002_banneridentificacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='banneridentificacao',
            name='identificador_unico_veiculo',
            field=models.CharField(
                blank=True,
                db_index=True,
                editable=False,
                help_text='Identificador único do veículo',
                max_length=8,
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='banneridentificacao',
            name='object_id',
            field=models.PositiveIntegerField(
                blank=True,
                editable=False,
                help_text='ID do veículo (campo legado para compatibilidade)',
                null=True
            ),
        ),
    ]
