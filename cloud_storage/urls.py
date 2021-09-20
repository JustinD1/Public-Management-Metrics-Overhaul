from django.conf.urls import url

from . import views
from cloud_storage.views import StorageCatagoryAutoComplete

app_name = 'cloud_storage'
urlpatterns = [
    url(r'^(?P<filename_pk>\d+)$',views.download_file,name="download"),
    url(r'^upload/',views.cloud_storage,name="upload"),
    url(r'^$',views.view_storage,name="home"),
    url(
        r'^catagory-autocomplete/$',
        StorageCatagoryAutoComplete.as_view(),
        name='catagory-autocomplete',
    ),
]
