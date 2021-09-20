from django import template

register = template.Library()

@register.filter
def decmial2precent(value,arg):
    if value*0 == 0:
        layout = '{0:.%df}' % arg 
        return layout.format(float(value)*100.)
    else:
        return "-"
