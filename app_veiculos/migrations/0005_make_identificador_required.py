# Generated manually to make identificador_unico_veiculo non-nullable
# and add unique_together constraint

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_veiculos', '0004_populate_identificador_unico_veiculo'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banneridentificacao',
            name='identificador_unico_veiculo',
            field=models.CharField(
                db_index=True,
                editable=False,
                help_text='Identificador único do veículo',
                max_length=8
            ),
        ),
        migrations.AlterUniqueTogether(
            name='banneridentificacao',
            unique_together={('content_type', 'identificador_unico_veiculo')},
        ),
    ]
