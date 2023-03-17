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
        """Testing if the 'spend_credits' (name) route is mapping to spend_credits (view)"""

        url = reverse('spend_credits', args=['past_sharings'])
        assert url == "/spend_credits/past_sharings/"
        assert resolve(url).view_name == 'spend_credits'
        assert resolve(url).func == spend_credits
        print(url)
