from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404

from .forms import DocumentForm,MultipleUpload
from .models import Document,WeekSales
from home.models import StoreSave,FileDate
from sls.models import Profile

from OPR2.scripts import uploadFile

@login_required
def model_form_upload(request):
    user = Profile.objects.get(user=request.user)
    if user.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)

    noteReport = []
    errorReport = []
    content = {}

    if request.method == 'POST':
        form = MultipleUpload(request.POST,request.FILES)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            for count,file in enumerate(files):
                # post = Document.objects.create(description=file,document=file)
                uploadFile(filepath=file,noteReport=noteReport,errorReport=errorReport)

    form = MultipleUpload()
    content['form'] = form
    if errorReport:
        content["errorReport"] = errorReport
    return render(request, 'opr2/model_form_upload.html',content)

@login_required
def show_opr_list(request,store):
    try:
        selectedStore = StoreSave.objects.get(store=store)
    except:
        raise Http404("The Store, %s, you have selected does not exist." %str(store))

    permissions = Profile.objects.get(user=request.user)
    if permissions.hierarchy == 1:
        storeDB = StoreSave.objects.exclude(store__icontains=store)
    elif (permissions.hierarchy == 2) and (permissions.region == selectedStore.region):
        storeDB = StoreSave.objects.filter(region=permissions.region).exclude(store__icontains=store)
    elif permissions.hierarchy == 3 and (selectedStore.store in [int(item) for item in permissions.store.split(" ")]):
        storeDB = []
    else:
        content = {'permissions':permissions}
        return render(request,'no_premission.html',content)

    dateDB = FileDate.objects.filter(store=selectedStore,file_type='OPR').order_by("date")

    yearList = []
    for item in dateDB.order_by("-date"):
        print("FileDate: %s, Year: %s." %(item,str(item.financial_year)))
        if item.financial_year not in yearList:
            yearList.append(item.financial_year)

    content = {'selectedStore':selectedStore, 'storeDB':storeDB, 'dateDB':dateDB, 'yearList':yearList}
    return render(request,'opr2/opr_request.html', content)

@login_required
def show_opr_dept(request,store,pk):
    try:
        deptDB = WeekSales.objects.filter(date=pk)
    except:
        raise Http404("The OPR you have selected does not exist.")

    selectedStore = StoreSave.objects.get(store=store)
    permissions = Profile.objects.get(user=request.user)
    if permissions.hierarchy == 1:
        storeDB = StoreSave.objects.exclude(store__icontains=store)
    elif (permissions.hierarchy == 2) and (permissions.region == selectedStore.region):
        storeDB = StoreSave.objects.filter(region=permissions.region).exclude(store__icontains=store)
    elif permissions.hierarchy == 3 and (selectedStore.store in [int(item) for item in permissions.store.split(" ")]):
        storeDB = []
    else:
        content = {'permissions':permissions}
        return render(request,'no_premission.html',content)

    deptDB = deptDB.order_by('pk')
    dateDB = deptDB[0].date

    content = {'deptDB':deptDB,'dateDB':dateDB,'store':selectedStore}
    return render(request,'opr2/display_opr_dept.html', content)
