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
    return render(request, 'sharingofexperience/index.html')


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
def sharing_an_experience_create(request, experienced_age):
    # form = SharingOfExperienceFormCreate
    # return render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})

    if request.method == 'POST':
        form = SharingOfExperienceFormCreate(request.POST)
        if form.is_valid():
            # first functional version 
            # SharingOfExperience = form.save()

            # New instance but without saving in database
            sharing_of_experience = form.save(commit=False)
            # set the connected user to the user before saving the model
            sharing_of_experience.user_id_id = request.user.id
            sharing_of_experience.moderator_validation = "NOP"  # NOP = "Not processed yet"
            sharing_of_experience.likes = {"likes": {}}
            sharing_of_experience.experienced_age = experienced_age

            # Save
            sharing_of_experience.save()
            return redirect('sharing_experiences_menu')
    else:
        form = SharingOfExperienceFormCreate()

    return render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})


@login_required
def sharing_an_experience_update(request, sharing_of_experience_id):
    sharing_of_experience = SharingOfExperience.objects.get(id=sharing_of_experience_id)

    if request.method == 'POST':
        form = SharingOfExperienceFormCreate(request.POST, instance=sharing_of_experience)
        if form.is_valid():
            form.save()
            return redirect('sharing_experiences_menu')
    else:
        form = SharingOfExperienceFormCreate(instance=sharing_of_experience)

    return render(request,
        'sharingofexperience/sharing_an_experience_update.html',
        {'form': form}
    )
