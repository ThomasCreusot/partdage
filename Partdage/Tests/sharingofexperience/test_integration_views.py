from datetime import datetime
import pytest

from django.urls import reverse
from django.test import Client
from django.contrib import auth

from pytest_django.asserts import assertTemplateUsed

from authentication.models import User
from sharingofexperience.models import ProfileModelSharingOfExperiencesUserHasAccess, SharingOfExperience

from sharingofexperience.views import ACCESS_TO_SHARINGS_MINIMUM_NUMBER, GAP_OF_YEARS_FROM_USER_AGE_FOR_DISPLAYING_EXPERIENCES, LOWER_LIMIT_AGE_TO_BE_SHARED
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

        # initial version
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
        """Tests if a user logged-in -> can access sharing_experiences_menu view with rigth content + tests the context value
        
        Scenario : 
        User A gets a request towards sharing_experiences_menu
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

