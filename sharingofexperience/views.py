from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from .models import SharingOfExperience, ProfileModelSharingOfExperiencesUserHasAccess
from sharingofexperience.forms import SharingOfExperienceFormCreate
from random import sample

LOWER_LIMIT_AGE_TO_BE_SHARED = 10  # years old
HIGHER_LIMIT_AGE_TO_BE_SHARED = 150  # years old
GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES = 1  # years old
ACCESS_TO_SHARINGS_MINIMUM_NUMBER = 5
DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION = 3
NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS = 2
COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS = 5
NUMBER_OF_AVAILABLE_PAST_OR_FUTURE_SHARINGS_WHEN_SPEND_CREDITS = 1


def age_calculation(birth_date):
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def sharing_of_experience_already_created_for_an_age(request, experienced_age):
    user_sharing_of_experiences = SharingOfExperience.objects.filter(user_id_id=request.user.id)
    age_already_filled_boolean = experienced_age in [user_sharing_of_experience.experienced_age for user_sharing_of_experience in user_sharing_of_experiences]
    return age_already_filled_boolean


def experienced_age_to_be_created_lower_than_user_age_boolean(experienced_age, request):
    user_age = age_calculation(request.user.birth_date)
    return experienced_age < user_age


def sharing_of_experience_of_an_user_at_a_given_age_id(request, experienced_age):
    sharing_of_experience_already_created = SharingOfExperience.objects.filter(
        Q(user_id_id=request.user.id) & Q(experienced_age=experienced_age)
    )
    sharing_of_experience_already_created_id = sharing_of_experience_already_created[0].id
    return sharing_of_experience_already_created_id


def url_to_be_returned_for_experience_create_view(
        request, experienced_age_to_be_created_low_enough_boolean, age_already_filled_boolean,
        experienced_age, form, context):

    if not experienced_age_to_be_created_low_enough_boolean:
        return render(request, 'sharingofexperience/be_patient.html')
    else:
        if age_already_filled_boolean:
            sharing_of_experience_already_created_id = sharing_of_experience_of_an_user_at_a_given_age_id(request, experienced_age)
            return redirect('sharing_an_experience_update', sharing_of_experience_already_created_id)
        else:
            return render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form, 'context': context})


def sharing_of_experience_found(sharing_of_experience_search):
    if len(sharing_of_experience_search) == 0:
        return False
    if len(sharing_of_experience_search) == 1:
        return True


def index(request):
    return render(request, 'sharingofexperience/index.html')


def why_partdage(request):
    return render(request, 'sharingofexperience/why_partdage.html')


def how_partdage_was_made(request):
    return render(request, 'sharingofexperience/how_partdage_was_made.html')


def policy_and_rules(request):
    return render(request, 'sharingofexperience/policy_and_rules.html')


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
    # + see if condition in def home() : {"dictionary initialisation": 1} -> {}
    return 'dictionary initialisation' in profile_model_dictionnary


def queryset_sharing_of_experiences_from_others(request):
    user_age = age_calculation(request.user.birth_date)
    user_age_plus_minus_range = user_age_plus_minus_range_generation(user_age)
    sharing_of_experiences_from_others = SharingOfExperience.objects.filter(
        ~Q(user_id_id=request.user.id) & Q(experienced_age__in=user_age_plus_minus_range)
    )
    return sharing_of_experiences_from_others


def add_credits_to_user(user_profile_model_dictionnary, number_of_credits):
    """Credits are attributed to users who should have access to sharings_of_experience but
    database is not big enough, for future consultation of sharings"""
    if 'credits' in user_profile_model_dictionnary:
        user_profile_model_dictionnary['credits'] += number_of_credits
    else:
        user_profile_model_dictionnary['credits'] = number_of_credits


def user_profile_model_dictionnary_reinitialisation(request):
    user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access
    # {"dictionary initialisation": 1} -> {}
    del user_profile_model_dictionnary['dictionary initialisation']
    user_profile_model.save()


