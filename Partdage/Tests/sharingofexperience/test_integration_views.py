from django.urls import reverse
from django.test import Client
# from django.contrib import auth

import pytest
from pytest_django.asserts import assertTemplateUsed

from datetime import date, datetime, timedelta

from authentication.models import User
from sharingofexperience.models import ProfileModelSharingOfExperiencesUserHasAccess
from sharingofexperience.models import SharingOfExperience

from sharingofexperience.views import ACCESS_TO_SHARINGS_MINIMUM_NUMBER
from sharingofexperience.views import GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES
from sharingofexperience.views import LOWER_LIMIT_AGE_TO_BE_SHARED
from sharingofexperience.views import DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION
from sharingofexperience.views import NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS
from sharingofexperience.views import COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS
from sharingofexperience.views import age_calculation


class TestAuthenticationViews():

    @pytest.mark.django_db
    def test_signup_page_and_login_page_right_credentials(self):
        """
        Tests that an user can sign-up and log-in
        + tests creation of a ProfileModel object during first connection
        """

        client = Client()
        credentials = {
            'first_name': 'test_user_signup',
            'last_name': 'test_user_signup',
            'username': 'test_user_signup',
            'email': 'test_user_signup@mail.com',
            'password1': 'TestUserPassword',
            'password2': 'TestUserPassword',
            'birth_date': '2000-01-31',
        }
        client.post(reverse('signup'), credentials)
        assert ProfileModelSharingOfExperiencesUserHasAccess.objects.all().count() == 0

        response = client.post(reverse('login'), {'username': 'test_user_signup',
        'password': 'TestUserPassword'})
        assert response.status_code == 302
        assert response.url == reverse('home')
        assert ProfileModelSharingOfExperiencesUserHasAccess.objects.all().count() == 1

        # Test that the user is well authenticated -> to be studied.
        # user = auth.get_user(client)
        # assert user.is_authenticated

    @pytest.mark.django_db
    def test_signup_page_and_login_page_wrong_credentials(self):
        """Tests that an user can not log-in with wrong credentials"""

        client = Client()
        credentials = {
            'first_name': 'test_user_signup',
            'last_name': 'test_user_signup',
            'username': 'test_user_signup',
            'email': 'test_user_signup@mail.com',
            'password1': 'TestUserPassword',
            'password2': 'TestUserPassword',
            'birth_date': '2000-01-31',
        }
        client.post(reverse('signup'), credentials)
        response = client.post(reverse('login'), {'username': 'test_user_signup', 'password': 'WrongPassword'})
        content = response.content.decode()

        assert response.status_code == 200
        assert content.find("Invalid credentials.") != -1


class TestIndexView():

    def test_index_user_not_logged_in(self):
        """Tests that an user not logged-in can access index view with rigth content"""

        client = Client()
        path = reverse('index')
        response = client.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/index.html")
        assert content.find(">LOGIN</a></button>") != -1

    @pytest.mark.django_db
    def test_index_user_logged_in(self):
        """Tests that an user logged-in can access index view with rigth content"""

        test_user_A = User.objects.create(
                username='test_user_A',
                password='test_user_A',
                birth_date='2000-01-31',
                email='user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        path = reverse('index')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/index.html")
        assert content.find(">HOME</a></button>") != -1
        assert content.find("Log out</a>") != -1


class TestHomeView:

    @pytest.mark.django_db
    def test_home_user_has_already_access_to_sharings(self):
        """
        Tests that an user logged in and who has already access to sharings of experiences:
        -> can access home page with rigth content 
        -> its dictionnary is not modified
        Note : We consider that User A has already access to sharings as its profile_model
        dictionary is {'credits': 1,} instead of {"dictionary initialisation": 1}

        Scenario :
        Creation of User A and User B
        User A has a profile model with credits (so we can consider it has already access to
        sharings as its dictionary does not contain "dictionary initialisation")
        User B has shared an experience
        User A logs-in the application and makes a GET request towards Home page
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        test_sharing_user_B = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = 11,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B.save()

        # User A makes a GET request towards home page
        path = reverse('home')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/home.html")
        assert content.find(">PARTAGER MES EXPERIENCES</a></button>") != -1 
        assert content.find(">APPRENDRE DES AUTRES</a></button>") != -1 

        # Tests that user A dictionnary is not modified
        expected_value = {'credits': 1,}
        assert test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access == expected_value


    @pytest.mark.django_db
    def test_home_user_has_not_access_to_sharings_yet(self):
        """
        Tests that an user logged in and who has already access to sharings of experiences 
        -> can access home with rigth content 
        -> its dictionnary is well updated
        Note : We consider that User A has NOT already access to sharings as its profile_model
        dictionary is {"dictionary initialisation": 1}
        Note : the ages of user A and shared experience of user B impacts the test: if too much
        difference (related to the GAP value (see constants imports)): then, 5 credits are allowed;
        if enough close : then, 4 credits + a new key in the dictionnary

        Scenario : 

        User A (age) and User B 
        User A has a profile model with "dictionary initialisation"
        User B shared two experiences : the first one corresponds to userA age, the second one is out of the range age_plus_minus (initially gap = 1 year) 
        User A logs-in the application and makes a GET request towards Home page.
        User A should have a dictionnary updated with credits instead of {"dictionary initialisation": 1}
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'dictionary initialisation': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # User A makes a GET request towards home
        path = reverse('home')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/home.html")
        assert content.find(">PARTAGER MES EXPERIENCES</a></button>") != -1 
        assert content.find(">APPRENDRE DES AUTRES</a></button>") != -1 

        # Test that user A dictionnary is updated
        expected_value = {str(test_sharing_user_B_1.id): True, 'credits': ACCESS_TO_SHARINGS_MINIMUM_NUMBER -1}
        # does not work : print(test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access)
        # >>> {'dictionary initialisation': 1}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_home_user_has_not_access_to_sharings_yet_moderator_validation_is_NOP(self):
        """
        Double verification of the test_home_user_has_not_access_to_sharings_yet test : in the
        present test, sharings of experience are not yet validated by the moderator. Then, they
        are not yet visible by the user

        Tests that an user logged in and who has already access to sharings of experiences 
        -> can access home with rigth content 
        -> its dictionnary is well updated
        Note : We consider that User A has NOT already access to sharings as its profile_model
        dictionary is {"dictionary initialisation": 1}
        Note : the ages of user A and shared experience of user B impacts the test: if too much
        difference (related to the GAP value (see constants imports)): then, 5 credits are allowed;
        if enough close : then, 4 credits + a new key in the dictionnary

        Scenario : 

        User A (age) and User B 
        User A has a profile model with "dictionary initialisation"
        User B shared two experiences : the first one corresponds to userA age, the second one is out of the range age_plus_minus (initially gap = 1 year) 
        User A logs-in the application and makes a GET request towards Home page.
        User A should have a dictionnary updated with credits instead of {"dictionary initialisation": 1}
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'dictionary initialisation': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # User A makes a GET request towards home
        path = reverse('home')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/home.html")
        assert content.find(">PARTAGER MES EXPERIENCES</a></button>") != -1 
        assert content.find(">APPRENDRE DES AUTRES</a></button>") != -1 

        # Test that user A dictionnary is updated
        expected_value = {'credits': ACCESS_TO_SHARINGS_MINIMUM_NUMBER}
        # does not work : print(test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access)
        # >>> {'dictionary initialisation': 1}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_home_user_not_logged_in(self):
        """Tests that an user not logged in -> can access home with rigth content"""

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        # user does not not log in : client_test_user_A.force_login(test_user_A)

        path = reverse('home')
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == '/login/?next=/home/'


class TestSharing_experiences_menuView:

    @pytest.mark.django_db
    def test_menu_user_logged_in(self):
        """
        Tests that an user logged-in 
        -> can access sharing_experiences_menu view with rigth content 
        -> tests the context value + presence of html buttons

        Scenario : 
        User A makes a request towards sharing_experiences_menu
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        # User A makes a GET request towards sharing_experiences_menu
        path = reverse('sharing_experiences_menu')
        response = client_test_user_A.get(path)

        content = response.content.decode()
        assert content.find("<p><strong>COMMENT PARTDAGER ?</strong></p>") != -1 
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/sharing_experiences_menu.html")

        # Tests context
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)
        test_user_A_ages = [age for age in range(test_user_A_age) if age > LOWER_LIMIT_AGE_TO_BE_SHARED]
        assert test_user_A_ages == response.context[0]['user_ages']

        # Tests presence of the first and last buttons
        assert content.find(">{0}</a></button>".format(LOWER_LIMIT_AGE_TO_BE_SHARED+1)) != -1 
        assert content.find(">{0}</a></button>".format(test_user_A_age-1)) != -1 


    @pytest.mark.django_db
    def test_menu_user_not_logged_in(self):
        """Tests that an user not logged-in -> can NOT access sharing_experiences_menu view"""

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        # user does not not log in : client_test_user_A.force_login(test_user_A)

        # User A makes a GET request towards sharing_experiences_menu
        path = reverse('sharing_experiences_menu')
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == '/login/?next=/sharing_experiences_menu/'


