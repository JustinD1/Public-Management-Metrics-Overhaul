from django.conf.urls import url

from . import views

app_name = 'opr2'
urlpatterns = [
    url(r'^$',views.model_form_upload,name="home"),
    url(r'^(?P<store>[-\w]+)/$',views.show_opr_list,name="show_opr_list"),
    url(r'^(?P<store>[-\w]+)/(?P<pk>\d+)/$',views.show_opr_dept,name="show_opr_dept"),
]
