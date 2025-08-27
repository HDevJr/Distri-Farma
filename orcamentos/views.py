import os
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
import traceback
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
from django.forms.utils import ErrorList
from .forms import OrcamentoForm, ItensOrcamentoFormSet
from vendas.models import Venda, ItemVenda
from .models import Orcamento
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils.html import format_html, format_html_join
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.utils import timezone


def orcamento_list(request):
    q = request.GET.get('q', '')
    mostrar = request.GET.get('mostrar', 'abertos')

    qs = Orcamento.objects.select_related('cliente')

    if mostrar == 'abertos':
        qs = qs.filter(convertido_em_venda=False)
    elif mostrar == 'convertidos':
        qs = qs.filter(convertido_em_venda=True)

    if q:
        qs = qs.filter(Q(id__icontains=q) | Q(cliente__nome__icontains=q))

    paginator = Paginator(qs.order_by('-criado_em'), 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(
        request,
        'orcamentos/orcamentos.html',
        {'page_obj': page_obj, 'q': q, 'mostrar': mostrar}
    )

def orcamento_detail(request, pk):
    orc = get_object_or_404(Orcamento, pk=pk)
    itens = []
    total_geral = Decimal('0.00')
    for it in orc.itens.select_related('produto').all():
        subtotal = Decimal(it.quantidade) * it.valor_unitario
        if it.desconto_aplicado:
            subtotal *= Decimal('0.95')
        itens.append({
            'produto': it.produto,
            'quantidade': it.quantidade,
            'valor_unitario': it.valor_unitario,
            'desconto_aplicado': it.desconto_aplicado,
            'subtotal': subtotal,
        })
        total_geral += subtotal

    ctx = {"orcamento": orc, "itens": itens, "total_geral": total_geral}
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "orcamentos/_orcamento_detail.html", ctx)
    return render(request, "orcamentos/orcamento_detail_page.html", ctx)


def orcamento_add(request):

    if request.method == 'POST':
        form = OrcamentoForm(request.POST)
        formset = ItensOrcamentoFormSet(request.POST, prefix='itens')  # <—
        if form.is_valid() and formset.is_valid():
            tem_item = any(
                f.cleaned_data and not f.cleaned_data.get('DELETE', False)
                for f in formset.forms
            )
            if not tem_item:
                formset._non_form_errors = ErrorList(["Adicione pelo menos um item ao orçamento."])
            else:
                try:
                    with transaction.atomic():
                        orc = form.save()
                        itens = formset.save(commit=False)
                        for it in itens:
                            it.orcamento = orc
                            it.save()
                            messages.success(request, f'Orçamento { orc.id } criado com sucesso.')
                        for f_del in getattr(formset, 'deleted_forms', []):
                            if f_del.instance.pk:
                                f_del.instance.delete()
                    return redirect('orcamento_list')
                except Exception as e:
                    messages.error(request, f"Erro ao salvar orçamento: {e}")
                    print("ERRO orcamento_add:", traceback.format_exc())
    else:
        form = OrcamentoForm()
        formset = ItensOrcamentoFormSet(prefix='itens')
        formset.extra = 1

    return render(request, 'orcamentos/orcamento_form.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Novo Orçamento',
    })


def orcamento_edit(request, pk):

    orc = get_object_or_404(Orcamento, pk=pk)

    if request.method == 'POST':
        form = OrcamentoForm(request.POST, instance=orc)
        formset = ItensOrcamentoFormSet(request.POST, instance=orc, prefix='itens')
        if form.is_valid() and formset.is_valid():
            tem_item = any(
                f.cleaned_data and not f.cleaned_data.get('DELETE', False)
                for f in formset.forms
            )
            if not tem_item:
                formset._non_form_errors = ErrorList(["Adicione pelo menos um item ao orçamento."])
            else:
                try:
                    with transaction.atomic():
                        form.save()
                        formset.save()
                        messages.success(request, 'Orçamento editado com sucesso.')
                    return redirect('orcamento_list')
                except Exception as e:
                    messages.error(request, f"Erro ao atualizar orçamento: {e}")
                    print("ERRO orcamento_edit:", traceback.format_exc())

    else:
        form = OrcamentoForm(instance=orc)
        formset = ItensOrcamentoFormSet(instance=orc, prefix='itens')
        formset.extra = 1 if formset.total_form_count() == 0 else 0

    return render(request, 'orcamentos/orcamento_form.html', {
        'form': form,
        'formset': formset,
        'titulo': f'Editar Orçamento {orc.pk}',
    })

