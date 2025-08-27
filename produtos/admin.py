from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('produto_id', 'nome', 'ean', 'quantidade_estoque', 'valor_unitario')
