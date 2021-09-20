from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document',)
        widget = {'document': forms.ClearableFileInput(attrs={'multiple':True})}

class MultipleUpload(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple':True}))
