from django.db import models
from django.core.validators import MinValueValidator


class Produto(models.Model):
    produto_id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    ean = models.CharField(max_length=13, unique=True)
    quantidade_estoque = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Valor Unitário"
    )
    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome

produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT, null=True, blank=True)
