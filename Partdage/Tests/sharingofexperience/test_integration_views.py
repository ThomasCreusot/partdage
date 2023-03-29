import pytest

from django.urls import reverse
from django.test import Client
from django.contrib import auth

from pytest_django.asserts import assertTemplateUsed

from authentication.models import User
from sharingofexperience.models import ProfileModelSharingOfExperiencesUserHasAccess, SharingOfExperience


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
        """Tests if a user can sign-up and log-in"""

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

        # Test that the user is well authenticated -> to be studied.
        # user = auth.get_user(client)
        # assert user.is_authenticated

        # ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access = {"dictionary initialisation": 1}
        assert ProfileModelSharingOfExperiencesUserHasAccess.objects.all().count() == 1


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
        pass
        #initial version
        #test_user_A = User.objects.create(
        #        username = 'test_user_A',
        #        password = 'test_user_A',
        #        birth_date = '2000-01-31',
        #        email = 'user_A@mail.com',
        #    )
        #test_user_A.save()
        #
        #client_test_user_A = Client()
        #client_test_user_A.force_login(test_user_A)
        #
        #path = reverse('index')
        #response = client_test_user_A.get(path)
        #content = response.content.decode()
        #
        #assert response.status_code == 200
        #assertTemplateUsed(response, "sharingofexperience/index.html")
        #
        #assert content.find("<h1>Welcome !</h1>") != -1
        #assert content.find(">Home</a></button>") != -1
        #assert content.find("Log out</a>") != -1


class TestHomeView:

    @pytest.mark.django_db
    def test_home_user_has_already_access_to_sharings(self):
        """Tests if a user logged in + who has already access to sharings of experiences -> can access home with rigth content
        Scenario : 
        User A and User B log in the application
        
        TO BE COMPLETED

        User A access the sharings of experience of user B
        User B creates sharings of experience
        """

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

        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'credits': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()
        #print(test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharin)

        test_sharing_a = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = 11,
                description = "description test_sharing_a",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_a.save()

        path = reverse('home')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/home.html")
        assert content.find(">Sharing experiences</a></button>") != -1 
        assert content.find(">Learing from other people</a></button>") != -1 

    @pytest.mark.django_db
    def test_home_user_has_not_access_to_sharings_yet(self):

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

        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess = ProfileModelSharingOfExperiencesUserHasAccess.objects.create(
            user = test_user_A,
            sharing_of_experiences_user_has_access = {'dictionary initialisation': 1,},
        )
        test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.save()

        test_sharing_a = SharingOfExperience.objects.create(
                user_id = test_user_B,
                experienced_age = 11,
                description = "description test_sharing_a",
                moderator_validation = "NOP",
                likes = {"likes": {}}
        )
        test_sharing_a.save()

        path = reverse('home')
        response = client_test_user_A.get(path)
        content = response.content.decode()

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/home.html")
        assert content.find(">Sharing experiences</a></button>") != -1 
        assert content.find(">Learing from other people</a></button>") != -1 

        # test_user_A_ProfileModelSharingOfExperiencesUserHasAccess.sharing_of_experiences_user_has_access --> pas la nouvelle valeur du dico
        # pour avoir la bonne valeur il faut rechercher le dictionnaire à nouveau
        user_profile_model = ProfileModelSharingOfExperiencesUserHasAccess.objects.get(user__pk=test_user_A.id)
        user_profile_model_dictionnary = user_profile_model.sharing_of_experiences_user_has_access
        print("a", user_profile_model_dictionnary)
        #assert user_profile_model_dictionnary == {'credits': 5}

        #CODE TO TEST
        #if user_has_not_yet_access_to_sharings_of_experiences(request):  # -->'dictionary initialisation' in profile_model_dictionnary
        #    user_profile_model_dictionnary_reinitialisation(request)
        #    sharings_of_experience_age_plus_minus_one = queryset_sharing_of_experiences_from_others(request)
        #    allocation_of_new_sharings_of_experiences(request, ACCESS_TO_SHARINGS_MINIMUM_NUMBER, sharings_of_experience_age_plus_minus_one)
        #    # print(timeit.timeit(code_test, number=10000))
        #return render(request, 'sharingofexperience/home.html')




    def test_home_user_not_logged_in(self):
        pass

