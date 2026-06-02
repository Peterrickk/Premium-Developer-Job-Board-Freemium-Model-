from django import template

register = template.Library()


@register.filter
def premium_mask(value):
    return "🔒 Premium Only"