from django import forms

from user_calendar.models import UserCalendar


class editEventForm(forms.ModelForm):
    start_date = forms.DateTimeField(label = "Starting date:", widget=forms.SplitDateTimeWidget())
    end_date = forms.DateTimeField(label = "Ending date:", widget=forms.SplitDateTimeWidget())


    class Meta:
        model = UserCalendar
        fields = ('title','discription','start_date','end_date',)
