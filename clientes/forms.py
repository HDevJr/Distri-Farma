from django import forms
from .models import Cliente
import re

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = {'cod'}
        fields = ['nome', 'telefone','documento' ,'email', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_documento(self):
        doc = self.cleaned_data.get('documento') or ''
        doc = ''.join(filter(str.isdigit, doc))

        if not doc:
            raise forms.ValidationError("Documento obrigatório.")

        if len(doc) == 11 or len(doc) == 14:
            return doc  # CPF ou CNPJ limpo
        raise forms.ValidationError("Informe um CPF ou CNPJ válido.")

    def save(self, commit=True):
        if not self.instance.pk:
            ultimo_cliente = Cliente.objects.order_by('-cod').first()
            ultimo_cod = int(ultimo_cliente.cod) if ultimo_cliente and ultimo_cliente.cod else 0
            self.instance.cod = ultimo_cod + 1
        return super().save(commit)