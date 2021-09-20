from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.http import FileResponse

from sls.models import Profile
from cloud_storage.models import FileStorageUpload, StorageCatagories
from home.models import StoreSave
from cloud_storage.forms import CloudUpload, CloudUploadCatagory

from dal import autocomplete

@login_required
def download_file(request,filename_pk):

    requested_file=FileStorageUpload.objects.get(pk=filename_pk)
    requested_file.downloads += 1
    requested_file.save()
    response = FileResponse(requested_file.file_name)
    response['Content-Disposition'] = 'attachment; filename="%s"'%(str(requested_file.file_name).split('/')[-1])
    return response


class StorageCatagoryAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return StorageCatagories.objects.none()

        qs = StorageCatagories.objects.all()
        if self.q:
            qs = qs.filter(catagory_option__istartswith=self.q)

        # qs = qs.value_list('catagory_option',flat=True)
        # print("\n\n")
        # print(qs)
        # print("\n\n")
        # return qs

@login_required
def view_storage(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except:
        return render(request,'home/home.html')

    noteReport = []
    errorReport = []
    content = {}
    hierarchy_choice = user_profile.hierarchy
    user_region = user_profile.region
    if hierarchy_choice < 3:
        user_store = "All"
    else:
        user_store = str(user_profile.store_town)
    for store_choice_id,store in FileStorageUpload.store_choice:
        if user_store == store:
            break

    store_list = ["-".join([str(x.store),str(x.store_town)]) for x in StoreSave.objects.all()]
    # print(request.POST)
    if request.method == 'POST':
        # print("post request sent.")
        if "deleteFile" in request.POST:
            # print("deleteFile has a value.")
            if hierarchy_choice < 3:
                # print("The user has the correct permissions")
                delete_file = FileStorageUpload.objects.filter(pk=request.POST["deleteFile"])
                # print("Going to delete the file:\n %s"%delete_file)
                delete_file.delete()
            else:
                # print("The user has the wrong primissions.")
                errorReport.append("You do not have permission to delete this file.")
    filtered_uploads = FileStorageUpload.objects.filter(store_select=store_choice_id,hierarchy_access__gte=hierarchy_choice)

    for item in FileStorageUpload.objects.all():
        item.store_select
        item.hierarchy_access

    # catagory_list = ['All','Popular',]+[str(catagory.catagory_option) for catagory in StorageCatagories.objects.all()]
    catagory_list = ['All',]+[str(catagory.catagory_option) for catagory in StorageCatagories.objects.all()]

    view_list = ['Full','List']

    # print('List of Stores:\n %s\n'%(store_list))
    # print('List of files:\n %s\n'%(filtered_uploads))
    # print('List of catagories:\n %s\n'%(catagory_list))
    # print('List of viewing options:\n %s\n'%(view_list))

    content['user_profile'] = user_profile
    content['store_list'] = store_list
    content['filtered_uploads'] = filtered_uploads
    content['catagory_list'] = catagory_list
    content['view_list'] = view_list
    content["errorReport"] = errorReport

    return render(request, "cloud_storage/view_storage.html",content)

@login_required
def cloud_storage(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except:
        return render(request,'home/home.html')

    noteReport = []
    errorReport = []
    content = {}

    if user_profile.hierarchy > 3:
        content = {'permissions':user}
        return render(request,'no_premission.html',content)

    print(request.POST)
    if request.method =='POST':
        form = CloudUpload(request.POST, request.FILES)
        catagory_form = CloudUploadCatagory(request.POST)
        file = request.FILES

        # print(form.is_valid(), catagory_form.is_valid())
        if catagory_form.is_valid():
            ##~ insert function for handling file.
            # print("\n\n\n\n")
            catagory_form_info = catagory_form.save(commit=False)
            catagory_form_info.save()
            # print("Saving: %s"%catagory_form_info)


        if form.is_valid():
            form_info = form.save(commit=False)
            form_info.created_by = user_profile.user
            form_info.save()
            # print("Saving: %s"%form_info)

    form = CloudUpload()
    catagory_form = CloudUploadCatagory()
    content['form'] = form
    content['catagory_form'] = catagory_form

    # print(catagory_form)
    # for numer,item in enumerate(form):
    #     print(numer,item)
    if errorReport:
        content["errorReport"] = errorReport
    if noteReport:
        content["noteReport"] = noteReport

    return render(request, "cloud_storage/upload_document.html",content)
