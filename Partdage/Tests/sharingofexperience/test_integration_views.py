from datetime import date, datetime, timedelta

import pytest

from django.urls import reverse
from django.test import Client
from django.contrib import auth

from pytest_django.asserts import assertTemplateUsed

from authentication.models import User
from sharingofexperience.models import ProfileModelSharingOfExperiencesUserHasAccess, SharingOfExperience

from sharingofexperience.views import ACCESS_TO_SHARINGS_MINIMUM_NUMBER, GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES, LOWER_LIMIT_AGE_TO_BE_SHARED, DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION, NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS
from sharingofexperience.views import age_calculation

"""
Organisation tests en classes
Pourquoi utiliser une classe de test ?  Pour :
-regrouper l’ensemble des tests d’une classe ;
-définir un environnement fixe pour l'exécution des méthodes de test ;
-éliminer la duplication du code commun pour tous les cas de test ;
-faciliter le refactoring des tests. 

Cette classe de test portera le nom de la classe à tester, précédé par Test
Perso je partirai bien sur une classe par view !
et chaque méthode de cette classe serait un scenario : propre.


gestion d’une bdd temporaire avec décorateur @pytest.mark.django_db
--> remplace les mocks ? Absolument pas car ce decorateur va juste faire en sorte que la base de donnees soit dans un etat correct ca ne la remplace pas

Tester URL : 
voir cours

Tester vues: 
voir cours

Tester modèles: 
voir cours -> les méthodes des modèles.


Client django pour lancer une requete
Le framework Django fournit un client de test afin de pouvoir simuler les requêtes HTTP sur notre application
from django.test import Client
client = Client()

Faites une requête GET
client = Client()
client.get('/path/', {'key1': 'data1', 'key2': 'data2’})
Equivalent à une requête GET sur l’URL :/path/?key1=data1&key2=data2.

Faites une requête POST
client = Client()
client.post('/path/', {'key1': 'data1', 'key2': 'data2’})
Equivalent à une requête POST sur l’URL/path/et avec une en-tête HTTP contenant key1=data1&key2=data2.

Syntaxe
class TestIndexView:
    def setup_method(self, method):
        #fonction appelée lors du lancement d'un test unitaire faisant partie d'une classe

    def test_signup_view(self):
        assert 1 == 1


    def teardown_method(self, method):
        #fonction appelée à la fin d'un test unitaire faisant partie d'une classe
"""


class TestAuthenticationViews():
    @pytest.mark.django_db
    def test_signup_page_and_login_page_right_credentials(self):
        """Tests if a user can sign-up and log-in + creation of a ProfileModel object during first
        connection"""

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

        temp_user = client.post(reverse('signup'), credentials)
        assert ProfileModelSharingOfExperiencesUserHasAccess.objects.all().count() == 0

        response = client.post(reverse('login'), {'username': 'test_user_signup', 'password': 'TestUserPassword'})
        assert response.status_code == 302
        assert response.url == reverse('home')
        # in views.py : try/except ProfileModelSharingOfExperiencesUserHasAccess.
        # sharing_of_experiences_user_has_access = {"dictionary initialisation": 1}
        assert ProfileModelSharingOfExperiencesUserHasAccess.objects.all().count() == 1

        # Test that the user is well authenticated -> to be studied.
        # user = auth.get_user(client)
        # assert user.is_authenticated


    @pytest.mark.django_db
    def test_signup_page_and_login_page_wrong_credentials(self):
        """Tests if a user can not log-in with wrong credentials"""

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

        temp_user = client.post(reverse('signup'), credentials)
        response = client.post(reverse('login'), {'username': 'test_user_signup', 'password': 'WrongPassword'})
        assert response.status_code == 200

        content = response.content.decode()
        assert content.find("Invalid credentials.") != -1 


