from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import ItemVenda
from produtos.models import Produto
from django.core.exceptions import ValidationError

@receiver(pre_save, sender=ItemVenda)
def ajustar_estoque_item(sender, instance, **kwargs):

    if not instance.produto_id or instance.quantidade is None:
        return

    with transaction.atomic():
        qtde_antiga = 0
        produto_antigo = None

        if instance.pk:
            try:
                item_antigo = ItemVenda.objects.get(pk=instance.pk)
                qtde_antiga = item_antigo.quantidade
                produto_antigo = item_antigo.produto
            except ItemVenda.DoesNotExist:
                pass

        if instance.pk and produto_antigo and instance.produto != produto_antigo:
            produto_antigo.quantidade_estoque += qtde_antiga
            produto_antigo.save(update_fields=['quantidade_estoque'])
            qtde_antiga = 0

        diff = instance.quantidade - qtde_antiga
        if diff > 0 and instance.produto.quantidade_estoque < diff:
            raise ValidationError(f"Estoque insuficiente! <br> Atual: {instance.produto.quantidade_estoque}")

        instance.produto.quantidade_estoque -= diff
        instance.produto.save(update_fields=['quantidade_estoque'])


@receiver(post_delete, sender=ItemVenda)
def restaurar_estoque_item(sender, instance, **kwargs):
    if not instance.produto_id or instance.quantidade is None:
        return
    instance.produto.quantidade_estoque += instance.quantidade
    instance.produto.save(update_fields=['quantidade_estoque'])
