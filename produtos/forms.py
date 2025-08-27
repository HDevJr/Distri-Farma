from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome',
            'descricao',
            'ean',
            'quantidade_estoque',
            'valor_unitario',
        ]

        def clean_valor_unitario(self):
            valor = self.cleaned_data.get('valor_unitario')
            if valor is None or valor <= 0:
                raise forms.ValidationError('O valor unitário deve ser maior que zero.')
            return valor