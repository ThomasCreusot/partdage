from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from . import forms
from sharingofexperience.models import ProfileModelSharingOfExperiencesUserHasAccess


def login_page(request):
    form = forms.LoginForm()
    message = ''
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)

                # Creation of a ProfileModelSharingOfExperiencesUserHasAccess if a user who logs in
                # does not have one
                # https://docs.djangoproject.com/en/4.1/topics/db/examples/one_to_one/
                try:
                    ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
                except ProfileModelSharingOfExperiencesUserHasAccess.DoesNotExist:
                    profile_model = ProfileModelSharingOfExperiencesUserHasAccess(
                        user=request.user,
                        # 'dictionary initialisation' is used later, see views.py of sharingofexperience app
                        sharing_of_experiences_user_has_access={"dictionary initialisation": 1},
                    )
                    profile_model.save()

                return redirect('home')
            else:
                message = 'Invalid credentials.'
    return render(
        request, 'authentication/login.html', context={'form': form, 'message': message})


def logout_user(request):
    logout(request)
    return redirect('index')


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # auto-login user
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authentication/signup.html', context={'form': form})