# import timeit
# code_test="""
def allocation_of_new_sharings_of_experiences(request, number_of_new_sharings, sharings_queryset_in_which_we_sample):
    user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access

    total_sharings_queryset_in_which_we_sample = sharings_queryset_in_which_we_sample.count()
    # print('total_sharings_of_experience_age_plus_minus_one', total_sharings_queryset_in_which_we_sample)

    # while len(profile_model_dictionnary) < min(ACCESS_TO_SHARINGS_MINIMUM_NUMBER, total_sharing_of_experience_age_plus_minus_one):
    #    Using random.sample(listName, x) (x=number of draws) on sharing_of_experience_age_plus_minus_one :
    #    Population must be a sequence.  For dicts or sets, use sorted(d).

    number_of_draws = min(number_of_new_sharings, total_sharings_queryset_in_which_we_sample)
    # print('number_of_draws', number_of_draws)

    # Initial version for comparison of Methods A and B
    # sharings_of_experience_age_plus_minus_one = queryset_sharing_of_experiences_from_others(request)
    # total_sharings_of_experience_age_plus_minus_one = sharings_of_experience_age_plus_minus_one.count()
    # print('total_sharings_of_experience_age_plus_minus_one', total_sharings_of_experience_age_plus_minus_one)

    # METHOD A : Equivalent of pop applied on dictionnary
    # timeit.timeit(10000) : 0.0004363999469205737
    # sharings_of_experience_age_plus_minus_one_sample = sharings_of_experience_age_plus_minus_one.order_by('?')[:number_of_draws]
    # for i in range(len(sharings_of_experience_age_plus_minus_one_sample)):
    #    sharing_access_given = sharings_of_experience_age_plus_minus_one_sample[0]
    #    sharings_of_experience_age_plus_minus_one_sample = sharings_of_experience_age_plus_minus_one_sample[1:]
    #    user_profile_model_dictionnary[sharing_access_given.id] = True

    # METHOD B : Conversion queryset to list + random.sample()
    # timeit.timeit(10000) : 0.0004342000465840101
    # list_sharings_of_experience_age_plus_minus_one = list(sharings_of_experience_age_plus_minus_one)
    # sample_sharings_of_experience_age_plus_minus_one = sample(list_sharings_of_experience_age_plus_minus_one, number_of_draws)
    # for sharing in sample_sharings_of_experience_age_plus_minus_one:
    #    user_profile_model_dictionnary[sharing.id] = True
    #    print('user_profile_model_dictionnary', user_profile_model_dictionnary)
    #
    # if total_sharings_of_experience_age_plus_minus_one < number_of_new_sharings:
    #    number_of_credits = number_of_new_sharings-total_sharings_of_experience_age_plus_minus_one
    #    add_credits_to_user(user_profile_model_dictionnary, number_of_credits)

    # METHOD C : Method B adapted to a queryset in which will sample sharings
    # REPRENDRE ICI et ajouter un queryset en parametre de la fonction :)
    list_sharings_queryset_in_which_we_sample = list(sharings_queryset_in_which_we_sample)
    sample_sharings_of_experience = sample(list_sharings_queryset_in_which_we_sample, number_of_draws)
    for sharing in sample_sharings_of_experience:
        user_profile_model_dictionnary[sharing.id] = True
        # print('user_profile_model_dictionnary', user_profile_model_dictionnary)

    if total_sharings_queryset_in_which_we_sample < number_of_new_sharings:
        number_of_credits = number_of_new_sharings-total_sharings_queryset_in_which_we_sample
        add_credits_to_user(user_profile_model_dictionnary, number_of_credits)

    user_profile_model.save()
# """


def cleaning_session_message(request):
    # Message could come from redirection (e.g. spend_credits())
    if 'message' in request.session:
        del request.session['message']


@login_required
def home(request):
    cleaning_session_message(request)

    if user_has_not_yet_access_to_sharings_of_experiences(request):
        user_profile_model_dictionnary_reinitialisation(request)
        sharings_of_experience_age_plus_minus_one = queryset_sharing_of_experiences_from_others(request)
        allocation_of_new_sharings_of_experiences(request, ACCESS_TO_SHARINGS_MINIMUM_NUMBER, sharings_of_experience_age_plus_minus_one)
        # print(timeit.timeit(code_test, number=10000))
    return render(request, 'sharingofexperience/home.html')


@login_required
def sharing_experiences_menu(request):
    user_age = age_calculation(request.user.birth_date)
    user_ages = [age for age in range(user_age) if age > LOWER_LIMIT_AGE_TO_BE_SHARED]

    user_sharing_of_experiences = SharingOfExperience.objects.filter(user_id_id=request.user.id)
    already_filled_ages = [sharing.experienced_age for sharing in user_sharing_of_experiences]

    context = {
        'user_ages': user_ages,
        'already_filled_ages': already_filled_ages
    }
    return render(request, 'sharingofexperience/sharing_experiences_menu.html', context=context)


def user_has_completed_all_his_sharings(request):
    count_user_sharing_of_experiences = len(SharingOfExperience.objects.filter(user_id_id=request.user.id))
    user_age = age_calculation(request.user.birth_date)

    # user_age - 1 as the user must wait his/her birthday to complete a sharing about the current year
    max_number_of_sharings_depends_on_user_age = user_age - 1 - LOWER_LIMIT_AGE_TO_BE_SHARED

    return count_user_sharing_of_experiences == max_number_of_sharings_depends_on_user_age


