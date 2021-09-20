from django.shortcuts import render
from django.utils import timezone

from sls.models import Profile, UserProfileURLs
from home.models import UserURLS
from user_calendar.models import UserCalendar,SelectiveUserEvent
from .forms import UpdateUrlList, UpdateUrlProfile

import datetime

def home(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except:
        return render(request,'home/home.html')

    if user_profile.custom_url_order:
        current_user_urls = [ int(x) for x in user_profile.custom_url_order.split(',')]
    else:
        current_user_urls = []
    now = timezone.localtime()

    # user_calendar = Usercalendar.objects.filter(start_date__day=now.strftime('%d'))

    if request.method == "POST":
        if "delete_url_from_list" in request.POST:
            delete_url_from_list = request.POST.getlist("delete_url_from_list")
            for delete_item in delete_url_from_list:
                current_user_urls.remove(int(delete_item))

            UserProfileURLs.objects.filter(id__in=delete_url_from_list).delete()
        if "url_code" in request.POST:
            update_url = UpdateUrlList(data=request.POST)
            update_url_profile = UpdateUrlProfile(data=request.POST)
            # print(request.POST['url_code'])
            # print(request.POST['name'])
            if update_url.is_valid() and update_url_profile.is_valid():
                if request.POST['url_code']:
                    url_link_object,created = UserURLS.objects.get_or_create(url_code=request.POST['url_code'])
                    print('object created: %s'%(url_link_object))
                    url_link_object.save()
                    profile_urls = UserProfileURLs.objects.create(url_link=url_link_object,name=request.POST['name'])

                    profile_urls.save()
                    current_user_urls.append(int(profile_urls.pk))
                    user_profile.custom_url_order = ','.join([str(item) for item in current_user_urls])
                    user_profile.save()


    if 'update_url' not in locals():
        update_url = UpdateUrlList()
        update_url_profile = UpdateUrlProfile()

    if user_profile.custom_url_order:
        user_external_links = UserProfileURLs.objects.filter(id__in=current_user_urls)
    else:
        user_external_links = []

    # This section pulls the next 10 up coming events for the user
    cutoffTime = timezone.localtime() - datetime.timedelta(hours=2)
    calendar_event = SelectiveUserEvent.objects.filter(users=request.user,calendar_event__start_date__gt=cutoffTime).order_by("calendar_event")[0:11]

    content = {'now':now,'user_profile':user_profile,'update_url':update_url,'update_url_profile':update_url_profile,'user_external_links':user_external_links}
    content["calendar_event"] = calendar_event
    return render(request,'home/home.html',content)
