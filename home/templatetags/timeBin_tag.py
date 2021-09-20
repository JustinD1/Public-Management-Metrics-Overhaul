from django import template
from django.utils import timezone

import datetime

register = template.Library()

@register.filter
def timeBin(value,arg):
    timecheck = timezone.localtime()
    start_time_delta = value - datetime.timedelta(hours=12)
    if timecheck >= value and timecheck < arg:
        return "Ongoing"
    elif timecheck > arg:
        return "Finished"
    elif  start_time_delta <= timecheck and value > timecheck:
        return "Upcoming"
    else:
        return "12+ hr"