class TestIndexView():

    def test_index_user_not_logged_in(self):
        """Tests if a user not logged-in can access index view with rigth content"""

        client = Client()
        path = reverse('index')
        response = client.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/index.html")
        assert content.find("<h1>Welcome !</h1>") != -1 
        assert content.find(">Login</a></button>") != -1 


    @pytest.mark.django_db
    def test_index_user_logged_in(self):
        """Tests if a user logged-in can access index view with rigth content"""

        test_user_A = User.objects.create(
                username = 'test_user_A',
                password = 'test_user_A',
                birth_date = '2000-01-31',
                email = 'user_A@mail.com',
            )
        test_user_A.save()
        
        client_test_user_A = Client()
        client_test_user_A.force_login(test_user_A)
        
        path = reverse('index')
        response = client_test_user_A.get(path)
        content = response.content.decode()
        
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/index.html")
        assert content.find("<h1>Welcome !</h1>") != -1
        assert content.find(">Home</a></button>") != -1
        assert content.find("Log out</a>") != -1


class TestHomeView:

    @pytest.mark.django_db
    def test_home_user_has_already_access_to_sharings(self):
        """Tests if a user logged in + who has already access to sharings of experiences -> can access home with rigth content and its dictionnary is not modified
        Note : We consider that User A has already access to sharings as its profile_model dictionary is
        {'credits': 1,} instead of {"dictionary initialisation": 1}
        
        Scenario : 
        User A and User B 
        User A has a profile model with credits (so we can consider it has already access to sharings as its dictionary does not contain "dictionary initialisation")
        User B has shared an experience
        User A logs-in the application and makes a GET request towards Home page.
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
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B.save()

        # User A makes a GET request towards home
        path = reverse('home')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/home.html")
        assert content.find(">Sharing experiences</a></button>") != -1 
        assert content.find(">Learing from other people</a></button>") != -1 

        # Test that user A dictionnary is unmodified
        expected_value = {'credits': 1,}
        assert test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access == expected_value


    @pytest.mark.django_db
    def test_home_user_has_not_access_to_sharings_yet(self):
        """Tests if a user logged in + who has already access to sharings of experiences -> can access home with rigth content and its dictionnary updated
        Note : We consider that User A has NOT already access to sharings as its profile_model dictionary is {"dictionary initialisation": 1}
        Note : the ages of user A and shared experience of user B impacts the test : if too much difference: then, 5 credits are allowed; 
        if enough close : then, 4 credits + a new key in the dictionnary

        Scenario : 
        User A (age) and User B 
        User A has a profile model with "dictionary initialisation" --> 
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
        assert content.find(">Sharing experiences</a></button>") != -1 
        assert content.find(">Learing from other people</a></button>") != -1 

        # Test that user A dictionnary is updated
        # expected_value = {'credits': ACCESS_TO_SHARINGS_MINIMUM_NUMBER}  # --> as a credit is allowed to a sharing
        expected_value = {str(test_sharing_user_B_1.id): True, 'credits': ACCESS_TO_SHARINGS_MINIMUM_NUMBER -1}

        # does not work : print(test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access)
        # >>> {'dictionary initialisation': 1}
        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access
        # print(user_profile_model_dictionnary)
        # >>> {'credits': 5} or {2: True, 'credits': 4} ;  depending on ages

        assert user_A_profile_model_dictionnary == expected_value

    @pytest.mark.django_db
    def test_home_user_not_logged_in(self):
        """Tests if a user not logged in -> can access home with rigth content"""

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

        # User A makes a GET request towards home
        path = reverse('home')
        response = client_test_user_A.get(path)
        assert response.status_code == 302
        assert response.url == '/login/?next=/home/'


