from django import forms

from .models import UserURLS
from sls.models import UserProfileURLs

class UpdateUrlList(forms.ModelForm):

    url_code = forms.URLField(initial='https://')
    class Meta:
        model=UserURLS
        fields=('url_code',)

class UpdateUrlProfile(forms.ModelForm):
    class Meta:
        model=UserProfileURLs
        fields=('name',)