def user_has_already_access_to_all_sharings_age_minus_plus(request):
    user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access

    if 'full access sharings age plus minus' in user_profile_model_dictionnary:
        return user_profile_model_dictionnary['user_profile_model_dictionnary'] is True
    else:
        return False


def user_profile_model_dictionnary_only_numeric_keys_kept(user_profile_model_dictionnary):
    user_profile_model_dictionnary_only_numeric_keys = []
    # try/except not necessary; but better practice ?
    for key in user_profile_model_dictionnary:
        if key.isnumeric():
            user_profile_model_dictionnary_only_numeric_keys.append(key)
    return user_profile_model_dictionnary_only_numeric_keys


def access_to_some_sharings_age_minus_plus(request, number_of_sharings_to_give_access):
    # list of existing sharings to which the user has already access
    user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access
    # >>> {"22": true, "23": true, "26": true, "credits": 5}

    # only numeric keys kept for research with Q objects
    user_profile_model_dictionnary_only_numeric_keys = user_profile_model_dictionnary_only_numeric_keys_kept(user_profile_model_dictionnary)

    # list of existing sharings to which the user does not yet have access (plus or minus a year old)
    sharing_of_experiences_from_others = queryset_sharing_of_experiences_from_others(request)
    # >>> <QuerySet [<SharingOfExperience: SharingOfExperience object (23)>, ...>

    sharings_from_others_user_does_have_access_yet = sharing_of_experiences_from_others.filter(
        ~Q(id__in=user_profile_model_dictionnary_only_numeric_keys)
    )

    allocation_of_new_sharings_of_experiences(request, number_of_sharings_to_give_access, sharings_from_others_user_does_have_access_yet)


def access_to_new_sharings_of_experience(request):
    user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access

    if user_has_completed_all_his_sharings(request) and not user_has_already_access_to_all_sharings_age_minus_plus(request):
        user_profile_model_dictionnary['full access sharings age plus minus'] = True
        # added 2023 03 31
        add_credits_to_user(user_profile_model_dictionnary, DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION)
        user_profile_model.save()

    else:
        count_sharings_by_user = len(SharingOfExperience.objects.filter(user_id_id=request.user.id))
        # print('count_sharings_by_user', count_sharings_by_user)
        if count_sharings_by_user % NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS == 0:
            # print('count_sharings_by_user', count_sharings_by_user)
            access_to_some_sharings_age_minus_plus(request, DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION)


@login_required
def sharing_an_experience_create(request, experienced_age):
    # form = SharingOfExperienceFormCreate
    # return render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})

    global url_to_be_returned_for_experience_create_view

    age_already_filled_boolean = sharing_of_experience_already_created_for_an_age(request, experienced_age)
    experienced_age_to_be_created_low_enough_boolean = experienced_age_to_be_created_lower_than_user_age_boolean(experienced_age, request)

    # initial version
    # if request.method == 'POST':
    if request.method == 'POST' and experienced_age_to_be_created_low_enough_boolean and not age_already_filled_boolean:

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

            access_to_new_sharings_of_experience(request)

            return redirect('sharing_experiences_menu')
    else:
        form = SharingOfExperienceFormCreate()

    context = {
        'experienced_age': experienced_age,
    }

    url_to_be_returned = url_to_be_returned_for_experience_create_view(
        request, experienced_age_to_be_created_low_enough_boolean, age_already_filled_boolean,
        experienced_age, form, context)
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
        sharing_of_experience = sharing_of_experience_search[0]
        if sharing_of_experience.user_id == request.user:
            if request.method == 'POST':
                form = SharingOfExperienceFormCreate(request.POST, instance=sharing_of_experience)
                if form.is_valid():
                    form.save()
                    return redirect('sharing_experiences_menu')
            else:
                form = SharingOfExperienceFormCreate(instance=sharing_of_experience)

            context = {
                'experienced_age': sharing_of_experience.experienced_age,
            }

            return render(
                request,
                'sharingofexperience/sharing_an_experience_update.html',
                {'form': form, 'context': context}
            )
        else:
            return render(request, 'sharingofexperience/not_your_experience.html')


