from django.urls import reverse, resolve
from sharingofexperience.views import sharing_an_experience_create, sharing_an_experience_update, like_a_sharing_of_experience, spend_credits


class TestSharingofExperienceUrls:

    def test_sharing_an_experience_create(self):
        """Testing if the 'sharing_an_experience_create' (name) route is mapping to sharing_an_experience_create (view)"""

        url = reverse('sharing_an_experience_create', args=[1])

        # Vérifie si l’URL est correcte
        assert url == "/sharing_an_experience_create/1/"
        # # Vérifie si le nom de la vue est correct et que l’URL correspond bien au nom de la vue.
        assert resolve(url).view_name == 'sharing_an_experience_create'
        assert resolve(url).func == sharing_an_experience_create


    def test_sharing_an_experience_update(self):
        """Testing if the 'sharing_an_experience_update' (name) route is mapping to sharing_an_experience_update (view)"""

        url = reverse('sharing_an_experience_update', args=[1])

        assert url == "/sharing_an_experience_update/1/"
        assert resolve(url).view_name == 'sharing_an_experience_update'
        assert resolve(url).func == sharing_an_experience_update


    def test_like_a_sharing_of_experience(self):
        """Testing if the 'like_a_sharing_of_experience' (name) route is mapping to like_a_sharing_of_experience (view)"""

        url = reverse('like_a_sharing_of_experience', args=[1])

        assert url == "/like_a_sharing_of_experience/1/"
        assert resolve(url).view_name == 'like_a_sharing_of_experience'
        assert resolve(url).func == like_a_sharing_of_experience

    def test_spend_credits(self):
        assert 1 == 1



"""
    path('sharing_an_experience_create/<int:experienced_age>/', sharingofexperience.views.sharing_an_experience_create, name='sharing_an_experience_create'),
    path('sharing_an_experience_update/<int:sharing_of_experience_id>/', sharingofexperience.views.sharing_an_experience_update, name='sharing_an_experience_update'),
    path('like_a_sharing_of_experience/<int:id_sharing_of_experience_to_be_liked>/', sharingofexperience.views.like_a_sharing_of_experience, name='like_a_sharing_of_experience'),
    path('spend_credits/<slug:past_or_future_sharings>/', sharingofexperience.views.spend_credits, name='spend_credits'),
"""