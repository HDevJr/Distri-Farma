from django.contrib import admin
from .models import Venda, ItemVenda

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    extra = 0

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'data', 'get_total']
    inlines = [ItemVendaInline]

    def get_total(self, obj):
        return obj.total
    get_total.short_description = 'Total'

@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'venda', 'produto', 'quantidade', 'valor_unitario', 'desconto_aplicado']
