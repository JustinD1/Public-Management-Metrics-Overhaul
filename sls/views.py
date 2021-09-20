from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.http import Http404

from django.contrib.auth.models import User
from .models import Profile
from .forms import UserCreate, ProfileForm

# Function to create a username based of the inputed first_name and last_name
def create_username(prefix):
    create_username_check = True

    user_with_same_prefix = User.objects.filter(username__startswith=prefix).order_by('-date_joined')
    if user_with_same_prefix.exists():
        last_user_with_same_prefix = user_with_same_prefix[0].username
        suffix_number = int(''.join(filter(lambda x:x.isdigit(),last_user_with_same_prefix))) + 1

        while True:
            created_username = ''.join([prefix,str(suffix_number)])
            if User.objects.filter(username=created_username).exists():
                suffix_number+=1
            else:
                break
    else:
        created_username = ''.join([prefix,'1'])
    return created_username

# Start of the view functions
@login_required
def view_profile(request,selected_user):
    current_user = User.objects.get(username = request.user)
    current_user_profile = Profile.objects.get(user=current_user)

    #Make sure that the selected_user exists and get there profile information.
    try:
        selected_user = User.objects.get(username=selected_user)
        selected_user_profile = Profile.objects.get(user=selected_user)
    except:
        raise Http404("The user, %s, you have selected does not exist." %str(selected_user))

    # Check that the current logged in user has permission to view the selected page and can't change profile of people with higher privilege.
    if current_user_profile.hierarchy > 3 or current_user_profile.hierarchy >= selected_user_profile.hierarchy:
        current_user_profile = Profile.objects.get(user=current_user)

        content = {'current_user':current_user, 'current_user_profile':current_user_profile}
        return render(request,'no_premission.html',content)


    if request.method == 'POST':
        user_form = UserCreate(data=request.POST)
        profile_form = ProfileForm(data=request.POST,current_user=request.user)
        if user_form.is_valid() and profile_form.is_valid():

            if (request.POST['first_name'] != selected_user.first_name) or (request.POST['last_name'] != selected_user.last_name):
                selected_user.first_name = request.POST['first_name']
                selected_user.last_name = request.POST['last_name']
                if not selected_user.username.startswith(request.POST['first_name'][0:1].lower()+request.POST['last_name'][0:3].lower()):
                    selected_user.username = create_username(prefix=request.POST['first_name'][0:1].lower()+request.POST['last_name'][0:3].lower())

            print(request.POST['password'])
            if request.POST['password']:
                selected_user.set_password(request.POST['password'])

            selected_user.save()

            if selected_user_profile.hierarchy != request.POST['hierarchy']:
                selected_user_profile.hierarchy = request.POST['hierarchy']

            if selected_user_profile.region != request.POST['region']:
                selected_user_profile.region = request.POST['region']

            if selected_user_profile.store != request.POST['store']:
                selected_user_profile.store = request.POST['store']

            if selected_user_profile.section != request.POST['section']:
                selected_user_profile.section = request.POST['section']

            selected_user_profile.save()

            return redirect(''.join(['/accounts/register/']))
    else:
        print(selected_user.first_name)
        print(selected_user.last_name)
        profile_form = ProfileForm(instance=selected_user_profile,current_user=request.user)
        user_form = UserCreate(instance=selected_user)
    content = {'user_form':user_form,'profile_form':profile_form,'selected_user':selected_user_profile}

    return render(request,'sls/update_user.html',content)

@login_required
def register(request):
    current_user = User.objects.get(username = request.user)
    if Profile.objects.get(user=User.objects.get(username=request.user)).hierarchy > 3:
        current_user_profile = Profile.objects.get(user=current_user)

        content = {'current_user':current_user, 'current_user_profile':current_user_profile}
        return render(request,'no_premission.html',content)

    if request.method == 'POST':
        print(" ")
        user_form = UserCreate(data=request.POST)
        profile_form = ProfileForm(data=request.POST,current_user=request.user)
        # print("user_form is valid: %s" %user_form.is_valid())
        # print("prifile_form is valid: %s" %profile_form.is_valid())
        print(" ")
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)

            user.username = create_username(prefix=request.POST['first_name'][0:1].lower()+request.POST['last_name'][0:3].lower())

            user.set_password(request.POST['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.created_by = current_user.username
            profile.save()
            return redirect('/accounts/register/')
    else:
        profile_form = ProfileForm(current_user=request.user)
        user_form = UserCreate()


    current_user_created_users = []
    added_users = []
    # for item in Profile.objects.filter(created_by=request.user).order_by('id'):
    #     print(item.user_id)
    #     # current_user_created_users.append(item.user_id)
    #     added_users.append()
    # added_users = User.objects.filter(pk__in=current_user_created_users)
    added_users = Profile.objects.filter(created_by=request.user).order_by('-id')

    content = {'user_form':user_form,'profile_form':profile_form,'added_users':added_users}
    return render(request,'sls/signup.html',content)