class TestSharing_an_experience_createView:

    @pytest.mark.django_db
    def test_creation_of_sharing_user_not_logged_in(self):
        """Tests that an user not logged-in -> can NOT access sharing_an_experience_create view"""

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        # user does not not log in : client_test_user_A.force_login(test_user_A)

        # User A makes a GET request towards sharing_an_experience_create
        path = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED+1])
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == '/login/?next=/sharing_an_experience_create/{0}/'.format(LOWER_LIMIT_AGE_TO_BE_SHARED+1)


    @pytest.mark.django_db
    def test_creation_of_sharing_all_conditions_meet_and_user_completed_all_his_sharings(self):
        """
        Tests that an user who meets all the conditions:
        - logged-in
        - + valid form
        - + no sharing is already created for the age concerned by the post request
        - + the age concerned by the post request is lower than the actual age of the user 
        - + which has completed all his/her sharings yet -> for this point; the age of user A will
        evolve each year in order to make the present test sustainable over time

        -> GET method: url_to_be_returned =
        render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        -> POST method: can access sharing_an_experience_create view with rigth content
        (redirection to menu)
        -> tests that the sharing of experience is well recorded in the database
        -> access given to all sharings from other users (age +/- GAP)

        Scenario : 
        Creation of users A and B
        Creation of user A profile model
        Creation of sharings (user B): a sharing corresponding to age of user A and another too
        high to be accessed by user A by default
        User A makes a GET request towards sharing_an_experience_create and then a POST request
        with valid form and valid age and so complete all his sharings
        """

        # Users creation and connection 
        # Note : the age of user A will evolve each year in order to make the present test
        # sustainable over time 
        # The goal is that User A has only one age to complete in order to complete all his
        # sharings
        # LOWER_LIMIT_AGE_TO_BE_SHARED (=10 initialy); on the website, an user can create a sharing
        # from LOWER_LIMIT_AGE_TO_BE_SHARED + 1 year
        today = date.today()
        # Explanation of birth_date_user_A_for_a_relevant_test calculation:
            # 365.25 to account leap years ; 
            # + 1 year as on the website, a user can create a sharing from LOWER_LIMIT_AGE_TO_BE_SHARED + 1 year ; 
              # e.g : LOWER_LIMIT_AGE_TO_BE_SHARED is 10 years old <=> the lowest age an user can complete is 11 years old
            # + 1 year as the user must have experienced a year before sharing an experience about it
              # e.g. : the lowest age an user can complete is 11 years old <=> the user must have at least 12 years old
            # + 1 day to be sure the birthday has passed
        birth_date_user_A_for_a_relevant_test = today - timedelta(days = 365.25 * (LOWER_LIMIT_AGE_TO_BE_SHARED + 1 + 1) +1)
        birth_date_user_A_for_a_relevant_test_str = str(birth_date_user_A_for_a_relevant_test)

        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = birth_date_user_A_for_a_relevant_test_str,
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_age_userA = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_age_userA.save()

        test_sharing_user_B_higher_than_age_userA = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age + GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES + 1,  # innacessible by user A by default
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_higher_than_age_userA.save()

        number_of_sharings_in_database_before_post_request_by_userA = len(SharingOfExperience.objects.all())

        # Test that User A -> GET method : url_to_be_returned = 
        # render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_create and so access the form
        # + 1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_create.html")
        assert content_get.find('<form action="" method="post">') != -1
        assert content_get.find('<input type="submit" value="Partdager">') != -1

        # User A makes a POST request towards sharing_an_experience_create with valid form and
        # valid age and so complete all his sharings
        # + 1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        # Test that User A -> POST method: can access sharing_an_experience_create view with rigth
        # content (redirection to menu)
        path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })
        assert response_post.status_code == 302
        assert response_post.url == reverse('sharing_experiences_menu')

        # Test that -> the sharing of experience is well recorded in the database
        number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
        assert number_of_sharings_in_database_before_post_request_by_userA + 1 == number_of_sharings_in_database_after_post_request_by_userA

        # Note: The access is not given to test_sharing_user_B_age_userA as full access is given
        expected_value = {'credits': 1 + DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION, 'full access sharings age plus minus': True}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value
        

    @pytest.mark.django_db
    def test_creation_of_sharing_all_conditions_meet_and_user_did_not_completed_all_his_sharings(self):
        """
        Tests that an user who meets the conditions :
        - logged-in
        - + valid form
        - + no sharing is already created for the age concerned by the post request
        - + the age concerned by the post request is lower than the actual age of the user 
        - + which has not completed all his/her sharings yet 
        - + the number of sharings % NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS == 0

        -> GET method : url_to_be_returned =
        render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        -> POST method : can access sharing_an_experience_create view with rigth content
        (redirection to menu)
        -> tests that the sharing of experience is well recorded in the database
        -> as the number of sharings % NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS == 0
        access given to credits and/or some (but not all) sharings from other users (age +/- GAP)

        Scenario : 
        Creation of users A and B
        Creation of user A profile model
        Creation of sharings (user B): a sharing corresponding to age of user A and another too
        high to be accessed by user A by default
        User A makes a GET request towards sharing_an_experience_create and then a POST request
        with valid form and valid age and so create a sharing.

        Note: For x in range(NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS): creation of
        sharings --> then test the update of user_profile_model_dictionnary with sharings id and/or
        credits
        Note: The tested action is done via access_to_some_sharings_age_minus_plus() which calls
        allocation_of_new_sharings_of_experiences()
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_age_userA = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_age_userA.save()

        test_sharing_user_B_higher_than_age_userA = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age + GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES + 1,  # innacessible by user A by default
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_higher_than_age_userA.save()

        number_of_sharings_in_database_before_post_request_by_userA = len(SharingOfExperience.objects.all())

        # Test that User A -> GET method: url_to_be_returned =
        # render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_create and so access the form
        # +1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_create.html")
        assert content_get.find('<form action="" method="post">') != -1
        assert content_get.find('<input type="submit" value="Partdager">') != -1

        for i in range(NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS):
            # User A makes a POST request towards sharing_an_experience_create with valid form and
            # valid age and so create a sharing
            # + 1 year because menu values for creation of sharings begins at
            # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
            # + i  for the boucle + the assertion of well recording
            # Test that User A -> POST method : can access sharing_an_experience_create view with
            # rigth content (redirection to menu)
            path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1 + i])
            response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })
            assert response_post.status_code == 302
            assert response_post.url == reverse('sharing_experiences_menu')

            # Test that -> the sharing of experience is well recorded in the database
            number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
            assert number_of_sharings_in_database_before_post_request_by_userA + 1 + i == number_of_sharings_in_database_after_post_request_by_userA
            
        # Test that User A -> access given to all sharings from other users (age +/- GAP)
        # Note : credits: + 1 is the initial value (when user A dictionary was created) ;-1 is
        # because of the access given to a sharing of experience of user B
        expected_value = {str(test_sharing_user_B_age_userA.id): True, 'credits': 1 + DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION -1}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_creation_of_sharing_all_conditions_meet_and_user_did_not_completed_all_his_sharings_moderator_validation_is_NOP(self):
        """
        Double verification of the test_creation_of_sharing_all_conditions_meet_and_user_did_not_completed_all_his_sharings test :
        in the present test, sharings of experience are not yet validated by the moderator.
        Then, they are not yet visible by the user.

        Tests that an user who meets the conditions :
        - logged-in
        - + valid form
        - + no sharing is already created for the age concerned by the post request
        - + the age concerned by the post request is lower than the actual age of the user 
        - + which has not completed all his/her sharings yet 
        - + the number of sharings % NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS == 0

        -> GET method : url_to_be_returned =
        render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        -> POST method : can access sharing_an_experience_create view with rigth content
        (redirection to menu)
        -> tests that the sharing of experience is well recorded in the database
        -> as the number of sharings % NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS == 0
        access given to credits and/or some (but not all) sharings from other users (age +/- GAP)

        Scenario : 
        Creation of users A and B
        Creation of user A profile model
        Creation of sharings (user B): a sharing corresponding to age of user A and another too
        high to be accessed by user A by default
        User A makes a GET request towards sharing_an_experience_create and then a POST request
        with valid form and valid age and so create a sharing.

        Note: For x in range(NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS): creation of
        sharings --> then test the update of user_profile_model_dictionnary with sharings id and/or
        credits
        Note: The tested action is done via access_to_some_sharings_age_minus_plus() which calls
        allocation_of_new_sharings_of_experiences()
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_age_userA = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_age_userA.save()

        test_sharing_user_B_higher_than_age_userA = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age + GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES + 1,  # innacessible by user A by default
                description = "description test_sharing",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_higher_than_age_userA.save()

        number_of_sharings_in_database_before_post_request_by_userA = len(SharingOfExperience.objects.all())

        # Test that User A -> GET method: url_to_be_returned =
        # render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_create and so access the form
        # +1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_create.html")
        assert content_get.find('<form action="" method="post">') != -1
        assert content_get.find('<input type="submit" value="Partdager">') != -1

        for i in range(NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS):
            # User A makes a POST request towards sharing_an_experience_create with valid form and
            # valid age and so create a sharing
            # + 1 year because menu values for creation of sharings begins at
            # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
            # + i  for the boucle + the assertion of well recording
            # Test that User A -> POST method : can access sharing_an_experience_create view with
            # rigth content (redirection to menu)
            path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1 + i])
            response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })
            assert response_post.status_code == 302
            assert response_post.url == reverse('sharing_experiences_menu')

            # Test that -> the sharing of experience is well recorded in the database
            number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
            assert number_of_sharings_in_database_before_post_request_by_userA + 1 + i == number_of_sharings_in_database_after_post_request_by_userA
            
        # Test that User A -> access given to all sharings from other users (age +/- GAP)
        # Note : credits: + 1 is the initial value (when user A dictionary was created) ;-1 is
        # because of the access given to a sharing of experience of user B
        expected_value = {'credits': 1 + DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_creation_of_sharing_invalid_form(self):
        """
        Tests that a user who meets all the conditions except that :
        - the form is not valid (Description field not filled in)

        -> error message

        -> GET method: url_to_be_returned =
        render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        -> POST method: no redirection
        -> tests that the sharing of experience is NOT recorded in the database

        Scenario : 
        Creation of user A 
        User A makes a GET request towards sharing_an_experience_create and then a POST request
        with an INvalid form and valid age and so create a sharing
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        number_of_sharings_in_database_before_post_request_by_userA = len(SharingOfExperience.objects.all())

        # Test that User A -> GET method : url_to_be_returned =
        # render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_create and so access the form
        # +1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_create.html")
        assert content_get.find('<form action="" method="post">') != -1
        assert content_get.find('<input type="submit" value="Partdager">') != -1

        # User A makes a POST request towards sharing_an_experience_create with INvalid form and
        # valid age and so does NOT create a sharing
        # +1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        # Test that User A -> POST method : no redirection
        path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_post = client_test_user_A.post(path_post, {'description': ''})
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/sharing_an_experience_create.html")
        # content_post = response_post.content.decode()  # --> No new text/message

        # Test that -> the sharing of experience is NOT recorded in the database
        number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
        assert number_of_sharings_in_database_before_post_request_by_userA + 0 == number_of_sharings_in_database_after_post_request_by_userA


    @pytest.mark.django_db
    def test_creation_of_sharing_age_already_filled(self):
        """
        Tests that an user who meets the conditions except that :
        - The age concerned by the post request is already filled (a sharing of experience already
        exist for this user at this age)

        -> redirection towards update view
        code : redirect('sharing_an_experience_update', sharing_of_experience_already_created_id)

        -> GET method : redirection towards update view
        -> POST method : redirection towards update view
        -> tests that the sharing of experience is NOT recorded in the database

        Scenario : 
        Creation of user A 
        Creation of a first sharing of experience for User A 
        User A makes a GET request towards sharing_an_experience_create and then a POST request
        with an valid form but the age is not valid as it corresponds to the age of the previously
        created sharing of experience
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()
        
        # Sharings of experience creation 
        # Creation of a first sharing of experience for User A 
        test_sharing_user_A_first = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_A_first.save()

        number_of_sharings_in_database_before_post_request_by_userA = len(SharingOfExperience.objects.all())

        # User A makes a GET request towards sharing_an_experience_create and then a POST request
        # with an valid form but the age is not valid as it corresponds to the age of the previously created sharing of experience

        # Test that User A -> GET method: redirection towards update view 
        # +1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        assert response_get.status_code == 302
        assert response_get.url == '/sharing_an_experience_update/{0}/'.format(test_sharing_user_A_first.id)

        # User A makes a POST request towards sharing_an_experience_create with valid form but not
        # valid age and so does not create a sharing
        # +1 year because menu values for creation of sharings begins at
        # LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        # Tests that User A -> POST method : redirection towards update view
        path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })
        assert response_post.status_code == 302
        assert response_post.url == '/sharing_an_experience_update/{0}/'.format(test_sharing_user_A_first.id)

        # Test that -> the sharing of experience is NOT recorded in the database
        number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
        assert number_of_sharings_in_database_before_post_request_by_userA + 0 == number_of_sharings_in_database_after_post_request_by_userA


    @pytest.mark.django_db
    def test_creation_of_sharing_age_is_too_high(self):
        """Tests that an user who meets all the conditions except that :
        - The age concerned by the post request is too high compared to user current age

        -> GET method : go to page sharingofexperience/be_patient.html
        -> POST method : go to page sharingofexperience/be_patient.html
        
        Scenario : 
        Creation of user A 
        User A makes a GET request towards sharing_an_experience_create and then a POST request
        with a valid form and an INvalid age (current age) and so does NOT create a sharing
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Test that User A -> GET method : go to page sharingofexperience/be_patient.html
        # User A makes a GET request towards sharing_an_experience_create with a age under the
        # lower limit and so does NOT access the form
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        path_get = reverse('sharing_an_experience_create', args=[test_user_A_age])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/be_patient.html")
        assert content_get.find("<p>Merci d'attendre d'avoir le recul nécéssaire pour renseigner cette age.</p>") != -1 

        # User A makes a POST request towards sharing_an_experience_create with valid form and with
        # an age under the lower limit and so does NOT access the form
        # Test that User A -> POST method : go to page sharingofexperience/be_patient.html
        path_post = reverse('sharing_an_experience_create', args=[test_user_A_age])
        response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })
        content_post = response_post.content.decode()
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/be_patient.html")
        assert content_post.find("<p>Merci d'attendre d'avoir le recul nécéssaire pour renseigner cette age.</p>") != -1 


class TestSharing_an_experience_updateView:

    @pytest.mark.django_db
    def test_update_of_sharing_user_not_logged_in(self):
        """Tests that an user not logged-in -> can NOT access sharing_an_experience_update view"""

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        # user does not log in : client_test_user_A.force_login(test_user_A)

        # Sharings of experience creation 
        # Creation of a first sharing of experience for User A 
        test_sharing_user_A = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_A.save()

        # User A makes a GET request towards sharing_an_experience_update
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_get = client_test_user_A.get(path_get)
        assert response_get.status_code == 302
        assert response_get.url == '/login/?next=/sharing_an_experience_update/{0}/'.format(test_sharing_user_A.id)

        # User A makes a POST request towards sharing_an_experience_update
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_post = client_test_user_A.post(path_post, {'description': 'Updated description of the sharing of experience by user A', })
        assert response_post.status_code == 302
        assert response_post.url == '/login/?next=/sharing_an_experience_update/{0}/'.format(test_sharing_user_A.id)


    @pytest.mark.django_db
    def test_update_of_sharing_all_conditions_meet(self):
        """
        Tests that an user who meets all the conditions :
        - logged-in
        - updates a sharing of experience which exists
        - updates one of its own sharing of experience (not the ID of another user)
        - valid form

        -> GET method : url_to_be_returned =
        render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        -> POST method : can access sharing_an_experience_update view with rigth content
        (redirection to menu)
        -> tests that the sharing of experience is well updated in the database

        Scenario : 
        Creation of users A
        Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        User A makes a GET request towards sharing_an_experience_update and then a POST request
        with valid form and valid sharing ID and so updates a sharing
        """

        # Users creation and connection
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        # Sharings of experience creation 
        test_sharing_user_A = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_A.save()

        # Test that User A -> GET method : url_to_be_returned =
        # render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_update and so access the form
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_update.html")
        assert content_get.find('{0}</textarea>'.format(test_sharing_user_A.description)) != -1
        assert content_get.find('<input type="submit" value="Mise à jour">') != -1

        # User A makes a POST request towards sharing_an_experience_update with valid form and
        # valid age and so updates a sharing
        # Test that User A -> POST method : can access sharing_an_experience_update view with rigth
        # content (redirection to menu)
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_post = client_test_user_A.post(path_post, {'description': 'Updated description of the sharing of experience by user A', })
        assert response_post.status_code == 302
        assert response_post.url == reverse('sharing_experiences_menu')

        # Test that -> tests that the sharing of experience is well updated in the database
        updated_sharing_of_experience = SharingOfExperience.objects.filter(id=test_sharing_user_A.id)[0]
        expected_value = "Updated description of the sharing of experience by user A"
        assert updated_sharing_of_experience.description == expected_value


    @pytest.mark.django_db
    def test_update_of_sharing_which_does_not_exist(self):
        """
        Tests that an user who meets the conditions except that :
        - the id of the sharing asked to be updated does not exist

        -> GET method : go to page sharing_of_experience_not_yet_created.html
        -> POST method : go to page sharing_of_experience_not_yet_created.html
        
        Scenario : 
        Creation of users A
        Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        User A makes a GET request towards sharing_an_experience_update and then a POST request
        with valid form but NOT a valid sharing ID (does not exists) and so ca not update the
        sharing
        """

        # Users creation and connection
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        # Sharings of experience creation 
        test_sharing_user_A = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_A.save()

        # Test that User A -> GET method : go to page sharing_of_experience_not_yet_created.html
        # User A makes a GET request towards sharing_an_experience_update and so access the form
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_of_experience_not_yet_created.html")
        assert content_get.find("<p>Merci de créer un partage d'expérience avant d'essayer de le modifier.</p>") != -1

        # User A makes a POST request towards sharing_an_experience_update with valid form and valid age and so updates a sharing
        # Test that User A -> POST method : go to page sharing_of_experience_not_yet_created.html
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id + 1])
        response_post = client_test_user_A.post(path_post, {'description': 'Updated description of the sharing of experience by user A', })
        content_post = response_post.content.decode()
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/sharing_of_experience_not_yet_created.html")
        assert content_post.find("<p>Merci de créer un partage d'expérience avant d'essayer de le modifier.</p>") != -1

        # Test that -> tests that the sharing of experience is not updated in the database
        updated_sharing_of_experience = SharingOfExperience.objects.filter(id=test_sharing_user_A.id)[0]
        expected_value = "description test_sharing"
        assert updated_sharing_of_experience.description == expected_value


    @pytest.mark.django_db
    def test_update_of_sharing_of_another_user(self):
        """
        Tests that an user who meets the conditions except that :
        - the id of the sharing asked to be updated was created by another user

        -> GET method : go to page not_your_experience.html
        -> POST method : go to page not_your_experience.html
        
        Scenario : 
        Creation of users A and B
        Creation of sharings (user B) : a sharing corresponding to the minimal age + 1
        User A makes a GET request towards sharing_an_experience_update and then a POST request with valid form but NOT a valid sharing ID (id of sharing created by user B) and so ca not update the sharing
        """

        # Users creation and connection
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        test_sharing_user_B = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B.save()

        # Test that User A -> GET method : go to page not_your_experience.html
        # User A makes a GET request towards sharing_an_experience_update but with the id of a
        # sharing corresponding to another user
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_B.id])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/not_your_experience.html")
        assert content_get.find("<p>Merci de ne pas essayer de modifier un partage d'expérience qui n'est pas le votre.</p>") != -1

        # User A makes a POST request towards sharing_an_experience_update but with the id of a sharing corresponding to another user
        # Test that User A -> POST method :  go to page not_your_experience.html
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_B.id])
        response_post = client_test_user_A.post(path_post, {'description': 'Updated description of the sharing of experience by user A', })
        content_post = response_post.content.decode()
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/not_your_experience.html")
        assert content_post.find("<p>Merci de ne pas essayer de modifier un partage d'expérience qui n'est pas le votre.</p>") != -1


    @pytest.mark.django_db
    def test_update_of_sharing_invalid_form(self):
        """
        Tests that an user who meets the conditions except that :
        - the form is invalid

        -> GET method : url_to_be_returned =
        render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        -> POST method : no redirection

        Scenario : 
        Creation of users A
        Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        User A makes a GET request towards sharing_an_experience_update and then a POST request
        with valid form and a valid sharing ID but an INvalid form and so ca not update the sharing
        """

        # Users creation and connection
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        # Sharings of experience creation 
        test_sharing_user_A = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_A.save()

        # Test that User A -> GET method : url_to_be_returned =
        # render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_update and so access the form
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()
        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_update.html")
        assert content_get.find('{0}</textarea>'.format(test_sharing_user_A.description)) != -1
        assert content_get.find('<input type="submit" value="Mise à jour">') != -1

        # User A makes a POST request towards sharing_an_experience_update with an INvalid form and
        # valid age and so does NOT update a sharing
        # Test that User A -> POST method : no redirection
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_post = client_test_user_A.post(path_post, {'description': '', })
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/sharing_an_experience_update.html")
        #content_post = response_post.content.decode()  # --> No new text/message

        # Test that -> tests that the sharing of experience is NOT updated in the database
        not_updated_sharing_of_experience = SharingOfExperience.objects.filter(id=test_sharing_user_A.id)[0]
        expected_value = "description test_sharing"
        assert not_updated_sharing_of_experience.description == expected_value


class TestLearning_from_othersView:

    @pytest.mark.django_db
    def test_learning_from_others_all_conditions_meet_not_full_access(self):
        """
        Tests that a couple user/sharing which meets the conditions:
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile
        model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content
            (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the sharing of experience corresponding to userA age is well displayed
        -> tests that the sharing of experience which does not correspond to userA age is not
        displayed

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared two experiences : the first one corresponds to userA age, the second one is
        out of the range age_plus_minus (initially gap = 1 year) 
        User A logs-in the application and makes a GET request towards learning_from_others page
        User A should have access to the sharing of experience corresponding to his/her age but no
        access to the sharing of experience which does not correspond to his/her
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared two experiences : the first one corresponds to userA age, the second one
        # is out of the range age_plus_minus (initially gap = 1 year) 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # Profile models creation 
        # Reminder : + user dictionnary has a key corresponding to a sharing id equal to true in
        # its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards learning_from_others page
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()
        # User A should have access to the sharing of experience corresponding to his/her age but no access to the sharing of experience which does not correspond to his/her
        # -> tests that the sharing of experience corresponding to userA age is well displayed
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_1.description)) != -1 
        assert content.find("<p>Likes :") != -1 
        assert content.find('<button><a href="/like_a_sharing_of_experience/{0}/">Like</a></button>'.format(test_sharing_user_B_1.id)) != -1 
        # -> tests that the sharing of experience which does not correspond to userA age is not displayed
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_2.description)) == -1


    @pytest.mark.django_db
    def test_learning_from_others_all_conditions_meet_full_access(self):
        """
        Tests that a couple user/sharing who all meets the conditions:
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has NOT a key corresponding to a sharing id equal to true in its
        profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content
            (sharings_not_yet_accessible)

        - Note : for this test, the user has 'full access sharings age plus minus' = True in its
        profile model

        -> tests that the sharing of experience corresponding to userA age is well displayed even
        if the corresponding numeric key is not equal to one

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared two experiences : the first one corresponds to userA age, the second one is
        out of the range age_plus_minus (initially gap = 1 year) 
        User A logs-in the application and makes a GET request towards learning_from_others page
        User A should have access to the sharing of experience corresponding to his/her age but no
        access to the sharing of experience which does not correspond to his/her
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared two experiences : the first one corresponds to userA age, the second one is
        # out of the range age_plus_minus (initially gap = 1 year) 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # Profile models creation 
        # Reminder : + user dictionnary has NOT a key corresponding to a sharing id equal to true
        # in its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 0, 'full access sharings age plus minus' : True},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards learning_from_others page
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()
        # User A should have access to the sharing of experience corresponding to his/her age but no access to the sharing of experience which does not correspond to his/her
        # -> tests that the sharing of experience corresponding to userA age is well displayed
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_1.description)) != -1 
        assert content.find("<p>Likes :") != -1 
        assert content.find('<button><a href="/like_a_sharing_of_experience/{0}/">Like</a></button>'.format(test_sharing_user_B_1.id)) != -1 
        # -> tests that the sharing of experience which does not correspond to userA age is not displayed
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_2.description)) == -1


    @pytest.mark.django_db
    def test_learning_from_others_all_conditions_meet_full_access_moderator_validation_is_NOP(self):
        """
        Double verification of the test_learning_from_others_all_conditions_meet_full_access test :
        in the present test, sharings of experience are not yet validated by the moderator.
        Then, they are not yet visible by the user.
        
        Tests that a couple user/sharing who all meets the conditions:
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has NOT a key corresponding to a sharing id equal to true in its
        profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content
            (sharings_not_yet_accessible)

        - Note : for this test, the user has 'full access sharings age plus minus' = True in its
        profile model

        -> tests that the sharing of experience corresponding to userA age is well displayed even
        if the corresponding numeric key is not equal to one

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared two experiences : the first one corresponds to userA age, the second one is
        out of the range age_plus_minus (initially gap = 1 year) 
        User A logs-in the application and makes a GET request towards learning_from_others page
        User A should have access to the sharing of experience corresponding to his/her age but no
        access to the sharing of experience which does not correspond to his/her
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared two experiences : the first one corresponds to userA age, the second one is
        # out of the range age_plus_minus (initially gap = 1 year) 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # Profile models creation 
        # Reminder : + user dictionnary has NOT a key corresponding to a sharing id equal to true
        # in its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 0, 'full access sharings age plus minus' : True},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards learning_from_others page
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()
        # User A should have access to the sharing of experience corresponding to his/her age but no access to the sharing of experience which does not correspond to his/her
        # -> tests that the sharing of experience corresponding to userA age is well displayed
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_1.description)) == -1 
        assert content.find("<p>Likes :") == -1 
        assert content.find('<button><a href="/like_a_sharing_of_experience/{0}/">Like</a></button>'.format(test_sharing_user_B_1.id)) == -1 
        # -> tests that the sharing of experience which does not correspond to userA age is not displayed
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_2.description)) == -1


    @pytest.mark.django_db
    def test_learning_from_others_user_not_logged_in(self):
        """Tests that an user not logged-in -> can NOT access learning_from_others view"""

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        # user does not not log in : client_test_user_A.force_login(test_user_A)

        # User A makes a GET request towards learning_from_others
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == '/login/?next=/learning_from_others/'


    @pytest.mark.django_db
    def test_learning_from_others_dictionary_initialisation_redirects_user(self):
        """
        Tests that a couple user/sharing who all meets the conditions:
        - user is logged-in
        - + user dictionnary HAS 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile
        model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content
            (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user is redirected towards home page
        -> tests that the redirection towards home page reinitialised the user profile model
        dictionary

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience which corresponds to userA age
        User A logs-in the application and makes a GET request towards learning_from_others page
        User A should be redirected towards home page
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared two experiences : the first one corresponds to userA age, the second one is out of the range age_plus_minus (initially gap = 1 year) 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # Profile models creation 
        # Reminder : + user dictionnary has a key corresponding to a sharing id equal to true in
        # its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 1, 'dictionary initialisation' : 1},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards learning_from_others page
        # User A should be redirected towards home page
        # -> tests that the user is redirected towards home page
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == reverse('home')

        # -> tests that the redirection towards home page reinitialised the user profile model
        # dictionary
        path = reverse('home')
        response = client_test_user_A.get(path)
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        expected_value = {str (test_sharing_user_B_1.id) : 1, 'credits': ACCESS_TO_SHARINGS_MINIMUM_NUMBER-1}
        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_learning_from_others_dictionary_initialisation_redirects_user_moderator_validation_is_NOP(self):
        """
        Double verification of the test_learning_from_others_dictionary_initialisation_redirects_user test :
        in the present test, sharings of experience are not yet validated by the moderator.
        Then, they are not yet visible by the user.

        Tests that a couple user/sharing who all meets the conditions:
        - user is logged-in
        - + user dictionnary HAS 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile
        model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content
            (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user is redirected towards home page
        -> tests that the redirection towards home page reinitialised the user profile model
        dictionary

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience which corresponds to userA age
        User A logs-in the application and makes a GET request towards learning_from_others page
        User A should be redirected towards home page
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared two experiences : the first one corresponds to userA age, the second one is out of the range age_plus_minus (initially gap = 1 year) 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # Profile models creation 
        # Reminder : + user dictionnary has a key corresponding to a sharing id equal to true in
        # its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 1, 'dictionary initialisation' : 1},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards learning_from_others page
        # User A should be redirected towards home page
        # -> tests that the user is redirected towards home page
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == reverse('home')

        # -> tests that the redirection towards home page reinitialised the user profile model
        # dictionary
        path = reverse('home')
        response = client_test_user_A.get(path)
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        expected_value = {str (test_sharing_user_B_1.id) : 1, 'credits': ACCESS_TO_SHARINGS_MINIMUM_NUMBER}
        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_learning_from_others_no_numeric_key_equal_to_true(self):
        """
        Tests that a couple user/sharing who all meets the conditions:
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has NOT ANY key corresponding to a sharing id equal to true in its
        profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content
            (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the 'sharings_not_yet_accessible' is displayed on HTML 
        
        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience which corresponds to userA age
        User A logs-in the application and makes a GET request towards learning_from_others page
        User A should not have access sharings of experience
        User A should have access to a text "My main philosophy is ..."
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared two experiences : the first one corresponds to userA age, the second one is
        # out of the range age_plus_minus (initially gap = 1 year) 
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        test_sharing_user_B_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_2.save()

        # Profile models creation 
        # Reminder : + user dictionnary has a NOT ANY key corresponding to a sharing id equal to
        # true in its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 0,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards learning_from_others page
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()
        # User A should NOT have access to the sharing of experience
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_1.description)) == -1 
        assert content.find("<p>Likes :") == -1 
        assert content.find('<button><a href="/like_a_sharing_of_experience/{0}/">Like</a></button>'.format(test_sharing_user_B_1.id)) == -1 
        assert content.find(">{0}</p>".format(test_sharing_user_B_2.description)) == -1
        # -> tests that the 'sharings_not_yet_accessible' is displayed on HTML 
        assert content.find("Ma philosophie actuelle principale est d'être ") != -1


class TestLike_a_sharing_of_experienceView:

    @pytest.mark.django_db
    def test_like_a_sharing_user_logged_in(self):
        """
        Tests that an user can like the sharing of experience of another user
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile
        model

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user can like the sharing of experience <=>
        sharing_of_experience.likes['likes'] -> user id

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience corresponding to user A age
        User A logs-in the application and makes a GET request
        towards like_a_sharing_of_experience()
        The sharing of experience gets a new like in its likes dictionary
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared an experience corresponding to userA age
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        # Profile models creation 
        # Reminder : + user dictionnary has a key corresponding to a sharing id equal to true in
        # its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards like_a_sharing_of_experience
        path = reverse('like_a_sharing_of_experience', args=[test_sharing_user_B_1.id])
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == reverse('learning_from_others')

        # -> tests that the user can like the sharing of experience <=>
        # sharing_of_experience.likes['likes'] -> user id
        liked_sharing_of_experience = SharingOfExperience.objects.filter(id = test_sharing_user_B_1.id)[0]
        expected_value = {'likes': {str(test_user_A.id): 1}}
        assert liked_sharing_of_experience.likes == expected_value


    @pytest.mark.django_db
    def test_like_a_sharing_user_not_logged_in(self):
        """
        Tests that an user not logged-in -> can NOT like a sharing of experience
        - user is not logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model
        (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile
        model

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user can NOT like the sharing of experience if not logged in
        <=> sharing_of_experience.likes['likes'] -> user id

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience corresponding to user A age
        User A does NOT log-in the application and makes a GET request towards
        like_a_sharing_of_experience()
        The sharing of experience DOES NOT get a new like in its likes dictionary
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        # user does not not log in : client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Sharings of experience creation 
        # User B shared an experience corresponding to userA age
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_1.save()

        # Profile models creation 
        # Reminder : + user dictionnary has a key corresponding to a sharing id equal to true in
        # its profile model
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {str (test_sharing_user_B_1.id) : 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # User A makes a GET request towards like_a_sharing_of_experience
        path = reverse('like_a_sharing_of_experience', args=[test_sharing_user_B_1.id])
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == '/login/?next=/like_a_sharing_of_experience/{0}/'.format(test_sharing_user_B_1.id)

        # -> tests that the user can NOT like the sharing of experience <=> sharing_of_experience.likes['likes'] -> user id
        liked_sharing_of_experience = SharingOfExperience.objects.filter(id = test_sharing_user_B_1.id)[0]
        expected_value = {'likes': {}}
        assert liked_sharing_of_experience.likes == expected_value


class TestSpend_creditsView:

    @pytest.mark.django_db
    def test_spend_credits_all_condition_met(self):
        """
        Tests that a user can spend credits to access past or futures sharings of experience
        - user is logged-in
        - user has enought credits to spend it 
        (2 * COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS)
        - there is at least a sharing he/she does not have access yet (both past and future)
        
        - Note : user dictionnary does not have 'dictionary initialisation' = 1 in its profile
        model (redirection home)
        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user can access two new sharings wich are not in the range
        'user_age - GAP ; user_age + GAP)

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared four experiences which are OUT of the range age_plus_minus
        (initially gap = 1 year) : two pasts and two futures experiences
        User A logs-in the application and makes two GET requests towards spend_creadits() : for
        past and future experiences
        The user has access to two sharings of experience which are OUT of the range age_plus_minus
        (initially gap = 1 year)
        Note : return redirect('learning_from_others')
        Note : user_credits -= COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS to be checked
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits' : 2*COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        # User B shared four experiences which are OUT of the range age_plus_minus
        # (initially gap = 1 year) : two pasts and two futures experiences
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_past_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-1,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_1.save()

        test_sharing_user_B_past_2= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-2,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_2.save()

        test_sharing_user_B_future_1 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_future_1.save()

        test_sharing_user_B_future_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+2,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_future_2.save()

        #-> Initially, user A does not have access to sharings wich are not in the range
        # 'user_age - GAP ; user_age + GAP)
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_past_1.description)) == -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_past_2.description)) == -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_future_1.description)) == -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_future_2.description)) == -1

        # User A makes a GET request towards spend_credits page
        path_past_experiences = reverse('spend_credits', args=['past_sharings'])
        response_past_experiences = client_test_user_A.get(path_past_experiences)
        assert response_past_experiences.status_code == 302
        assert response_past_experiences.url == reverse('learning_from_others')

        path_future_experiences = reverse('spend_credits', args=['future_sharings'])
        response_future_experiences = client_test_user_A.get(path_future_experiences)
        assert response_future_experiences.status_code == 302
        assert response_future_experiences.url == reverse('learning_from_others')

        #-> tests that the user can access two new sharings wich are not in the range
        # 'user_age - GAP ; user_age + GAP)
        # User A makes a GET request towards learning_from_others page (in reality : automated
        # with redirection)
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_past_1.description)) != -1 or content.find(">{0}</p>".format(test_sharing_user_B_past_2.description)) != -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_future_1.description)) != -1 or content.find(">{0}</p>".format(test_sharing_user_B_future_2.description)) != -1

        # Test that : user_credits -= COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS to be
        # checked
        expected_value_past1_future_1 = {str(test_sharing_user_B_past_1.id): True, str(test_sharing_user_B_future_1.id): True, 'credits': 0}
        expected_value_past1_future_2 = {str(test_sharing_user_B_past_1.id): True, str(test_sharing_user_B_future_2.id): True, 'credits': 0}
        expected_value_past2_future_1 = {str(test_sharing_user_B_past_2.id): True, str(test_sharing_user_B_future_1.id): True, 'credits': 0}
        expected_value_past2_future_2 = {str(test_sharing_user_B_past_2.id): True, str(test_sharing_user_B_future_2.id): True, 'credits': 0}

        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value_past1_future_1 or user_A_profile_model_dictionnary == expected_value_past1_future_2 or user_A_profile_model_dictionnary == expected_value_past2_future_1 or user_A_profile_model_dictionnary == expected_value_past2_future_2


    @pytest.mark.django_db
    def test_spend_credits_all_condition_met_moderator_validation_is_NOP(self):
        """
        Double verification of the test_spend_credits_all_condition_met test :
        in the present test, sharings of experience are not yet validated by the moderator.
        Then, they are not yet visible by the user.

        Tests that a user can spend credits to access past or futures sharings of experience
        - user is logged-in
        - user has enought credits to spend it 
        (2 * COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS)
        - there is at least a sharing he/she does not have access yet (both past and future)
        
        - Note : user dictionnary does not have 'dictionary initialisation' = 1 in its profile
        model (redirection home)
        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user can access two new sharings wich are not in the range
        'user_age - GAP ; user_age + GAP)

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared four experiences which are OUT of the range age_plus_minus
        (initially gap = 1 year) : two pasts and two futures experiences
        User A logs-in the application and makes two GET requests towards spend_creadits() : for
        past and future experiences
        The user has access to two sharings of experience which are OUT of the range age_plus_minus
        (initially gap = 1 year)
        Note : return redirect('learning_from_others')
        Note : user_credits -= COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS to be checked
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits' : 2*COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        # User B shared four experiences which are OUT of the range age_plus_minus
        # (initially gap = 1 year) : two pasts and two futures experiences
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_past_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-1,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_1.save()

        test_sharing_user_B_past_2= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-2,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_2.save()

        test_sharing_user_B_future_1 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_future_1.save()

        test_sharing_user_B_future_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+2,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B_future_2.save()

        #-> Initially, user A does not have access to sharings wich are not in the range
        # 'user_age - GAP ; user_age + GAP)
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_past_1.description)) == -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_past_2.description)) == -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_future_1.description)) == -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_future_2.description)) == -1

        # User A makes a GET request towards spend_credits page
        path_past_experiences = reverse('spend_credits', args=['past_sharings'])
        response_past_experiences = client_test_user_A.get(path_past_experiences)
        assert response_past_experiences.status_code == 302
        assert response_past_experiences.url == reverse('learning_from_others')

        path_future_experiences = reverse('spend_credits', args=['future_sharings'])
        response_future_experiences = client_test_user_A.get(path_future_experiences)
        assert response_future_experiences.status_code == 302
        assert response_future_experiences.url == reverse('learning_from_others')

        #-> tests that the user can access two new sharings wich are not in the range
        # 'user_age - GAP ; user_age + GAP)
        # User A makes a GET request towards learning_from_others page (in reality : automated
        # with redirection)
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find(">{0}</p>".format(test_sharing_user_B_past_1.description)) == -1 and content.find(">{0}</p>".format(test_sharing_user_B_past_2.description)) == -1
        assert content.find(">{0}</p>".format(test_sharing_user_B_future_1.description)) == -1 and content.find(">{0}</p>".format(test_sharing_user_B_future_2.description)) == -1

        # Test that : user_credits -= COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS to be
        # checked
        expected_value_past1_future_1 = {str(test_sharing_user_B_past_1.id): True, str(test_sharing_user_B_future_1.id): True, 'credits': 0}
        expected_value_past1_future_2 = {str(test_sharing_user_B_past_1.id): True, str(test_sharing_user_B_future_2.id): True, 'credits': 0}
        expected_value_past2_future_1 = {str(test_sharing_user_B_past_2.id): True, str(test_sharing_user_B_future_1.id): True, 'credits': 0}
        expected_value_past2_future_2 = {str(test_sharing_user_B_past_2.id): True, str(test_sharing_user_B_future_2.id): True, 'credits': 0}

        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary != expected_value_past1_future_1 and user_A_profile_model_dictionnary != expected_value_past1_future_2 and user_A_profile_model_dictionnary != expected_value_past2_future_1 and user_A_profile_model_dictionnary != expected_value_past2_future_2


    @pytest.mark.django_db
    def test_spend_credits_user_not_logged_in(self):
        """
        Tests that an user can NOT spend credits to access past or futures sharings as
        - user is NOT logged-in
        - user has enought credits to spend it
        (2 * COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS)
        - there is at least a sharing he/she does not have access yet (both past and future)
        
        - Note : user dictionnary does not have 'dictionary initialisation' = 1 in its profile
        model (redirection home)
        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared two experiences which are OUT of the range age_plus_minus
        (initially gap = 1 year) : a past and a future experience
        User A DOES NOT log-in the application and makes two GET requests towards spend_creadits():
        for past and future experiences
        The user has NOT access to the two sharings of experience which are OUT of the range
        age_plus_minus (initially gap = 1 year)
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        # user does not not log in : client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()


        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits' : 2*COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()


        # Sharings of experience creation 
        # User B shared four experiences which are OUT of the range age_plus_minus
        # (initially gap = 1 year) : two pasts and two futures experiences
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_past_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-1,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_1.save()

        test_sharing_user_B_past_2= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-2,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_2.save()

        test_sharing_user_B_future_1 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_future_1.save()

        test_sharing_user_B_future_2 = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+2,
                description = "description test_sharing test_sharing_user_B_2",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_future_2.save()

        # User A makes a GET request towards spend_credits page
        path_past = reverse('spend_credits', args=['past_sharings'])
        response_past = client_test_user_A.get(path_past)
        assert response_past.status_code == 302
        assert response_past.url == '/login/?next=/spend_credits/past_sharings/'

        path_future = reverse('spend_credits', args=['future_sharings'])
        response_future = client_test_user_A.get(path_future)
        assert response_future.status_code == 302
        assert response_future.url == '/login/?next=/spend_credits/future_sharings/'


    @pytest.mark.django_db
    def test_spend_credits_not_enough_credits(self):
        """
        Tests that a user can NOT spend credits to access past or futures sharings of experience if
        he/she has NO enough credits
        - user is logged-in
        - user has NOT enough credits to spend it
        (< COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS)
        - there is at least a sharing he/she does not have access yet (both past and future)
        
        - Note : user dictionnary does not have 'dictionary initialisation' = 1 in its profile
        model (redirection home)
        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user can NOT access a new sharing wich is not in the range
        user_age - GAP - user_age + GAP

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared two experiences which are OUT of the range age_plus_minus
        (initially gap = 1 year) : a past and a future experience
        User A logs-in the application and makes two GET requests towards spend_creadits(): for
        past and future experiences
        The user has NOT access to the two sharings of experience which are OUT of the range
        age_plus_minus (initially gap = 1 year)
        The user has access to the message = "You do not have enough credits ..."
        """

        # Users creation and connection 
        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username = 'test_user_B',
                password = 'test_user_B',
                birth_date = '2000-01-31',
                email = 'user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation 
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits' : COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS-1},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation 
        # User B shared four experiences which are OUT of the range age_plus_minus (initially gap = 1 year) : two pasts and two futures experiences
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        test_sharing_user_B_past_1= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-1,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_1.save()

        test_sharing_user_B_past_2= SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = test_user_A_age-GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES-2,
                description = "description test_sharing test_sharing_user_B_1",
                moderator_validation = "VAL",
                likes = {"likes": {}}
        )
        test_sharing_user_B_past_2.save()

        test_sharing_user_B_future_1 = SharingOfExperience.objects.create(
                user_id=test_user_B,
                experienced_age=test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+1,
                description="description test_sharing test_sharing_user_B_2",
                moderator_validation="VAL",
                likes={"likes": {}}
        )
        test_sharing_user_B_future_1.save()

        test_sharing_user_B_future_2 = SharingOfExperience.objects.create(
                user_id=test_user_B,
                experienced_age=test_user_A_age+GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES+2,
                description="description test_sharing test_sharing_user_B_2",
                moderator_validation="VAL",
                likes={"likes": {}}
        )
        test_sharing_user_B_future_2.save()

        # User A makes a GET request towards spend_credits page
        path_past_experiences = reverse('spend_credits', args=['past_sharings'])
        response_past_experiences = client_test_user_A.get(path_past_experiences)
        assert response_past_experiences.status_code == 302
        assert response_past_experiences.url == reverse('learning_from_others')

        path_future_experiences = reverse('spend_credits', args=['future_sharings'])
        response_future_experiences = client_test_user_A.get(path_future_experiences)
        assert response_future_experiences.status_code == 302
        assert response_future_experiences.url == reverse('learning_from_others')

        # The user has NOT access to the two sharings of experience which are OUT of the range
        # age_plus_minus (initially gap = 1 year)
        # The user has access to the message = "You do not have enough credits ..."

        # User A makes a GET request towards learning_from_others page (in reality : automated
        # with redirection)
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")

        # -> User A does not have access to sharings wich are not in the range 'user_age - GAP ; user_age + GAP)
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_past_1.description)) == -1
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_past_2.description)) == -1
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_future_1.description)) == -1
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_future_2.description)) == -1

        # The user has access to the message = "You do not have enough credits ..."
        assert content.find("You do not have enough credits {0} to access past or futures experiences shares".format(COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS)) != -1

        # Test that : user_credits did not change
        expected_value = {'credits': COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS-1}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value

    @pytest.mark.django_db
    def test_spend_credits_empty_queryset_of_sharings_to_buy_access_for(self):
        """
        Tests that an user can NOT spend credits to access past or futures sharings of experience
        - user is logged-in
        - user has enought credits to spend it
        (2 * COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS)
        - there is NOT ANY sharing he/she does not have access yet (neither past nor future)

        - Note : user dictionnary does not have 'dictionary initialisation' = 1 in its profile
        model (redirection home)
        - Note : for this test, the user does not have 'full access sharings age plus minus' in its
        profile model

        -> tests that the user can NOT access a new sharing wich is not in the range
        user_age - GAP - user_age + GAP
        -> tests that User has access to the message = "You have enough credits to access past or
        futures experiences shares; however, our database ..."
        -> tests that : user_credits are not spent

        Scenario :
        Creation of users A and B and profile model of user A
        User B did not shared any experiences
        User A logs-in the application and makes two GET requests towards spend_creadits(): for
        past and future experiences
        The user has NOT access to any sharings of experience (they do not exist)
        """

        # Users creation and connection
        test_user_A = User.objects.create(
                username='test_user_A',
                password='test_user_A',
                birth_date='2000-01-31',
                email='user_A@mail.com',
            )
        test_user_A.save()
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)

        test_user_B = User.objects.create(
                username='test_user_B',
                password='test_user_B',
                birth_date='2000-01-31',
                email='user_B@mail.com',
            )
        test_user_B.save()

        # Profile models creation
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user=test_user_A,
            sharing_of_experiences_user_has_access={'credits': 2*COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        # Sharings of experience creation
        # there is NOT ANY sharing he/she does not have access yet (neither past nor future)

        # User A makes a GET request towards spend_credits page (both past and future) : PAST
        path_past_experiences = reverse('spend_credits', args=['past_sharings'])
        response_past_experiences = client_test_user_A.get(path_past_experiences)
        assert response_past_experiences.status_code == 302
        assert response_past_experiences.url == reverse('learning_from_others')
        # -> Past : tests that the user can NOT access a new sharing wich is not in the range user_age - GAP - user_age + GAP
        path_past = reverse('learning_from_others')
        response_past = client_test_user_A.get(path_past)
        content_past = response_past.content.decode()
        assert response_past.status_code == 200
        assertTemplateUsed(response_past, "sharingofexperience/learning_from_others.html")
        assert content_past.find('<p>Likes :') == -1
        assert content_past.find('<button><a href="/like_a_sharing_of_experience/') == -1

        # User A makes a GET request towards spend_credits page (both past and future) : FUTURE
        path_future_experiences = reverse('spend_credits', args=['future_sharings'])
        response_future_experiences = client_test_user_A.get(path_future_experiences)
        assert response_future_experiences.status_code == 302
        assert response_future_experiences.url == reverse('learning_from_others')
        # -> Future : tests that the user can NOT access a new sharing wich is not in the range user_age - GAP - user_age + GAP
        path_future = reverse('learning_from_others')
        response_future = client_test_user_A.get(path_future)
        content_future = response_future.content.decode()
        assert response_future.status_code == 200
        assertTemplateUsed(response_future, "sharingofexperience/learning_from_others.html")
        assert content_future.find('<p>Likes :') == -1
        assert content_future.find('<button><a href="/like_a_sharing_of_experience/') == -1

        # Both Past and future : User has access to the message = "You have enough credits to access past or futures experiences shares; however, our database ..."
        path = reverse('learning_from_others')
        response = client_test_user_A.get(path)
        content = response.content.decode()
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/learning_from_others.html")
        assert content.find("You have enough credits to access past or futures experiences shares; however") != -1

        # Test that : user_credits are not spent
        expected_value = {'credits': 2 * COST_IN_CREDITS_TO_ACCESS_PAST_OR_FUTURE_SHARINGS}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        assert user_A_profile_model_dictionnary == expected_value