class TestSharing_experiences_menuView:

    @pytest.mark.django_db
    def test_menu_user_logged_in(self):
        """Tests if a user logged-in -> can access sharing_experiences_menu view with rigth content + tests the context value + presence of html buttons
        
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
        assert content.find("<p>Sharing my experiences</p>") != -1 
        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/sharing_experiences_menu.html")

        # Test context
        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)
        test_user_A_ages = [age for age in range(test_user_A_age) if age > LOWER_LIMIT_AGE_TO_BE_SHARED]
        # print("user_ages", user_ages)
        # print('response', response.context[0]['user_ages'])
        assert test_user_A_ages == response.context[0]['user_ages']

        # Test presence of the first and last buttons
        assert content.find(">{0}</a></button>".format(LOWER_LIMIT_AGE_TO_BE_SHARED+1)) != -1 
        assert content.find(">{0}</a></button>".format(test_user_A_age-1)) != -1 


    @pytest.mark.django_db
    def test_menu_user_not_logged_in(self):
        """Tests if a user not logged-in -> can NOT access sharing_experiences_menu view"""

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
        """Tests if a user not logged-in -> can NOT access sharing_an_experience_create view"""

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
        Tests that a user who meets the conditions:
        - logged-in
        - + valid form
        - + no sharing is already created for the age concerned by the post request
        - + the age concerned by the post request is lower than the actual age of the user 
        - + which has completed all his/her sharings yet -> for this point; the age of user A will evolve each year in order to make the present test sustainable over time 

        -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        -> POST method : can access sharing_an_experience_create view with rigth content (redirection to menu)
        -> tests that the sharing of experience is well recorded in the database
        -> access given to all sharings from other users (age +/- GAP)

        Scenario : 
        Creation of users A and B
        Creation of user A profile model
        Creation of sharings (user B) : a sharing corresponding to age of user A and another too high to be accessed by user A by default
        User A makes a GET request towards sharing_an_experience_create and then a POST request with valid form and valid age and so complete all his sharings.
        """

        # Users creation and connection 
        # Note : the age of user A will evolve each year in order to make the present test sustainable over time 
        # the goal is that User A has only one age to complete in order to complete all his sharings
        # LOWER_LIMIT_AGE_TO_BE_SHARED (=10 initialy) ; on the website, an user can create a sharing from LOWER_LIMIT_AGE_TO_BE_SHARED + 1 year
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
        # Creation of sharings (user B) : a sharing corresponding to age of user A and another too high to be accessed by user A by default
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

        # Test that User A -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_create and so access the form
        # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()

        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_create.html")
        assert content_get.find('<form action="" method="post">') != -1
        assert content_get.find('<input type="submit" value="Send">') != -1



        # User A makes a request towards sharing_an_experience_create with valid form and valid age and so complete all his sharings
        # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })

        # Test that User A -> POST method : can access sharing_an_experience_create view with rigth content (redirection to menu)
        assert response_post.status_code == 302
        assert response_post.url == reverse('sharing_experiences_menu')

        # Test that -> the sharing of experience is well recorded in the database
        number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
        assert number_of_sharings_in_database_before_post_request_by_userA + 1 == number_of_sharings_in_database_after_post_request_by_userA

        # Test that User A -> access given to all sharings from other users (age +/- GAP)
        # print(test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access)
        # >>> {'credits': 1}
        
        # initial : 
        # expected_value = {str(test_sharing_user_B_age_userA.id): True, 'credits': ACCESS_TO_SHARINGS_MINIMUM_NUMBER -1}
        # reflexion -> The access is not given to test_sharing_user_B_age_userA as full access is given
        expected_value = {'credits': 1 + DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION, 'full access sharings age plus minus': True}

        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access

        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_creation_of_sharing_all_conditions_meet_and_user_did_not_completed_all_his_sharings(self):
        """
        Tests that a user who meets the conditions :
        - logged-in
        - + valid form
        - + no sharing is already created for the age concerned by the post request
        - + the age concerned by the post request is lower than the actual age of the user 
        - + which has not completed all his/her sharings yet 
        - + the number of sharings % NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS == 0


        -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        -> POST method : can access sharing_an_experience_create view with rigth content (redirection to menu)
        -> tests that the sharing of experience is well recorded in the database
        -> as the number of sharings % NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS == 0 --> access given to credits and/or some (but not all) sharings from other users (age +/- GAP)

        Scenario : 
        Creation of users A and B
        Creation of user A profile model
        Creation of sharings (user B) : a sharing corresponding to age of user A and another too high to be accessed by user A by default
        User A makes a GET request towards sharing_an_experience_create and then a POST request with valid form and valid age and so create a sharing.

        Note : For x in range(NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS) : creation of sharings --> then test the update of user_profile_model_dictionnary with sharings id and/or credits
        Note : The tested action is done via access_to_some_sharings_age_minus_plus() which calls allocation_of_new_sharings_of_experiences()
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
        # Creation of sharings (user B) : a sharing corresponding to age of user A and another too high to be accessed by user A by default
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

        # Test that User A -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_create and so access the form
        # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()

        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_create.html")
        assert content_get.find('<form action="" method="post">') != -1
        assert content_get.find('<input type="submit" value="Send">') != -1


        for i in range(NUMBER_OF_PARTICIPATION_TO_GET_ACCESS_TO_NEW_SHARINGS):
            # User A makes a POST request towards sharing_an_experience_create with valid form and valid age and so create a sharing
            # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
            # + i  for the boucle + the assertion of well recording
            path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1 + i])
            response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })

            # Test that User A -> POST method : can access sharing_an_experience_create view with rigth content (redirection to menu)
            assert response_post.status_code == 302
            assert response_post.url == reverse('sharing_experiences_menu')

            # Test that -> the sharing of experience is well recorded in the database
            number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
            assert number_of_sharings_in_database_before_post_request_by_userA + 1 + i == number_of_sharings_in_database_after_post_request_by_userA

            
        # Test that User A -> access given to all sharings from other users (age +/- GAP)
        # print(test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access)
        # >>> {'credits': 1}
        
        # Note : credits : +1 is the initial value (when user A dictionary was created) ; -1 is because of the access given to a sharing of experience of user B
        expected_value = {str(test_sharing_user_B_age_userA.id): True, 'credits': 1 + DEFAULT_NUMBER_GIVE_ACCESS_TO_SHARINGS_AT_EACH_PARTICIPATION -1}

        user_A_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_A_profile_model_dictionnary = user_A_profile_model.sharing_of_experiences_user_has_access

        assert user_A_profile_model_dictionnary == expected_value


    @pytest.mark.django_db
    def test_creation_of_sharing_invalid_form(self):
        """
        Tests that a user who meets the conditions except that :
        - the form is not valid (Description field not filled in)

        -> error message

        -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        -> POST method : no redirection
        -> tests that the sharing of experience is NOT recorded in the database


        Scenario : 
        Creation of user A 
        User A makes a GET request towards sharing_an_experience_create and then a POST request with an INvalid form and valid age and so create a sharing
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

        # Test that User A -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_create.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_create and so access the form
        # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()

        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_create.html")
        assert content_get.find('<form action="" method="post">') != -1
        assert content_get.find('<input type="submit" value="Send">') != -1

        # User A makes a POST request towards sharing_an_experience_create with INvalid form and valid age and so does NOT create a sharing
        # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_post = client_test_user_A.post(path_post, {'description': ''})


        # Test that User A -> POST method : no redirection
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/sharing_an_experience_create.html")
        #content_post = response_post.content.decode()  # --> No new text/message

        # Test that -> the sharing of experience is NOT recorded in the database
        number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
        assert number_of_sharings_in_database_before_post_request_by_userA + 0 == number_of_sharings_in_database_after_post_request_by_userA


    @pytest.mark.django_db
    def test_creation_of_sharing_age_already_filled(self):
        """
        Tests that a user who meets the conditions except that :
        - The age concerned by the post request is already filled (a sharing of experience already exist for this user at this age)

        -> redirection towards update view
        code : redirect('sharing_an_experience_update', sharing_of_experience_already_created_id)

        -> GET method : redirection towards update view
        -> POST method : redirection towards update view
        -> tests that the sharing of experience is NOT recorded in the database

        Scenario : 
        Creation of user A 
        Creation of a first sharing of experience for User A 
        User A makes a GET request towards sharing_an_experience_create and then a POST request with an valid form but the age is not
        valid as it corresponds to the age of the previously created sharing of experience
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
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_A_first.save()

        number_of_sharings_in_database_before_post_request_by_userA = len(SharingOfExperience.objects.all())

        # User A makes a GET request towards sharing_an_experience_create and then a POST request with an valid form but the age is not
        # valid as it corresponds to the age of the previously created sharing of experience

        # Test that User A -> GET method: redirection towards update view 
        # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_get = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_get = client_test_user_A.get(path_get)
        assert response_get.status_code == 302
        assert response_get.url == '/sharing_an_experience_update/{0}/'.format(test_sharing_user_A_first.id)

        # User A makes a POST request towards sharing_an_experience_create with valid form but not valid age and so does not create a sharing
        # +1 year because menu values for creation of sharings begins at LOWER_LIMIT_AGE_TO_BE_SHARED + 1 
        path_post = reverse('sharing_an_experience_create', args=[LOWER_LIMIT_AGE_TO_BE_SHARED + 1])
        response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })

        # Tests that User A -> POST method : redirection towards update view
        assert response_post.status_code == 302
        assert response_post.url == '/sharing_an_experience_update/{0}/'.format(test_sharing_user_A_first.id)

        # Test that -> the sharing of experience is NOT recorded in the database
        number_of_sharings_in_database_after_post_request_by_userA = len(SharingOfExperience.objects.all())
        assert number_of_sharings_in_database_before_post_request_by_userA + 0 == number_of_sharings_in_database_after_post_request_by_userA


    @pytest.mark.django_db
    def test_creation_of_sharing_age_is_too_high(self):
        """Tests that a user who meets the conditions except that :
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
        # User A makes a GET request towards sharing_an_experience_create with a age under the lower limit and so does NOT access the form

        test_user_A_birthdate = datetime.strptime(test_user_A.birth_date, "%Y-%m-%d")
        test_user_A_age = age_calculation(test_user_A_birthdate)

        path_get = reverse('sharing_an_experience_create', args=[test_user_A_age])
        response_get = client_test_user_A.get(path_get)

        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/be_patient.html")
        content_get = response_get.content.decode()
        assert content_get.find("<p>Please wait until you are sure you have the necessary hindsight before entering this age.</p>") != -1 

        # User A makes a POST request towards sharing_an_experience_create with valid form and with a age under the lower limit and so does NOT access the form
        path_post = reverse('sharing_an_experience_create', args=[test_user_A_age])
        response_post = client_test_user_A.post(path_post, {'description': 'Description of the sharing of experience by user A', })

        # Test that User A -> POST method : go to page sharingofexperience/be_patient.html
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/be_patient.html")
        content_post = response_post.content.decode()
        assert content_post.find("<p>Please wait until you are sure you have the necessary hindsight before entering this age.</p>") != -1 


