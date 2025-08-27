from django.db import models
from clientes.models import Cliente
from produtos.models import Produto

class Orcamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    convertido_em_venda = models.BooleanField(default=False)

    def __str__(self):
        return f"Orçamento #{self.pk} - {self.cliente}"
    
cliente = models.ForeignKey('clientes.Cliente',on_delete=models.SET_NULL, null=True, blank=True)

class ItemOrcamento(models.Model):
    orcamento = models.ForeignKey(Orcamento, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    desconto_aplicado = models.BooleanField(default=False)

    @property
    def total(self):
        total = self.quantidade * self.valor_unitario
        return total * (0.95 if self.desconto_aplicado else 1)
