from django import template

register = template.Library()

@register.filter(name='getvalue')
def getvalue(values, key):
    if key not in values:
        return None
    return values[key]

@register.filter(name='multiply')
def multiply(value, arg):
    return float(value) * float(arg) 

@register.filter(name='startswith')
def startswith(value, arg):
    return value.startswith(arg)
