from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'sls'
urlpatterns = [
    url(r'^login/$', auth_views.login,name="login"),
    url(r'^logout/$', auth_views.logout,name="logout"),
    url(r'^register/$', views.register,name="register"),
    url(r'^(?P<selected_user>[-\w]+)/$', views.view_profile,name="view_profile"),
    ]
