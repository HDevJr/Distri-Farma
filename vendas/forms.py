from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from .models import Venda, ItemVenda
from produtos.models import Produto
from collections import defaultdict
from django.forms import ValidationError
from django_select2.forms import Select2Widget

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = ['cliente']


class ItemVendaForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = ['produto', 'quantidade', 'valor_unitario', 'desconto_aplicado']
        widgets = {
            'produto': Select2Widget,
            'quantidade': forms.NumberInput(attrs={
                'class': 'sem-setas form-control',
                'inputmode': 'numeric',
            }),
            'valor_unitario': forms.NumberInput(attrs={
                'readonly': True,
                'class': 'sem-setas form-control bg-light',
                'tabindex': '-1',
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor_unitario'].widget.attrs['readonly'] = True

class BaseItemVendaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_itens = 0
        contagem_por_produto = defaultdict(int)

        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue

            produto = form.cleaned_data.get('produto')
            nova_qtde = form.cleaned_data.get('quantidade')
            valor_unitario = form.cleaned_data.get('valor_unitario')

            if not produto:
                form.add_error('produto', 'Selecione um produto.')
                continue
            if nova_qtde is None:
                form.add_error('quantidade', 'Informe a quantidade.')
                continue
            if not valor_unitario or valor_unitario <= 0:
                form.add_error('valor_unitario', 'Valor unitário inválido.')
                continue

            qtde_antiga = 0
            produto_antigo = produto
            if form.instance.pk:
                try:
                    item_antigo = ItemVenda.objects.get(pk=form.instance.pk)
                    qtde_antiga = item_antigo.quantidade
                    produto_antigo = item_antigo.produto
                except ItemVenda.DoesNotExist:
                    pass

            if produto == produto_antigo:
                estoque_disponivel = produto.quantidade_estoque + qtde_antiga
            else:
                estoque_disponivel = produto.quantidade_estoque

            contagem_por_produto[produto.pk] += nova_qtde

            if contagem_por_produto[produto.pk] > estoque_disponivel:
                form.add_error(
                    'quantidade',
                    f'Estoque insuficiente. Disponível: {estoque_disponivel}'
                )

            total_itens += 1

        if total_itens == 0:
            raise ValidationError("Corrija o campo")

ItemVendaFormSet = inlineformset_factory(
    Venda,
    ItemVenda,
    form=ItemVendaForm,
    formset=BaseItemVendaFormSet,
    extra=1,
    can_delete=True
)