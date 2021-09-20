from django.utils import timezone
from django.contrib.auth.models import User

from user_calendar.models import UserCalendar, SelectiveUserEvent

import datetime
import calendar
import pytz
from email.mime.text import MIMEText
from subprocess import Popen, PIPE


def populate_cascading_events(data_to_html,events,depth):
    entered_pks = []
    skip_pks = []
    depth += 1
    for a,event in enumerate(events):
        # skip event if it clashes with current event
        if event.pk in skip_pks:
            print("skipping")
            continue
        print("\n\n\n The current event is:")
        print(depth,"   ",a,events.count(),event.title,event.start_date,event.pk)

        # make list of events that clash and get their pks
        overlaping_events = []
        overlaping_events = events.filter(start_date__gte=event.start_date).exclude(start_date__gte=event.end_date)
        for pk in overlaping_events:
            if pk.pk not in skip_pks:
                skip_pks.append(pk.pk)

        # make list of pk that have been entered in this level and enter the data that will be sent
        entered_pks.append(event.pk)
        height = (event.end_date-event.start_date).total_seconds()/1800 #1800 is 30 min in seconds
        data_to_html[event.start_date.strftime("%H:%M")]["data"]=True
        data_to_html[event.start_date.strftime("%H:%M")]["events"].append([event,height,depth])

    print("skip array: ",skip_pks)
    if len(skip_pks) > 0:
        print("clashing events triggered sending skipped events to be entered")
        # create a list of all clashed events, minus any events that have been entered
        # and send to recursive function to be added

        events = events.filter(pk__in=skip_pks).exclude(pk__in=entered_pks)
        print(events)
        data_to_html,depth = populate_cascading_events(data_to_html,events,depth)
    return data_to_html,depth

def create_day_view_array(events):
    time_periods = []
    data_to_html = {}
    # shop work day starts @6am-ish for some. No need for times outside of shop hours.
    time = datetime.datetime.strptime("00:00","%H:%M")

    while True:
        time_periods.append(time.strftime("%H:%M"))
        data_to_html[time.strftime("%H:%M")] = {"data":False,"events":[]}

        time = time + datetime.timedelta(minutes=30)
        if time.time() == datetime.datetime.strptime("00:00","%H:%M").time():
            break

    depth = -1
    data_to_html,dept = populate_cascading_events(data_to_html,events,depth)


    for item in data_to_html:
        if data_to_html[item]['data']:
            print(item,data_to_html[item])
    return data_to_html,time_periods

def monthCalendarView(request,first_day_of_the_selected_month,selected_users):
    # print("Starting function")
    # print(first_day_of_the_selected_month,first_day_of_the_selected_month.isocalendar(),"\n\n")
    calendar_size = 42 # There is 42 cells in the calendar display.
    list_of_dates_in_month = []
    first_day_value = int(first_day_of_the_selected_month.strftime("%w"))
    active_year = int(first_day_of_the_selected_month.strftime("%Y"))
    active_month = int(first_day_of_the_selected_month.strftime("%m"))

    add_prefix_buffer_value = first_day_value - 1 # 1 is for monday
    # print("")

    # print(calendar.monthrange(active_year,active_month)[1])
    # print(first_day_of_the_selected_month)
    last_day_of_the_selected_month = first_day_of_the_selected_month.replace(day=calendar.monthrange(active_year,active_month)[1])

    # Working out the prefix
    if add_prefix_buffer_value == -1:
        start_buffer = datetime.timedelta(days=6)
    elif add_prefix_buffer_value == 0:
        start_buffer = datetime.timedelta(days=0)
    else:
        start_buffer = datetime.timedelta(days=add_prefix_buffer_value)

    date = first_day_of_the_selected_month - start_buffer
    last_date = date+datetime.timedelta(days=41)
    # selected_users events.
    if selected_users == None:
        User_events = SelectiveUserEvent.objects.filter(users=request.user)
        print("\n\n\nUsername: ",request.user)
        print(User_events,"\n\n")
    # Create a list of events in the seleted month to add to the calendar.
    list_of_month_events = UserCalendar.objects.filter(start_date__range=[date,last_date])
    print(list_of_month_events,"\n\n")
    list_of_month_events = list_of_month_events.filter(pk__in=User_events.values("calendar_event"))
    print(list_of_month_events,"\n\n")
    # for add_to_date in range(0,calendar_size):
    while date <= last_date:
        cycle_month = int(date.strftime("%m"))
        if (date < first_day_of_the_selected_month) or (date > last_day_of_the_selected_month):
            active_day = "off-month"
            # print("Date: ",date)
            # print("Last date: ",last_day_of_the_selected_month)
            # print("Day value: ",int(date.strftime("%w")))
            # print(date > last_day_of_the_selected_month)
            # print(int(date.strftime("%w")) > 1)
        else:
            active_day = "on-month"

        # if (date > last_day_of_the_selected_month) and (int(date.strftime("%w")) == 1):
        #     break
        # print("Date: ",date)

        current_day_events = list_of_month_events.filter(start_date__day=int(date.strftime("%d")),start_date__month=cycle_month)
        # for item in current_day_events:
        #     print(item.title)
        #     print("-----"+item.start_date.strftime("%w-%m-%Y"))

        if current_day_events.count()>3:
            current_day_events = ['3+ events...']
        list_of_dates_in_month.append([date,active_day,date.isocalendar()[1],current_day_events])
        # print(date,date.isoformat())
        date = date + datetime.timedelta(days=1)

    # for item in list_of_dates_in_month:
    #     print(item)
    return list_of_dates_in_month

