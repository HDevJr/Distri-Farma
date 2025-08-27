from django.apps import AppConfig

class VendasConfig(AppConfig):
    name = 'vendas'

    def ready(self):
        import vendas.signals
