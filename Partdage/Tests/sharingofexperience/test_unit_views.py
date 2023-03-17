from django.urls import reverse
from django.test import Client
from pytest_django.asserts import assertTemplateUsed


"""
Utiliser Mocks pour de l'unitaire


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
voir cours


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


class TestIndexView:
    def setup_method(self, method):
        #fonction appelée lors du lancement d'un test unitaire faisant partie d'une classe

    def test_signup_view(self):
        assert 1 == 1


    def teardown_method(self, method):
        #fonction appelée à la fin d'un test unitaire faisant partie d'une classe
"""


class TestIndexView:

    def test_index(self):
        client = Client()
        path = reverse('index')
        response = client.get(path)
        content = response.content.decode()

        expected_content = "<h1>Welcome !</h1>"

        assert response.status_code == 200
        assertTemplateUsed(response, "sharingofexperience/index.html")
        assert content.find(expected_content) != -1