def createReminder(request,createdEvent,calendarDates):
    reminder_date = []
    # print("I'm in the function")
    int_reminder_time = int(request.POST["reminder_time"])
    # print(datetime.timedelta(days=int_reminder_time))
    # print(int_reminder_time)
    grammer_for_day = "days"
    # print(request.POST["time_period"])
    if request.POST["time_period"].lower() == "day":
        time_delta = datetime.timedelta(days=int_reminder_time)
        time_to_event = request.POST["reminder_time"]
        if int(request.POST["reminder_time"]) == 1:
            grammer_for_day = "day"
    elif request.POST["time_period"].lower() == "week":
        # print("weeks section")
        time_delta = datetime.timedelta(days=7*int(request.POST["reminder_time"]))
        time_to_event = 7*int(request.POST["reminder_time"])
    elif request.POST["time_period"].lower() == "month":
        # print("month section")
        time_delta = datetime.timedelta(days=30*int(request.POST["reminder_time"]))
        time_to_event = 30*int(request.POST["reminder_time"])

    reminder_title = "Event Schedule Reminder: "+createdEvent["title"]

    if request.POST["reminder_repeat"] == "first":
        reminder_discription = "This has a reminder, "+str(time_to_event)+" "+grammer_for_day+" before the first event."
        reminder_date.append(calendarDates[0] - time_delta)
    else:
        for num,date in enumerate(calendarDates):
            reminder_discription = "This has a reminder, "+str(time_to_event)+" "+grammer_for_day+" before each event."
            reminder_date.append(calendarDates[num] - time_delta)

    # for item in reminder_date:
    #     print(reminder_title)
    #     print(reminder_discription)
    #     print(item)

    return reminder_discription

def Send_Calendar_mail(user,event,user_creator,reminder):

    if reminder:
        msg_body = "Hello {},\n This is a reminder that you have the following event tomorrow:\n".format(user.first_name)
    else:
        msg_body = "Hello {},\n{} has added you to the following event:\n".format(user.first_name,user_creator.first_name)


    msg_event ="{}\n{}-{}\n\n{}\n\n".format(event["title"],event["start_time"],event["finish_time"],event["discription"])
    msg_footer = "This is an automated message. Do not reply to this message\nFor queries on this event please contant the event creator;\n{} at {}\n".format(user_creator.first_name,user_creator.email)

    msg = MIMEText(msg_body+msg_event+msg_footer)
    msg["From"] = "calendar@donohoegroup.ie"
    msg["To"] = user.email
    msg["Subject"] = "Calendar event:{}".format(event["title"])

    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_bytes())

def event2Database(createdEvent,calendarDates,selected_users,errorReport):
    savedEvent = []
    for date in calendarDates:
        start_date = datetime.datetime.combine(date,datetime.datetime.strptime(createdEvent["start_time"],"%H:%M").time())
        end_date = datetime.datetime.combine(date,datetime.datetime.strptime(createdEvent["finish_time"],"%H:%M").time())
        # Check to see is the created event has not passed. Can only create future eventsself.
        if start_date < datetime.datetime.now():
            errorReport.append("The following date and time has passed please try again\n%s."%start_date)
            return

        event,created = UserCalendar.objects.get_or_create(
            start_date=start_date,
            end_date=end_date,
            title=createdEvent["title"],
            discription=createdEvent["discription"],
            created_by=createdEvent["created_by"]
        )
        event.save()

        for person in selected_users:
            user,created = SelectiveUserEvent.objects.get_or_create(
                            calendar_event=event,
                            users=User.objects.get(pk=person)
            )

            user.save()
        savedEvent.append(event)

    return savedEvent


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0: # include if it is curently the selected day
        days_ahead += 7

    return d + datetime.timedelta(days_ahead)

