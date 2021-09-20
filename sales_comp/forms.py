from django import forms
from django.forms.formsets import BaseFormSet

from .models import totalWeekTurnover

class ChangeBudget(forms.ModelForm):
    class Meta:
        model = totalWeekTurnover
        fields = ('budget_percent',)

# class DeptSelect(forms.Form):
#     field = forms.ChoiceField(choices=deptList, default=deptList[0])
