from django import template

register = template.Library()

@register.filter(name='getkey')
def getkey(value, arg):
    return value[arg]

@register.filter(name='multiply')
def multiply(value, arg):
    return float(value) * float(arg) 

@register.filter(name='startswith')
def startswith(value, arg):
    return value.startswith(arg)