def calc_month_date(month_date, selected_date,errorReport):
    when_prefix = month_date[0]
    when_suffix = int(month_date[1])

    month = selected_date.month
    year = selected_date.year

    if when_suffix != 7:
        first_selected_weekday = next_weekday(selected_date,when_suffix)

    if when_prefix == "first" and when_suffix == 7:
        day = 1
        output = datetime.date(year,month,day)

    elif when_prefix == "last" and when_suffix == 7:
        day = calendar.monthrange(year,month)
        output = datetime.date(year,month,day)

    elif when_prefix == "first":
        output=first_selected_weekday.day

    # using the first_selected_weekday just add in the time
    # difference of 7 days to get the next
    elif when_prefix == "second":
        output=first_selected_weekday+datetime.timedelta(days=7)

    elif when_prefix == "third":
        output=first_selected_weekday+datetime.timedelta(days=14)

    elif when_prefix == "last":
        # Need to check that there isn't a half week in the month
        check_last_weekday = first_selected_weekday + datetime.timedelta(days=21)
        check_last_weekday_1 = check_last_weekday + datetime.timedelta(days=7)
        if check_last_weekday.month == check_last_weekday_1.month:
            output= check_last_weekday_1
        else:
            output= check_last_weekday
    return output

def add_one_month(selected_date):
    #This will add on one month to the inputed date.
    day = 1
    month = selected_date.month
    year = selected_date.year + month // 12
    month = month % 12 + 1
    return datetime.date(year,month,day)

def create_next_reoccuring_event(repeat_type,selected_date,noteReport,errorReport):
    # set up the next dates if the loop continues
    if repeat_type == "Month":
        selected_date = add_one_month(selected_date.replace(day=1))

    elif repeat_type == "Day":
        selected_date = selected_date + datetime.timedelta(days=1)

    elif repeat_type == "Week":
        selected_date = selected_date + datetime.timedelta(weeks=1)

    elif repeat_type == "Year":
        day=selected_date.day
        month=selected_date.month
        year=selected_date.year
        if selected_date.day == 29 and selected_date.month == 2:
            leap_year_check=True
            while leap_year_check:
                year+=4
                try:
                    selected_date = datetime.date(year, month, day)
                    # check become False as we want to exit
                    # once we have a valid date
                    leap_year_check=False
                except ValueError:
                    noteReport.append("%s-%s-%s is not a leap day! skipping."%(day,month,year))

        else:
            year+=1
            # print(year,"-",month,"-",day)
            selected_date = datetime.date(year, month, day)
    return selected_date

def createDates(raw_data,noteReport,errorReport):
    create_event_date = []

    for key,value in raw_data.items():
        if  key in ['group_choice','selected_users','month_date']:
            for item in raw_data.getlist(key):
                print("%s : %s" %(key,item))
        else:
            print("%s : %s" %(key,value))
    # print("\n\n")

    if raw_data["repeat_type"] == "Month":
        #This is the first day of the current calendar month.
        selected_date = datetime.date.today().replace(day=1)
        if raw_data["month_start"] == "next" :
            selected_date = add_one_month(selected_date)

    else:
        selected_date = datetime.datetime.strptime(raw_data["date"],'%Y-%m-%d').date()

    # Setting up the conditions for the repeat event loop
    number_repeat_events = 0
    if raw_data["event_repeat"]:
        repeat = int(raw_data["event_repeat"]) - 1
    else:
        repeat = 0

    while number_repeat_events <= repeat:
        # print(" ")
        # print("The number of repeats is set to:%s"%repeat)
        # print(" ")
        number_repeat_events+=1
        year = selected_date.year
        month = selected_date.month

        # Fist work out the starting date. This date will
        # be used to work out the following repeat events.
        if raw_data["repeat_type"] == "Month":
            # month is a special case as it needs to
            # work out based on selections (i.e. lest
            # do this first friday of the month.)
            create_event_date.append(calc_month_date(month_date=raw_data.getlist("month_date"),selected_date=selected_date))

        else:
            create_event_date.append(selected_date)

        # print("Event date:%s"%create_event_date)

        if number_repeat_events == 1 and selected_date.day == 29 and selected_date.month == 2:
            noteReport.append("You have created an event on the leap day, event only reoccuring in valid leap years.")

        selected_date = create_next_reoccuring_event(
                raw_data["repeat_type"],
                selected_date,
                noteReport,
                errorReport
                )

        if selected_date.day == '29' and selected_date.month == "2" and number_repeat_events == 1:
                noteReport.append("You have created an event on the leap day, event only reoccuring in valid leap years.")
        if repeat:
            selected_date = create_next_reoccuring_event(raw_data,selected_date,noteReport,errorReport)

    output = {
                "create_event_date":create_event_date,
                "noteReport":noteReport
            }
    return output
