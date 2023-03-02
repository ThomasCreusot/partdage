from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from .models import SharingOfExperience
from sharingofexperience.forms import SharingOfExperienceFormCreate


LOWER_LIMIT_AGE_TO_BE_SHARED = 10  # years old
GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES = 1  # years old

def age_calculation(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def sharing_of_experience_already_created_for_an_age(request, experienced_age):
    user_sharing_of_experiences = SharingOfExperience.objects.filter(user_id_id = request.user.id)
    age_already_filled_boolean = experienced_age in [user_sharing_of_experience.experienced_age for user_sharing_of_experience in user_sharing_of_experiences]
    return age_already_filled_boolean


def experienced_age_to_be_created_lower_than_user_age_boolean(experienced_age, request):
    user_age = age_calculation(request.user.birth_date)
    return experienced_age < user_age


def sharing_of_experience_of_an_user_at_a_given_age_id(request, experienced_age):
    sharing_of_experience_already_created = SharingOfExperience.objects.filter(
        Q(user_id_id = request.user.id) & Q(experienced_age=experienced_age)
    )
    sharing_of_experience_already_created_id = sharing_of_experience_already_created[0].id
    return sharing_of_experience_already_created_id


def url_to_be_returned_for_experience_create_view(
        request, experienced_age_to_be_created_low_enough_boolean, age_already_filled_boolean,
        experienced_age, form):

    if not experienced_age_to_be_created_low_enough_boolean:
        return render(request, 'sharingofexperience/be_patient.html')
    else : 
        if age_already_filled_boolean:
            sharing_of_experience_already_created_id=sharing_of_experience_of_an_user_at_a_given_age_id(request, experienced_age)
            return redirect('sharing_an_experience_update', sharing_of_experience_already_created_id)
        else: 
            return render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})


def sharing_of_experience_found(sharing_of_experience_search):
    if len(sharing_of_experience_search) == 0:
        return False
    if len(sharing_of_experience_search) == 1:
        return True


def index(request):
    return render(request, 'sharingofexperience/index.html')


def user_age_plus_minus_range_generation(user_age):
    GAP = GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES
    plus_minus_range = 2 * GAP + 1
    user_age_plus_minus_range = []
    for i in range(plus_minus_range):
        user_age_plus_minus_range.append(user_age - GAP + i)
    return user_age_plus_minus_range


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

    global url_to_be_returned_for_experience_create_view

    if request.method == 'POST':
        form = SharingOfExperienceFormCreate(request.POST)
        if form.is_valid():
            # first functional version 
            # SharingOfExperience = form.save()

            # New instance but without saving in database
            sharing_of_experience = form.save(commit=False)
            # set the connected user to the user and other data before saving the model
            sharing_of_experience.user_id_id = request.user.id
            sharing_of_experience.moderator_validation = "NOP"  # NOP = "Not processed yet"
            sharing_of_experience.likes = {"likes": {}}
            sharing_of_experience.experienced_age = experienced_age
            # Save
            sharing_of_experience.save()
            return redirect('sharing_experiences_menu')
    else:
        form = SharingOfExperienceFormCreate()


    age_already_filled_boolean = sharing_of_experience_already_created_for_an_age(request, experienced_age)
    experienced_age_to_be_created_low_enough_boolean = experienced_age_to_be_created_lower_than_user_age_boolean(experienced_age, request)

    url_to_be_returned = url_to_be_returned_for_experience_create_view(
        request, experienced_age_to_be_created_low_enough_boolean, age_already_filled_boolean,
        experienced_age, form)
    return url_to_be_returned


@login_required
def sharing_an_experience_update(request, sharing_of_experience_id):
    # modified as an user could as to update a sharing_of_experience that does not exist yet
    # sharing_of_experience = SharingOfExperience.objects.get(id=sharing_of_experience_id)
    global sharing_of_experience_found

    sharing_of_experience_search = SharingOfExperience.objects.filter(id=sharing_of_experience_id)

    sharing_of_experience_was_found = sharing_of_experience_found(sharing_of_experience_search)

    if not sharing_of_experience_was_found:
        return render(request, 'sharingofexperience/sharing_of_experience_not_yet_created.html')

    elif sharing_of_experience_was_found:
        sharing_of_experience=sharing_of_experience_search[0]
        if sharing_of_experience.user_id == request.user:
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
        else:
            return render(request, 'sharingofexperience/not_your_experience.html')


@login_required
def learning_from_others(request):
    user_age = age_calculation(request.user.birth_date)
    user_age_plus_minus_range = user_age_plus_minus_range_generation(user_age)
    sharing_of_experiences_from_others = SharingOfExperience.objects.filter(
        ~Q(user_id_id = request.user.id) & Q(experienced_age__in=user_age_plus_minus_range)
    )
    context = {
        'sharing_of_experiences':sharing_of_experiences_from_others
    }
    return render(request, 'sharingofexperience/learning_from_others.html', context=context)


@login_required
def like_a_sharing_of_experience(request):
    print("like : done")
    return redirect('learning_from_others')