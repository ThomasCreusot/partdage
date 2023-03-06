from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from .models import SharingOfExperience, ProfileModelSharingOfExperiencesUserHasAccess
from sharingofexperience.forms import SharingOfExperienceFormCreate


LOWER_LIMIT_AGE_TO_BE_SHARED = 10  # years old
GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES = 1  # years old
ACCESS_TO_SHARINGS_MINIMUM_NUMBER = 5

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


def user_has_not_yet_access_to_sharings_of_experiences(request):
    profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    profile_model_dictionnary = profile_model.sharing_of_experiences_user_has_access
    # total_sharing_of_experience_age_plus_minus_one = queryset_sharing_of_experiences_from_others(request).count()
    # len(profile_model_dictionnary)-1 as the dictionnary initialy contains {"dictionary initialisation": 1}
    # return len(profile_model_dictionnary)-1 < min(ACCESS_TO_SHARINGS_MINIMUM_NUMBER, total_sharing_of_experience_age_plus_minus_one)

    # see views.py of authentication app : 
    # -> sharing_of_experiences_user_has_access = {"dictionary initialisation": 1}
    # + see allocation_of_new_sharings_of_experiences : {"dictionary initialisation": 1} -> {}
    return 'dictionary initialisation' in profile_model_dictionnary


def queryset_sharing_of_experiences_from_others(request):
    user_age = age_calculation(request.user.birth_date)
    user_age_plus_minus_range = user_age_plus_minus_range_generation(user_age)
    sharing_of_experiences_from_others = SharingOfExperience.objects.filter(
        ~Q(user_id_id = request.user.id) & Q(experienced_age__in=user_age_plus_minus_range)
    )
    return sharing_of_experiences_from_others


def allocation_of_new_sharings_of_experiences(request, number_of_new_sharings):
    profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    profile_model_dictionnary = profile_model.sharing_of_experiences_user_has_access
    
    # {"dictionary initialisation": 1} -> {}
    # profile_model_dictionnary = {}  # does not works for the actual purpose
    del profile_model_dictionnary['dictionary initialisation']

    total_sharing_of_experience_age_plus_minus_one = queryset_sharing_of_experiences_from_others(request).count()

    i=0
    while len(profile_model_dictionnary) < min(ACCESS_TO_SHARINGS_MINIMUM_NUMBER, total_sharing_of_experience_age_plus_minus_one):
        profile_model_dictionnary[i]=i
        i+=1
        print(i)
    profile_model.save()
    print("2", profile_model_dictionnary)



@login_required
def home(request):
    profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    profile_model_dictionnary = profile_model.sharing_of_experiences_user_has_access
    print("1", profile_model_dictionnary)

    print('initialisation', user_has_not_yet_access_to_sharings_of_experiences(request))
    if user_has_not_yet_access_to_sharings_of_experiences(request):
        allocation_of_new_sharings_of_experiences(request, ACCESS_TO_SHARINGS_MINIMUM_NUMBER)

    #{test to understand}
    profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    profile_model_dictionnary = profile_model.sharing_of_experiences_user_has_access
    print("3", profile_model_dictionnary)

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

    sharing_of_experiences_from_others = queryset_sharing_of_experiences_from_others(request)

    for sharing_of_experience in sharing_of_experiences_from_others:
        sharing_of_experience.total_likes_calculation()

    context = {
        'sharing_of_experiences':sharing_of_experiences_from_others
    }
    return render(request, 'sharingofexperience/learning_from_others.html', context=context)


@login_required
def like_a_sharing_of_experience(request, id_sharing_of_experience_to_be_liked):
    print("like : to be done ; with a if sharing of experience instance . property (to be created : list of sharing exp the request.user has access) = add a like from request.user in dico ; else redirect")
    sharing_of_experience_to_be_liked = SharingOfExperience.objects.filter(id = id_sharing_of_experience_to_be_liked)[0]
    sharing_of_experience_to_be_liked.receive_like(request.user.id)

    return redirect('learning_from_others')