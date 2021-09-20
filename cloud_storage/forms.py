from django import forms
from django.forms.formsets import BaseFormSet
from django.utils.html import format_html

from cloud_storage.models import FileStorageUpload, StorageCatagories

from dal import autocomplete

# class CatagoryAutocomplete(autocomplete.Select2QuerySetView):
#     def get_result_label(self,item):
#         return format_html('<img src="flags/{}.png"> {}',FileStorageUpload.catagory,FileStorageUpload.catagory)
class CloudUploadCatagory(forms.ModelForm):
    class Meta:
        model = StorageCatagories
        fields = ("__all__")
        labels = {
            "catagory_option":"Add New Catagory"
        }


class CloudUpload(forms.ModelForm):
    catagory = forms.ModelChoiceField(
        queryset=StorageCatagories.objects.all(),
    #     widget=autocomplete.ModelSelect2Multiple(url='cloud_storage:catagory-autocomplete',attrs={'data-html':True})
    )
    class Meta:
        model = FileStorageUpload
        # fields = ('__all__')
        fields = ('catagory','file_name','store_select','discription','hierarchy_access')
