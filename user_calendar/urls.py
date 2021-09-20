from django.conf.urls import url
from . import views

app_name = 'user_calendar'
urlpatterns = [
    url(r'^$',
        views.full_calendar,
        name="full_calendar"
        ),
    url(r'^add_event',
        views.add_event,
        name="add_event"
        ),
    url(r'^queryDates',
        views.grab_date_events,
        name="query_dates"
        ),
    url(r'^(?P<uuid>[-\w]+)',
        views.edit_events,
        name="edit_event"
        ),
]
