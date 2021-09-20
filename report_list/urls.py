from django.conf.urls import url, include
from django.contrib import admin

from . import views
app_name = 'reports'
urlpatterns = [
    url(r'^$',views.landing,name="reports_landing"),
]
