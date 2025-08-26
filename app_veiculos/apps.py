from django.apps import AppConfig


class AppVeiculosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_veiculos'

    def ready(self):
        """
        Importa os sinais quando a aplicação está pronta.
        """
        import app_veiculos.signals  # noqa: F401
