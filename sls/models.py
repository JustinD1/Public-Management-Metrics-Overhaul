from django.db import models
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.core.validators import validate_comma_separated_integer_list

from django.db.models.signals import post_save
from django.contrib.auth.models import User

from home.models import UserURLS

#Setting up an Extending User Model Using a One-To-One Link
class Profile(models.Model):
    hierarchy_choice=[
        (1,'Owner'),
        (2,'Region Manager'),
        (3,'Store Manager'),
        (4,'Cash Supervisor'),
        (5,'Department Manager'),
        (6,'Other'),
    ]
    # current user profile information.
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    hierarchy = models.PositiveIntegerField(blank=True, choices=hierarchy_choice)
    region = models.PositiveIntegerField(blank=True)
    store = models.TextField(max_length=10,blank=False)
    section = models.TextField(max_length=100,blank=True)
    # user that created this user.
    created_by = models.TextField(max_length=20,editable=False)
    # list of url ID's in order of user preferance (*still working on it...)
    custom_url_order = models.CharField(validators=[validate_comma_separated_integer_list],max_length=250,null=True,default='')


class UserProfileURLs(models.Model):
    # def meta:
    url_link = models.ForeignKey(UserURLS,on_delete=models.CASCADE)
    name = models.CharField(blank=True, max_length=100)
