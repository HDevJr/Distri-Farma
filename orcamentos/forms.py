from django import forms
from django.forms import inlineformset_factory
from .models import Orcamento, ItemOrcamento

class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = ["cliente"]

class ItemOrcamentoForm(forms.ModelForm):
    class Meta:
        model = ItemOrcamento
        fields = ["produto", "quantidade", "valor_unitario", "desconto_aplicado"]

ItensOrcamentoFormSet = inlineformset_factory(
    Orcamento, ItemOrcamento,
    form=ItemOrcamentoForm,
    extra=1, can_delete=True
)
