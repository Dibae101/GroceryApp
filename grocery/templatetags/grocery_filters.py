from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtracts the arg from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value