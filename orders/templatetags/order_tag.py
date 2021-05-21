from django import template
register = template.Library()


@register.filter(name="multiple")
def multiple(value, args):
    return value * args
