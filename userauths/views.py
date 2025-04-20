from django.shortcuts import  redirect, render
from userauths.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import login , authenticate , logout
from django.contrib import messages
from django.conf import settings
from userauths.models import User, Profile


# User = settings.AUTH_USER_MODEL

def register_view(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hello {username},Your account was Created Successfully.')
            new_user = authenticate(username = form.cleaned_data['email'], password = form.cleaned_data['password1'])     
            login(request, new_user)
            return redirect('core:index')
    else:
        form = UserRegisterForm()
            
    context = {
        'form': form,
        }
    return render(request, 'userauths/sign-up.html', context)


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in')
        return redirect('core:index')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.warning(request, 'Please provide both email and password')
            return render(request, 'userauths/sign-in.html')

        # Authenticate directly with email as username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page if available
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('core:index')
            else:
                messages.warning(request, 'Your account is inactive. Please contact support.')
        else:
            messages.error(request, 'Invalid email or password')

    return render(request, 'userauths/sign-in.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('userauths:sign-in')




def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("core:dashboard")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "userauths/profile-edit.html", context)






