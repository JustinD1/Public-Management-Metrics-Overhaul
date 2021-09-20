from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from home.models import StoreSave
from sls.models import Profile

# Create your views here.
@login_required
def landing(request):
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)

    stores = StoreSave.objects.all()
    return render(request,'reportList/report_lists.html', {'stores':stores})
