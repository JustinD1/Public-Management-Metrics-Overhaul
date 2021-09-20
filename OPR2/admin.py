from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Document)

class StoreLayout(admin.ModelAdmin):
    fieldsets = [
        (None,      {'fields':['storeName']}),
    ]
admin.site.register(StoreSave,StoreLayout)
admin.site.register(FileDate)
