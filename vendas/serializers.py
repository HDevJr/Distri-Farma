from rest_framework import serializers
from .models import Venda, ItemVenda
from .models import Produto, Cliente
from produtos.serializers import ProdutoSerializer
from clientes.serializers import ClienteSerializer

class ItemVendaSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    produto_id = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(),
        source='produto',
        write_only=True
    )
    
    class Meta:
        model = ItemVenda
        fields = ['id', 'produto', 'produto_id', 'quantidade', 'valor_unitario']

class VendaSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        source='cliente',
        write_only=True
    )
    itens = ItemVendaSerializer(many=True)

    class Meta:
        model = Venda
        fields = ['cod', 'cliente', 'cliente_id', 'data', 'itens']

