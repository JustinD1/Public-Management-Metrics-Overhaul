from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import render_to_string

from user_calendar.models import UserCalendar
from user_calendar.call_calendar_events import *
from user_calendar.forms import editEventForm
from sls.models import Profile, UserProfileURLs
from home.models import StoreSave

import calendar
import datetime

@csrf_exempt
@login_required
def add_event(request):

    # Check user has premission to view this data
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)

    errorReport = []
    noteReport = []

    repeat_type_select=['Day','Week','Month','Year']
    monthly_select_type=['first','last','second','third']
    monthly_select_day=[
    (7,'Day'),
    (0,'Mon'),
    (1,'Tue'),
    (2,'Wed'),
    (3,'Thur'),
    (4,'Fri'),
    (5,'Sat'),
    (6,'Sun'),
    ]

    # Creating the list of users that you can select in the formself.
    # Creates a seprate group for Management for easier selection.
    group_choices=Profile.hierarchy_choice
    user_choices=Profile.objects.all().exclude(user__username="sysadmin")
    # remove the Management team from the store lists
    user_choices=user_choices.all().order_by('hierarchy')

    store_sort=StoreSave.objects.all()
    content={'store_sort':store_sort,'user_choices':user_choices,'group_choices':group_choices,'repeat_type_select':repeat_type_select,'monthly_select_type':monthly_select_type,'monthly_select_day':monthly_select_day}

    if request.method == 'POST':
        # print(" ")
        # print(" ")
        # print(request.POST)
        # print(" ")
        # print(" ")
        if "deleteEvent" in request.POST:
            # print("delete event has been toggled, the event number is %s"%request.POST["deleteEvent"])
            PK_2_deleted=request.POST["deleteEvent"]
            # print(PK_2_deleted)
            PK_2_deleted = PK_2_deleted[1:-1].split(",")
            for item in PK_2_deleted:
                UserCalendar.objects.get(pk=int(item)).delete()
                # print("Deleting event")

            noteReport.append("Deleted the event.")
            return render(request,'user_calendar/add_event.html',content)

        if "confirmEvent" in request.POST:
            PK_2_email = request.POST["confirmEvent"]
            PK_2_email = PK_2_email[1:-1].split(",")
            PK_2_email = [int(item) for item in PK_2_email]
            # print(PK_2_email)

            createdEvent = {}
            target_events = UserCalendar.objects.filter(pk__in=PK_2_email)
            reminder = False

            for event in target_events:
                createdEvent["title"] = event.title
                createdEvent["discription"] = event.discription
                createdEvent["start_time"] = event.start_date.time()
                createdEvent["finish_time"] = event.end_date.time()
                listUsers = SelectiveUserEvent.objects.filter(calendar_event=event.pk)
                for user in listUsers:
                    # Send_Calendar_mail(user.users,createdEvent,event.created_by,reminder)
                    print(user.users,createdEvent,event.created_by,reminder)
                noteReport.append("Event has been created and emialed to Attendees.")
                return render(request,'user_calendar/add_event.html',content)

        # print(request.POST)
        user_input = request.POST.copy()
        for key,value in user_input.items():
            if  key in ['group_choice','selected_users','month_date']:
                for item in user_input.getlist(key):
                    print("%s : %s" %(key,item))
            else:
                print("%s : %s" %(key,value))

        # print("\n\n\n")
        # need to check that the user has filled out the form properly

        error_check = False
        # checks for title
        if not user_input["title"]:
            errorReport.append("You need to have a title for the event.")
            error_check = True
        # Checks title not over 150 characters
        elif len(user_input["title"]) > 150:
            errorReport.append("Title can only be a maximum of 150 characters. (%s)"%(len(user_input["title"])))
            error_check = True
        #Checks that the discription isn't over 300 characters
        if len(user_input["discription"]) > 300:
            errorReport.append("Discription can only be a maximum of 300 characters. (%s)"%(len(user_input["discription"])))
            error_check = True
        # checks that the user has inputed a starting time
        if not user_input["start_time"]:
            errorReport.append("You need to select a start time for the event.")
            error_check = True
        # Checks if the finishing time is set and if not set it to and hour after starting
        elif not user_input["finish_time"]:
            noteReport.append("Finishing time was not set; setting it to 1 hour later.")
            start_time_time_object=datetime.datetime.strptime(user_input["start_time"],"%H:%M")
            user_input["finish_time"] = (start_time_time_object + datetime.timedelta(hours=1)).strftime("%H:%M")
        # check to make sure that the repeat events are going to be between 1-20
        # to prevent people from circumvent the html lock
        if (int(user_input["event_repeat"]) < 1) or (int(user_input["event_repeat"]) > 31):
            errorReport.append("You have tried to set the repeat outside the values of 1 to 31.\n1 means the day you have selected.")

        selected_users = user_input.getlist("selected_users")
        selected_groups = user_input.getlist("group_choice")
        if selected_groups:
            # populating group into seprate users excluding sysadmin.
            for person in Profile.objects.filter(hierarchy__in=selected_groups).exclude(user=2):
                    selected_users.append(person.user.pk)

        if not (selected_users):
            errorReport.append("You need to select a group or individual users.")
            error_check = True

        if not error_check:
            calendarDates = []
            createdEvent = {}

            event_added = createDates(
            user_input,
            noteReport,
            errorReport)

            calendarDates = event_added["create_event_date"]
            createdEvent["title"] = user_input["title"]
            createdEvent["discription"] = user_input["discription"]
            createdEvent["start_time"] = user_input["start_time"]
            createdEvent["finish_time"] = user_input["finish_time"]
            createdEvent["created_by"] = request.user
            content["createdEvent"] = createdEvent
            # content["calendarDates"] = calendarDates

            savedEvents = event2Database(createdEvent=createdEvent,calendarDates=calendarDates,selected_users=selected_users,errorReport=errorReport)

            if "create_reminder" in request.POST:
                print("creating reminder objects for the events.")
                reminder_discription = createReminder(request,createdEvent,calendarDates)
                createdEvent["reminder_discription"] = reminder_discription


            # print("The list of errors being reported:\n%s"%errorReport)

            if not errorReport:
                content["savedEvents"] = savedEvents
                content["selected_users"] = Profile.objects.filter(user__in=selected_users)
                # print("created events:")
                # print(savedEvents)
                content["eventPKs"]= [x.pk for x in savedEvents]

                # Email the users that have been added to the event.
                for user_reciver_pk in selected_users:
                    user_reciver = User.objects.get(pk=user_reciver_pk)
                    print(user_reciver)


        if noteReport:
            content["noteReport"] = noteReport
        if errorReport:
            errorReport.append("Fatal error occured event was not created")
            content["errorReport"] = errorReport
    return render(request,'user_calendar/add_event.html',content)

