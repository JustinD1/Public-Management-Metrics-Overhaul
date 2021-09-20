# from rest_framework.generics import (
#     ListCreateAPIView,
#     RetrieveUpdateDestroyAPIView
# )

# from rest_framework.permissions import IsAuthenticated


from django.contrib.auth.decorators import login_required

from user_calendar.models import UserCalendar
from .serializers import UserCalendarSerializer
