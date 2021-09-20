from django.db import models
from django.contrib.auth.models import User

from home.models import StoreSave

class StorageCatagories(models.Model):
    catagory_option = models.CharField(max_length=255)
    def __str__(self):
        return self.catagory_option

class FileStorageUpload(models.Model):
    """(FileStorageUpload description)"""
    hierarchy_choice=[
        (6,'All'),
        (1,'Owner'),
        (2,'Upper Management'),
        (3,'Store Manager'),
        (4,'Cash Supervisor'),
        (5,'Department Manager'),
    ]
    ##~ create a list of form choices of stores that are in the database
    #with the first choice being all stores.
    store_choice = [(1, 'All'),] + [
        (num+2, "-".join([str(x.store),str(x.store_town)])) for num,x in enumerate(StoreSave.objects.all())
    ]
    store_select = models.PositiveIntegerField(choices=store_choice)
    file_name = models.FileField()
    uploaded_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    catagory = models.ForeignKey(StorageCatagories)
    discription = models.CharField(max_length=255)
    downloads = models.PositiveIntegerField("download total", default=0)
    hierarchy_access = models.PositiveIntegerField(blank=True, choices=hierarchy_choice)

    def __unicode__(self):
        return u"FileStorageUpload"
