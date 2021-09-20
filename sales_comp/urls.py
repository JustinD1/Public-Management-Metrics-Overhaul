from django.conf.urls import url
from . import views

app_name = 'sales'
urlpatterns = [
    url(r'^(?P<storeID>\d+)/(?P<year>[0-9]{4})/$',
        views.total_year_sale_to_previous_year,
        name="yearly_sales"
        ),
    url(r'^dept/(?P<storeID>\d+)/(?P<year>[0-9]{4})/$',
        views.departmant_sales_weekly_breakdown,
        name="department_breakdown"
        ),
    url(r'^weekly/(?P<storeID>\d+)/$',
        views.department_comparison,
        name="department_comparison"
        ),
    url(r'^missing/$',
        views.missing_oprs,
        name="missing"
        ),
]