class TestSharing_an_experience_updateView:

    @pytest.mark.django_db
    def test_update_of_sharing_user_not_logged_in(self):
        """Tests if a user not logged-in -> can NOT access sharing_an_experience_update view"""

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
                moderator_validation = "NOP",
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
        Tests that a user who meets the conditions :
        - logged-in
        - updates a sharing of experience which exists
        - updates one of its own sharing of experience (not the ID of another user)
        - valid form

        -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        -> POST method : can access sharing_an_experience_update view with rigth content (redirection to menu)
        -> tests that the sharing of experience is well updated in the database

        Scenario : 
        Creation of users A
        Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        User A makes a GET request towards sharing_an_experience_update and then a POST request with valid form and valid sharing ID and so updates a sharing
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
        # Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        test_sharing_user_A = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_A.save()

        # Test that User A -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_update and so access the form
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()

        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_update.html")
        assert content_get.find('{0}</textarea>'.format(test_sharing_user_A.description)) != -1
        assert content_get.find('<input type="submit" value="Send">') != -1

        # User A makes a POST request towards sharing_an_experience_update with valid form and valid age and so updates a sharing
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_post = client_test_user_A.post(path_post, {'description': 'Updated description of the sharing of experience by user A', })

        # Test that User A -> POST method : can access sharing_an_experience_update view with rigth content (redirection to menu)
        assert response_post.status_code == 302
        assert response_post.url == reverse('sharing_experiences_menu')

        # Test that -> tests that the sharing of experience is well updated in the database
        updated_sharing_of_experience = SharingOfExperience.objects.filter(id=test_sharing_user_A.id)[0]

        expected_value = "Updated description of the sharing of experience by user A"

        assert updated_sharing_of_experience.description == expected_value


    @pytest.mark.django_db
    def test_update_of_sharing_which_does_not_exist(self):
        """
        Tests that a user who meets the conditions except that :
        - the id of the sharing asked to be updated does not exist

        -> GET method : go to page sharing_of_experience_not_yet_created.html
        -> POST method : go to page sharing_of_experience_not_yet_created.html
        
        Scenario : 
        Creation of users A
        Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        User A makes a GET request towards sharing_an_experience_update and then a POST request with valid form but NOT a valid sharing ID (does not exists) and so ca not update the sharing
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
        # Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        test_sharing_user_A = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "NOP",
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
        assert content_get.find('<p>Please create a sharing of exeprience before trying to update it.</p>') != -1

        # User A makes a POST request towards sharing_an_experience_update with valid form and valid age and so updates a sharing
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id + 1])
        response_post = client_test_user_A.post(path_post, {'description': 'Updated description of the sharing of experience by user A', })
        content_post = response_post.content.decode()

        # Test that User A -> POST method : go to page sharing_of_experience_not_yet_created.html
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/sharing_of_experience_not_yet_created.html")
        assert content_post.find('<p>Please create a sharing of exeprience before trying to update it.</p>') != -1

        # Test that -> tests that the sharing of experience is not updated in the database
        updated_sharing_of_experience = SharingOfExperience.objects.filter(id=test_sharing_user_A.id)[0]
        expected_value = "description test_sharing"
        assert updated_sharing_of_experience.description == expected_value


    @pytest.mark.django_db
    def test_update_of_sharing_of_another_user(self):
        """
        Tests that a user who meets the conditions except that :
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
        # Creation of sharings (user B) : a sharing corresponding to the minimal age + 1
        test_sharing_user_B = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_B.save()

        # Test that User A -> GET method : go to page not_your_experience.html
        # User A makes a GET request towards sharing_an_experience_update but with the id of a sharing corresponding to another user
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_B.id])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()

        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/not_your_experience.html")
        assert content_get.find('<p>Please do not try to modify a sharing of experience which is not your.</p>') != -1

        # User A makes a POST request towards sharing_an_experience_update but with the id of a sharing corresponding to another user
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_B.id])
        response_post = client_test_user_A.post(path_post, {'description': 'Updated description of the sharing of experience by user A', })
        content_post = response_post.content.decode()

        # Test that User A -> POST method :  go to page not_your_experience.html
        assert response_post.status_code == 200
        assertTemplateUsed(response_post, "sharingofexperience/not_your_experience.html")
        assert content_post.find('<p>Please do not try to modify a sharing of experience which is not your.</p>') != -1


    @pytest.mark.django_db
    def test_update_of_sharing_invalid_form(self):
        """
        Tests that a user who meets the conditions except that :
        - the form is invalid

        -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        -> POST method : no redirection

        Scenario : 
        Creation of users A
        Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        User A makes a GET request towards sharing_an_experience_update and then a POST request with valid form and a valid sharing ID but an INvalid form and so ca not update the sharing
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
        # Creation of sharings (user A) : a sharing corresponding to the minimal age + 1
        test_sharing_user_A = SharingOfExperience.objects.create(
                user_id = test_user_A,
                experienced_age = LOWER_LIMIT_AGE_TO_BE_SHARED + 1,
                description = "description test_sharing",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_user_A.save()

        # Test that User A -> GET method : url_to_be_returned = render(request, 'sharingofexperience/sharing_an_experience_update.html', {'form': form})
        # User A makes a GET request towards sharing_an_experience_update and so access the form
        path_get = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_get = client_test_user_A.get(path_get)
        content_get = response_get.content.decode()

        assert response_get.status_code == 200
        assertTemplateUsed(response_get, "sharingofexperience/sharing_an_experience_update.html")
        assert content_get.find('{0}</textarea>'.format(test_sharing_user_A.description)) != -1
        assert content_get.find('<input type="submit" value="Send">') != -1

        # User A makes a POST request towards sharing_an_experience_update with an INvalid form and valid age and so does NOT update a sharing
        path_post = reverse('sharing_an_experience_update', args=[test_sharing_user_A.id])
        response_post = client_test_user_A.post(path_post, {'description': '', })

        # Test that User A -> POST method : no redirection
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
        Tests that a couple user/sharing who meets the conditions:
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its profile model

        -> tests that the sharing of experience corresponding to userA age is well displayed
        -> tests that the sharing of experience which does not correspond to userA age is not displayed

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared two experiences : the first one corresponds to userA age, the second one is out of the range age_plus_minus (initially gap = 1 year) 
        User A logs-in the application and makes a GET request towards learning_from_others page.
        User A should have access to the sharing of experience corresponding to his/her age but no access to the sharing of experience which does not correspond to his/her
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
        # Reminder : + user dictionnary has a key corresponding to a sharing id equal to true in its profile model
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
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_1.description)) != -1 
        assert content.find("<p>Likes :") != -1 
        assert content.find('<button><a href="/like_a_sharing_of_experience/{0}/">Like</a></button>'.format(test_sharing_user_B_1.id)) != -1 
        # -> tests that the sharing of experience which does not correspond to userA age is not displayed
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_2.description)) == -1


    @pytest.mark.django_db
    def test_learning_from_others_all_conditions_meet_full_access(self):
        """
        Tests that a couple user/sharing who meets the conditions:
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model (redirection home)
        - + user dictionnary has NOT a key corresponding to a sharing id equal to true in its profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content (sharings_not_yet_accessible)

        - Note : for this test, the user has 'full access sharings age plus minus' = True in its profile model

        -> tests that the sharing of experience corresponding to userA age is well displayed even if the corresponding numeric key is not equal to one

        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared two experiences : the first one corresponds to userA age, the second one is out of the range age_plus_minus (initially gap = 1 year) 
        User A logs-in the application and makes a GET request towards learning_from_others page.
        User A should have access to the sharing of experience corresponding to his/her age but no access to the sharing of experience which does not correspond to his/her
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
        # Reminder : + user dictionnary has NOT a key corresponding to a sharing id equal to true in its profile model
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
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_1.description)) != -1 
        assert content.find("<p>Likes :") != -1 
        assert content.find('<button><a href="/like_a_sharing_of_experience/{0}/">Like</a></button>'.format(test_sharing_user_B_1.id)) != -1 
        # -> tests that the sharing of experience which does not correspond to userA age is not displayed
        assert content.find("<p>{0}</p>".format(test_sharing_user_B_2.description)) == -1



    @pytest.mark.django_db
    def test_learning_from_others_user_not_logged_in(self):
        """
        Tests that a couple user/sharing who meets the conditions:
        - user is NOT logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its profile model

        -> tests that the user is redirected towards home page
        
        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience which corresponds to userA age
        User A does NOT log-in the application and makes a GET request towards learning_from_others page.
        User A should NOT have access to the sharing of experience as he/she is not logged-in
        """

        pass


    @pytest.mark.django_db
    def test_learning_from_others_dictionary_initialisation_redirects_user(self):
        """
        Tests that a couple user/sharing who meets the conditions:
        - user is logged-in
        - + user dictionnary HAS 'dictionary initialisation' = 1 in its profile model (redirection home)
        - + user dictionnary has a key corresponding to a sharing id equal to true in its profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its profile model

        -> tests that the user is redirected towards home page
        
        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience which corresponds to userA age
        User A logs-in the application and makes a GET request towards learning_from_others page.
        User A should be redirected towards home page
        """

        pass


    @pytest.mark.django_db
    def test_learning_from_others_no_numeric_key_equal_to_true(self):
        """
        Tests that a couple user/sharing who meets the conditions:
        - user is logged-in
        - + user dictionnary does not have 'dictionary initialisation' = 1 in its profile model (redirection home)
        - + user dictionnary has NOT ANY key corresponding to a sharing id equal to true in its profile model
            ->at_least_a_numeric_key_is_true ; if not : impacts HTML content (sharings_not_yet_accessible)

        - Note : for this test, the user does not have 'full access sharings age plus minus' in its profile model

        -> tests that the 'sharings_not_yet_accessible' is displayed on HTML 
        
        Scenario : 
        Creation of users A and B and profile model of user A
        User B shared an experience which corresponds to userA age
        User A logs-in the application and makes a GET request towards learning_from_others page.
        User A should have access to a text "My main philosophy is ..."
        """

        pass

