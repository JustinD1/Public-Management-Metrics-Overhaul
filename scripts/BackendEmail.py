from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone
from django.db.models import Q

from sls.models import Profile, UserProfileURLs
from user_calendar.models import SelectiveUserEvent,UserCalendar
from user_calendar.call_calendar_events import *

import datetime

# [#0001] Cycle through the emails in the morning and email people that have an
#         event on the current day.

##############################################################
######################## [#0001] #############################
##############################################################
# This is to email events for the next day.
# It uses the function in user_calendar.call_calendar_events


def emailNotice():
    createdEvent = {}
    now_date = timezone.now()
    start_datetime_check = now_date
    end_datetime_check = now_date + datetime.timedelta(days=1)

    target_events = UserCalendar.objects.filter(start_date__gt=start_datetime_check).filter(start_date__lt=end_datetime_check)
    reminder = True

    for event in target_events:
        createdEvent["title"] = event.title
        createdEvent["discription"] = event.discription
        createdEvent["start_time"] = event.start_date.time()
        createdEvent["finish_time"] = event.end_date.time()
        listUsers = SelectiveUserEvent.objects.filter(calendar_event=event.pk)
        for user in listUsers:
            Send_Calendar_mail(user.users,createdEvent,event.created_by,reminder)
            # print("%s,has been emailed."%user)
