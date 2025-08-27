from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Cliente
from .forms import ClienteForm
from .serializers import ClienteSerializer
from .permissions import IsAdminOrRepresentante
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.db import IntegrityError

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrRepresentante]


def cliente_list(request):
    termo = request.GET.get('q', '').strip()

    if termo:
        lista = Cliente.objects.filter(
            Q(nome__icontains=termo) | Q(cod__icontains=termo)
        ).order_by('nome')
    else:
        lista = Cliente.objects.all().order_by('nome')

    paginator = Paginator(lista, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
        'termo': termo,
    }
    return render(request, 'clientes/clientes.html', contexto)

def cliente_add(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, f'Cliente criado com sucesso.')
        return redirect('cliente_list')
    return render(request, 'clientes/cliente_form.html', {'form': form})

def cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente editado com sucesso.')
            return redirect('cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente'})



def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            cliente.delete()
            messages.success(request, 'Cliente excluído com sucesso.')
        except (ProtectedError, IntegrityError):
            messages.error(request, 'Não é possível excluir: Há vendas/orçamentos vinculados.')
        return redirect('cliente_list')
    return render(request, 'clientes/cliente_confirm_delete.html', {'cliente': cliente})