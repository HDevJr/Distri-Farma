from django import template
import locale

register = template.Library()

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # fallback

@register.filter
def currency_brl(value):
    try:
        value = float(value)
        return locale.currency(value, grouping=True, symbol=True)
    except (ValueError, TypeError):
        return "R$ 0,00"
