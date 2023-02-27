from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import SharingOfExperience
from sharingofexperience.forms import SharingOfExperienceFormCreate

LOWER_LIMIT_AGE_TO_BE_SHARED = 10 #  years old


def age_calculation(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def index(request):
    objects=SharingOfExperience.objects.all()
    context={
        "objects":objects,
    }
    return render(request, 'index.html', context)


@login_required
def home(request):
    return render(request, 'sharingofexperience/home.html')


@login_required
def sharing_experiences_menu(request):
    user_age = age_calculation(request.user.birth_date)
    user_ages = [age for age in range(user_age) if age > LOWER_LIMIT_AGE_TO_BE_SHARED]
    context = {
        'user_ages':user_ages
    }
    return render(request, 'sharingofexperience/sharing_experiences_menu.html', context=context)


@login_required
def sharing_an_experience_create(request):
    # form = SharingOfExperienceFormCreate
    # return render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})

    if request.method == 'POST':
        form = SharingOfExperienceFormCreate(request.POST)
        if form.is_valid():
            # Create new "nomModele" and save it in database
            SharingOfExperience = form.save()
            return redirect('sharing_experiences_menu')
    else:
        form = SharingOfExperienceFormCreate()
    return render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
