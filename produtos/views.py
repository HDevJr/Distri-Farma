from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Produto
from .forms import ProdutoForm
from .serializers import ProdutoSerializer
from .permissions import IsAdminOrReadOnly
from django.shortcuts import render, redirect, get_object_or_404
from produtos.models import Produto
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.db import IntegrityError

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

def produto_list(request):
    termo = request.GET.get('q', '').strip()

    if termo:
        lista = Produto.objects.filter(
            Q(nome__icontains=termo) | Q(produto_id__icontains=termo)
        ).order_by('nome')
    else:
        lista = Produto.objects.all().order_by('nome')

    paginator = Paginator(lista, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'produtos/produtos.html', {'page_obj': page_obj, 'termo': termo})


@login_required
def produto_add(request):
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        messages.error(request, "Você não tem permissão para cadastrar produtos.")
        return redirect('produto_list')
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso.')
            return redirect('produto_list')
    else:
        form = ProdutoForm()
    return render(request, 'produtos/produto_form.html', {'form': form, 'titulo': 'Adicionar Produto'})


def produto_edit(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto editado com sucesso.')
            return redirect('produto_list')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'produtos/produto_form.html', {'form': form, 'titulo': 'Editar Produto'})

def produto_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        try:
            produto.delete()
            messages.success(request, 'Produto excluído com sucesso.')
        except (ProtectedError, IntegrityError):
            messages.error(request, 'Não é possível excluir: Há vendas/orçamentos usando este produto.')
        return redirect('produto_list')
    return render(request, 'produtos/produto_confirm_delete.html', {'produto': produto})

def valor_unitario_view(request):
    produto_id = request.GET.get('produto_id')
    try:
        produto = Produto.objects.get(produto_id=produto_id)
        return JsonResponse({'valor_unitario': float(produto.valor_unitario)})
    except Produto.DoesNotExist:
        return JsonResponse({'erro': 'Produto não encontrado'}, status=404)