@login_required
def learning_from_others(request):
    # initial version
    # sharing_of_experiences_from_others = queryset_sharing_of_experiences_from_others(request)
    # for sharing_of_experience in sharing_of_experiences_from_others:
    #    sharing_of_experience.total_likes_calculation()

    sharings_of_experiences_to_display = []
    sharings_not_yet_accessible = False

    user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access

    if 'dictionary initialisation' in user_profile_model_dictionnary:
        if user_profile_model_dictionnary['dictionary initialisation'] == 1:
            return redirect('home')

    at_least_a_numeric_key_is_true = False
    for key in user_profile_model_dictionnary:
        if key.isnumeric():
            if user_profile_model_dictionnary[key]:
                at_least_a_numeric_key_is_true = True
                break

    user_profile_model_dictionnary_int = [int(key) for key in user_profile_model_dictionnary if key.isnumeric()]

    if at_least_a_numeric_key_is_true is True:
        sharings_of_experiences_to_display = SharingOfExperience.objects.filter(id__in=user_profile_model_dictionnary_int)
        for sharing in sharings_of_experiences_to_display:
            sharing.total_likes_calculation()

    if at_least_a_numeric_key_is_true is False:
        # if 'credits' in user_profile_model_dictionnary:
        #    if user_profile_model_dictionnary['credits'] > 1:
        #        sharings_not_yet_accessible = True
        sharings_not_yet_accessible = True

    if 'full access sharings age plus minus' in user_profile_model_dictionnary:
        if user_profile_model_dictionnary['full access sharings age plus minus'] is True:
            sharings_of_experiences_to_display = queryset_sharing_of_experiences_from_others(request)

    context = {
        'sharing_of_experiences': sharings_of_experiences_to_display,
        'COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS': COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS,
        'NUMBER_OF_AVAILABLE_PAST_OR_FUTURE_SHARINGS_WHEN_SPEND_CREDITS': NUMBER_OF_AVAILABLE_PAST_OR_FUTURE_SHARINGS_WHEN_SPEND_CREDITS,
        'past_sharings': "past_sharings",
        'future_sharings': "future_sharings",
        'sharings_not_yet_accessible': sharings_not_yet_accessible
    }
    return render(request, 'sharingofexperience/learning_from_others.html', context=context)


@login_required
def like_a_sharing_of_experience(request, id_sharing_of_experience_to_be_liked):
    print("like : to be done ; with a if sharing of experience instance . property (to be created : list of sharing exp the request.user has access) = add a like from request.user in dico ; else redirect")
    sharing_of_experience_to_be_liked = SharingOfExperience.objects.filter(id=id_sharing_of_experience_to_be_liked)[0]
    sharing_of_experience_to_be_liked.receive_like(request.user.id)

    return redirect('learning_from_others')


@login_required
def spend_credits(request, past_or_future_sharings):
    message = ""
    user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
    user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access
    user_credits = user_profile_model_dictionnary['credits']

    if user_credits >= COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS:
        user_age = age_calculation(request.user.birth_date)
        user_profile_model_dictionnary_only_numeric_keys = user_profile_model_dictionnary_only_numeric_keys_kept(user_profile_model_dictionnary)

        if past_or_future_sharings == "past_sharings":
            past_ages_before_gap = [age for age in range(LOWER_LIMIT_AGE_TO_BE_SHARED, user_age - GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES)]
            past_or_future_sharings_from_other_users = SharingOfExperience.objects.filter(
                ~Q(user_id_id=request.user.id) & Q(experienced_age__in=past_ages_before_gap) & ~Q(id__in=user_profile_model_dictionnary_only_numeric_keys)
            )
        elif past_or_future_sharings == "future_sharings":
            future_ages_after_gap = [age for age in range(user_age + GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES + 1, HIGHER_LIMIT_AGE_TO_BE_SHARED)]
            past_or_future_sharings_from_other_users = SharingOfExperience.objects.filter(
                ~Q(user_id_id=request.user.id) & Q(experienced_age__in=future_ages_after_gap) & ~Q(id__in=user_profile_model_dictionnary_only_numeric_keys)
            )

        queryset_is_empty = past_or_future_sharings_from_other_users.count() == 0
        if queryset_is_empty is False:
            allocation_of_new_sharings_of_experiences(request, NUMBER_OF_AVAILABLE_PAST_OR_FUTURE_SHARINGS_WHEN_SPEND_CREDITS, past_or_future_sharings_from_other_users)
            # initial version : user_credits -= COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS
            user_profile_model_after_allocation_of_credits = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=request.user.id)
            user_profile_model_dictionnary_after_allocation_of_credits = user_profile_model_after_allocation_of_credits.sharing_of_experiences_user_has_access
            user_profile_model_dictionnary_after_allocation_of_credits['credits'] -= COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS
            user_profile_model_after_allocation_of_credits.save()
        elif queryset_is_empty is True:
            message = "You have enough credits to access past or futures experiences shares; however, our database is not yet enough complete to satisfy your demand. Please try again later. Thanks for your comprehension"

    else:
        message = "You do not have enough credits {0} to access past or futures experiences shares".format(COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS)

    # print(message)
    request.session['message'] = message
    return redirect('learning_from_others')