def orcamento_delete(request, pk):
    orc = get_object_or_404(Orcamento, pk=pk)
    if orc.convertido_em_venda:
        return redirect('orcamento_list')

    if request.method == 'POST':
        orc.delete()
        messages.success(request, f'Orçamento excluído com sucesso')
        return redirect('orcamento_list')

    return render(request, 'orcamentos/orcamento_confirm_delete.html', {'orcamento': orc})

def _ctx_pdf_from_orcamento(orc):
    cli = getattr(orc, "cliente", None)
    cliente_nome = getattr(cli, "nome", "") or "-"
    cliente_telefone = getattr(cli, "telefone", "") or "-"
    cliente_documento = getattr(cli, "documento", "") or "-"
    cliente_email = getattr(cli, "email", "") or "-"
    cliente_descricao = getattr(orc, "descricao", "") or "-"

    data = getattr(orc, "criado_em", None) or timezone.localtime()
    data_str = data.strftime("%d/%m/%Y")

    itens_pdf = []
    total_geral = Decimal("0.00")
    itens_qs = orc.itens.select_related("produto").all()

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
        "title": "Orçamento",
        "doc_id": orc.pk,
        "data_str": data_str,
        "cliente_nome": cliente_nome,
        "cliente_telefone": cliente_telefone,
        "cliente_documento": cliente_documento,
        "cliente_email": cliente_email,
        "cliente_descricao": cliente_descricao,
        "itens": itens_pdf,
        "total_geral": total_geral,
    }

def orcamento_pdf(request, pk):
    orc = get_object_or_404(Orcamento.objects.select_related('cliente'), pk=pk)
    context = _ctx_pdf_from_orcamento(orc)

    html_str = render_to_string('pdf/doc_unificado.html', context)
    pdf = HTML(string=html_str, base_url=request.build_absolute_uri('/')).write_pdf(
        stylesheets=[CSS(filename=str(settings.BASE_DIR / 'core' / 'static' / 'pdf' / 'base_doc.css'))]
    )
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="orcamento_{context["doc_id"]}.pdf"'
    return resp

def orcamento_confirmar_conversao(request, pk):
    orc = get_object_or_404(Orcamento, pk=pk, convertido_em_venda=False)

    itens_qs = getattr(orc, 'itens', None)
    if itens_qs is None:
        itens_qs = orc.itensorcamento_set  # fallback
    itens_qs = itens_qs.select_related('produto').all()

    itens = []
    total_geral = Decimal('0.00')
    for it in itens_qs:
        subtotal = Decimal(it.quantidade) * it.valor_unitario
        if it.desconto_aplicado:
            subtotal *= Decimal('0.95')
        itens.append({
            'produto': it.produto,
            'quantidade': it.quantidade,
            'valor_unitario': it.valor_unitario,
            'desconto_aplicado': it.desconto_aplicado,
            'subtotal': subtotal,
        })
        total_geral += subtotal

    return render(
        request,
        'orcamentos/confirmar_conversao.html',
        {'orcamento': orc, 'itens': itens, 'total_geral': total_geral}
    )

@transaction.atomic
def orcamento_converter(request, pk):
    if request.method != 'POST':
        return redirect('orcamento_confirmar_conversao', pk=pk)

    orc = get_object_or_404(Orcamento, pk=pk, convertido_em_venda=False)

    itens_qs = getattr(orc, 'itens', None)
    if itens_qs is None:
        itens_qs = orc.itensorcamento_set
    itens_qs = itens_qs.select_related('produto').all()

    insuficientes = []
    for it in itens_qs:
        disponivel = it.produto.quantidade_estoque
        if it.quantidade > disponivel:
            insuficientes.append((str(it.produto), it.quantidade, disponivel))

    if insuficientes:
        lista_html = format_html_join(
            '', '<li>{} — solicitada: {} | disponível: {}</li>',
            ((nome, q, disp) for nome, q, disp in insuficientes)
        )
        messages.error(
            request,
            format_html(
                '<div>Estoque insuficiente para os itens abaixo. '
                'A conversão não foi realizada:</div><ul class="mb-0">{}</ul>',
                lista_html
            )
        )
        return redirect('orcamento_confirmar_conversao', pk=pk)

    venda = Venda.objects.create(
        cliente=orc.cliente,
        orcamento=orc,
    )

    for it in itens_qs:
        ItemVenda.objects.create(
            venda=venda,
            produto=it.produto,
            quantidade=it.quantidade,
            valor_unitario=it.valor_unitario,
            desconto_aplicado=it.desconto_aplicado,
        )

    orc.convertido_em_venda = True
    orc.save(update_fields=['convertido_em_venda'])
    orc.delete()

    messages.success(request, 'Venda criada a partir do orçamento.')
    return redirect('venda_edit', pk=venda.pk)