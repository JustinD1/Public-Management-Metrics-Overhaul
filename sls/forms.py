from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile
from home.models import StoreSave
from OPR2.models import OPRSave

class UserCreate(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    password = forms.CharField(required=False,widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name','last_name', 'password', 'email')

    def save(self, commit=True):
        user = super(UserCreate,self).save(commit=False)
        password = self.cleaned_data["password"]
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        self.current_user = kwargs.pop('current_user',None)
        super(ProfileForm, self).__init__(*args,**kwargs)

        current_user_object = Profile.objects.get(user=User.objects.get(username=self.current_user))

        highest_hierarchy_from_user = current_user_object.hierarchy
        # Create region choices
        region_choice = []
        region_list = []
        for item in StoreSave.objects.all():
            if item.region not in region_list:
                region_list.append(item.region)
        region_choice += [(idx,x) for idx, x in enumerate(region_list)]
        # Department section choices
        section_choice = [(0,'all')]

        section_choice += [(idx + 1,x.name) for idx,x in enumerate(OPRSave.objects.filter(data_level=1))]
        section_choice += [(len(section_choice),"None")]

        # Store choices
        if highest_hierarchy_from_user == 1:
            store_choice = [(1,'all')]
        else:
            store_choice = []

        store_choice += [(x.store,'-'.join([str(x.store),str(x.store_town)])) for x in StoreSave.objects.filter(region=current_user_object.region)]

        # hierarchy choice, need to limit what the person creating the account can see, Don't want a store manager creating someone with owner status.

        if highest_hierarchy_from_user == 2:
            update_hierarchy = self.fields['hierarchy'].choices[3:]
            self.fields['hierarchy'] = forms.ChoiceField(choices=update_hierarchy)
        elif highest_hierarchy_from_user > 2:
            update_hierarchy = self.fields['hierarchy'].choices[4:]
            self.fields['hierarchy'] = forms.ChoiceField(choices=update_hierarchy)
        self.fields['region'] = forms.ChoiceField(choices=region_choice)
        self.fields['section'] = forms.ChoiceField(choices=section_choice)
        self.fields['store'] = forms.ChoiceField(choices=store_choice)
    class Meta:
        model = Profile

        fields = ('hierarchy','region','store','section')
