from django.db import models
from django.db.models.signals import pre_save, post_delete
from clientes.models import Cliente
from produtos.models import Produto
from decimal import Decimal

class Venda(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    data = models.DateTimeField(auto_now_add=True)
    orcamento = models.ForeignKey('orcamentos.Orcamento', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=20,
        choices=[('rascunho','Rascunho'),('finalizada','Finalizada')],
        default='finalizada'
    )

    class Meta:
        ordering = ['cliente']

    @property
    def total(self):
        return sum(item.get_valor_total() for item in self.itens.all())

cliente = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True)

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    desconto_aplicado = models.BooleanField(default=False)

    class Meta:
        ordering = ['produto']

    def get_valor_total(self):
        total = self.quantidade * self.valor_unitario
        if self.desconto_aplicado:
            total *= Decimal('0.95')
        return total

    def valor_total(self):
        return self.quantidade * self.valor_unitario
    
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._produto_original = self.produto
    self._quantidade_original = self.quantidade

