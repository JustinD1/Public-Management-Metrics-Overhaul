from rest_framework import serializers

from user_calendar.models import UserCalendar

class UserCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCalendar
        field = ["start_date","end_date","title","discription","uuid"]