@csrf_exempt
@login_required
def full_calendar(request):
    user = Profile.objects.get(user=request.user)

    # print("\n\n")
    # print(request.POST)
    # print("\n\n")

    content = {}
    current_year = int(datetime.datetime.now().date().strftime("%Y"))
    # order of viewing options for the calendar.
    list_types = [("Month",""),("Week",""),("Day",""),("List",""),]
    # order of months for cycling through.

    list_of_months = [(str(i), calendar.month_name[i]) for i in range(1,13)]

    first_day_of_the_selected_month = datetime.datetime.now().date().replace(day=1)
    # print(first_day_of_the_selected_month,"\n")

    if "selected_users" not in request.POST:
        selected_users = None
    # select the current date/year/view_type if one is not selected from the user.
    if "selected_year" in request.POST:
        selected_year = request.POST["selected_year"]
        first_day_of_the_selected_month = first_day_of_the_selected_month.replace(year=int(selected_year))
    else:
        selected_year = first_day_of_the_selected_month.strftime("%Y")
    if "selected_month" in request.POST:
        # Set the value of the month via quick select
        if "month-backward" in request.POST:
            change_month = int(request.POST["selected_month"]) - 1
            if change_month < 1:
                change_month = 12
                selected_year = str(int(selected_year) - 1)
        elif "month-forward" in request.POST:
            change_month = int(request.POST["selected_month"]) + 1
            if change_month > 12:
                change_month = 1
                selected_year = str(int(selected_year) + 1)
        else:
            change_month = int(request.POST["selected_month"])

        first_day_of_the_selected_month = first_day_of_the_selected_month.replace(month=change_month)
        # print(first_day_of_the_selected_month,"\n\n")
        selected_month = first_day_of_the_selected_month.strftime("%B")
    else:
        selected_month = first_day_of_the_selected_month.strftime("%B")

    list_of_months.insert(0,list_of_months.pop([x for x, y in enumerate(list_of_months) if y[1] == selected_month][0]))

    # list of dates in selected month with buffers for week completion.
    first_day_of_the_selected_month = first_day_of_the_selected_month.replace(year=int(selected_year))
    list_of_dates_in_month = monthCalendarView(request,first_day_of_the_selected_month,selected_users)

    # order of the user selectable years.
    list_of_years = []
    for year in range(current_year - 1,current_year + 3):
        if year == int(selected_year):
            list_of_years.insert(0,year)
        else:
            list_of_years.append(year)

    content["selected_year"] = selected_year
    content["selected_month"] = selected_month
    content["list_types"] = list_types
    content["list_of_months"] = list_of_months
    content["list_of_years"] = list_of_years
    content["list_of_dates_in_month"] = list_of_dates_in_month
    return render(request,'user_calendar/view_calendar.html',content)

@login_required
def edit_events(request,uuid):
    # Check user has premission to view this data
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'user_calendar/no_premission.html',content)

    errorReport = []
    noteReport = []
    content = {}
    event = UserCalendar.objects.get(uuid=uuid)
    form = editEventForm(instance=event)

    content["form"] = form
    return render(request,'user_calendar/edit_event.html',content)

############
#
# API Views
#
# ##########


@login_required
def grab_date_events(request):
    content = {}
    data_structure = []
    information = request.GET["information"]
    display_type = information.split('_')[0].lower()
    date = datetime.datetime.strptime(information.split('_')[1],'%d/%m/%Y')

    if display_type == 'week':
        last_date = date+datetime.timedelta(days=8)
        events = UserCalendar.objects.filter(start_date__range=[date,last_date])
        while date < last_date:
            cycle_month = int(date.strftime("%m"))
            cycle_year = int(date.strftime("%Y"))
            events_in_day = events.filter(start_date__day=int(date.strftime("%d")),start_date__month=cycle_month,start_date__year=cycle_year)
            data_structure.append([date,events_in_day])
            date = date + datetime.timedelta(days=1)
        content['selected_events'] = data_structure
        return_str = render_to_string('user_calendar/display_week_events.html',content)

    else:
        events = UserCalendar.objects.filter(start_date__day=int(date.strftime("%d")),start_date__month=int(date.strftime("%m")),start_date__year=int(date.strftime("%Y"))).order_by("start_date")
        event_stacking,time_periods = create_day_view_array(events)

        content['selected_events'] = event_stacking
        content['time_periods'] = time_periods

        return_str = render_to_string('user_calendar/display_day_events.html',content)

    # return_str = "Please no errors!"
    return HttpResponse(return_str)
