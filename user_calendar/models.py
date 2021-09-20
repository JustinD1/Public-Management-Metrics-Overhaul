from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import validate_comma_separated_integer_list

import uuid as uuid_lib

import datetime
class UserCalendar(models.Model):
    repeat_choice=[
        (1,'Once'),
        (2,'Daily'),
        (3,'Weekly'),
        (4,'Montly'),
        (5,'Yearly'),
    ]
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    repeating_events = models.CharField(validators=[validate_comma_separated_integer_list],max_length=250,null=True,default='')
    title = models.CharField(blank=False, max_length=150)
    discription = models.CharField(blank=True, max_length=300)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    reminder_event = models.BooleanField(default=False)
    uuid = models.UUIDField ( #should be using this as look up to hide sequential keys.
        db_index=True,
        default=uuid_lib.uuid4,
        editable=False)

    class Meta:
        ordering = ['start_date']

class SelectiveUserEvent(models.Model):
    calendar_event = models.ForeignKey(UserCalendar,on_delete=models.CASCADE)
    users = models.ForeignKey(User,on_delete=models.CASCADE)
    attending = models.BooleanField(default=True)

class reminderCalendar(models.Model):
    user_calendar = models.ForeignKey(UserCalendar,on_delete=models.CASCADE)
    reminder_title = models.CharField(blank=False, max_length=150)
    time_to_event = models.DateField(default=datetime.datetime.today)
