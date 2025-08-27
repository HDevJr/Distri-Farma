from django.db import models
from django.db.models import Max

class Cliente(models.Model):
    cod = models.PositiveIntegerField(unique=True, editable=False)
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    documento = models.CharField(
        max_length=18,
        unique=True,
        null=True,
        blank=True,
        verbose_name="CPF ou CNPJ"
    )
    descricao = models.TextField(blank=True)

    @property
    def documento_formatado(self):
        val = ''.join(filter(str.isdigit, self.documento or ''))
        if len(val) == 11:
            return f'{val[:3]}.{val[3:6]}.{val[6:9]}-{val[9:]}'
        elif len(val) == 14:
            return f'{val[:2]}.{val[2:5]}.{val[5:8]}/{val[8:12]}-{val[12:]}'
        return self.documento

    class Meta:
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.cod:
            max_cod = Cliente.objects.aggregate(Max('cod'))['cod__max']
            self.cod = (max_cod or 0) + 1
        super().save(*args, **kwargs)

    @property
    def documento_formatado(self):
        doc = self.documento or ''
        if len(doc) == 11:
            return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
        elif len(doc) == 14:
            return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
        return doc

    def __str__(self):
        return self.nome
    