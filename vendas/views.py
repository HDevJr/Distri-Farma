import os

from .forms import VendaForm, ItemVendaFormSet
from .serializers import VendaSerializer
from .permissions import IsAdminOrRepresentanteVenda
from django.conf import settings
from django.http import HttpResponse
from django.templatetags.static import static
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Venda, ItemVenda
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from decimal import Decimal
from django.utils import timezone

class VendaViewSet(viewsets.ModelViewSet):
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrRepresentanteVenda]
    
def venda_list(request):
    query = request.GET.get('q', '')

    if query:
        vendas_queryset = Venda.objects.filter(
            Q(id__icontains=query) |
            Q(cliente__nome__icontains=query)
        )
    else:
        vendas_queryset = Venda.objects.all()

    paginator = Paginator(vendas_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query
    }
    return render(request, 'vendas/vendas.html', context)

def venda_detail(request, pk):
    venda = get_object_or_404(
        Venda.objects.select_related('cliente').prefetch_related('itens__produto'),
        pk=pk
    )
    return render(request, 'vendas/_venda_detail.html', {'venda': venda})

def venda_add(request):
    if request.method == 'POST':
        form = VendaForm(request.POST)
        formset = ItemVendaFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    venda = form.save(commit=False)
                    venda.save()

                    itens = formset.save(commit=False)
                    for obj in formset.deleted_objects:
                        obj.delete()
                    for item in itens:
                        item.venda = venda
                        item.save()
                        messages.success(request, 'Venda criada com sucesso.')
                return redirect('venda_list')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = VendaForm()
        formset = ItemVendaFormSet()
    return render(request, 'vendas/venda_form.html', {'form': form, 'formset': formset, 'titulo': 'Nova Venda'})   

def venda_edit(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    if request.method == 'POST':
        form = VendaForm(request.POST, instance=venda)
        formset = ItemVendaFormSet(request.POST, instance=venda)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    venda = form.save()
                    itens = formset.save(commit=False)

                    for obj in formset.deleted_objects:
                        obj.delete()

                    for item in itens:
                        item.venda = venda
                        item.save()
            except Exception as e:
                form.add_error(None, str(e))
            else:
                messages.success(request, 'Venda editada com sucesso.')
                return redirect('venda_list')
    else:
        form = VendaForm(instance=venda)
        formset = ItemVendaFormSet(instance=venda, queryset=ItemVenda.objects.filter(venda=venda))
        formset.extra = 0
    return render(request, 'vendas/venda_form.html', {
        'form': form, 'formset': formset, 'titulo': 'Editar Venda'
    })

def venda_delete(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    if request.method == 'POST':
        venda.delete()
        messages.success(request, 'Venda excluída com sucesso.')
        return redirect('venda_list')
    return render(request, 'vendas/venda_confirm_delete.html', {'venda': venda})

def _ctx_pdf_from_venda(venda):
    cli = getattr(venda, "cliente", None)
    cliente_nome = getattr(cli, "nome", "") or "-"
    cliente_telefone = getattr(cli, "telefone", "") or "-"
    cliente_documento = getattr(cli, "documento", "") or "-"
    cliente_email = getattr(cli, "email", "") or "-"

    cliente_descricao = getattr(venda, "observacao", "") or getattr(venda, "descricao", "") or "-"

    data = getattr(venda, "criado_em", None) or getattr(venda, "data", None) or timezone.localtime()
    data_str = data.strftime("%d/%m/%Y")

    itens_pdf = []
    total_geral = Decimal("0.00")
    itens_qs = venda.itens.select_related("produto").all()

    for it in itens_qs:
        qtd = Decimal(it.quantidade or 0)
        val = Decimal(it.valor_unitario or 0)
        desc = bool(it.desconto_aplicado)
        sub = qtd * val
        if desc:
            sub *= Decimal("0.95")

        itens_pdf.append({
            "produto_nome": getattr(it.produto, "nome", "—"),
            "quantidade": qtd,
            "valor_unitario": val,
            "desconto_aplicado": desc,
            "subtotal": sub,
        })
        total_geral += sub

    return {
        "title": "Venda",
        "doc_id": venda.pk,
        "data_str": data_str,
        "cliente_nome": cliente_nome,
        "cliente_telefone": cliente_telefone,
        "cliente_documento": cliente_documento,
        "cliente_email": cliente_email,
        "cliente_descricao": cliente_descricao,
        "itens": itens_pdf,
        "total_geral": total_geral,
    }

def venda_pdf(request, pk):
    venda = get_object_or_404(
        Venda.objects.select_related('cliente').prefetch_related('itens__produto'),
        pk=pk
    )
    context = _ctx_pdf_from_venda(venda)

    html_str = render_to_string('pdf/doc_unificado.html', context)
    pdf = HTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf(
        stylesheets=[CSS(filename=str(settings.BASE_DIR / 'core' / 'static' / 'pdf' / 'base_doc.css'))]
    )
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="venda_{context["doc_id"]}.pdf"'
    return resp