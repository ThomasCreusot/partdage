"""Partdage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import authentication.views
import sharingofexperience.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sharingofexperience.views.index, name='index'),
    path('why_partdage/', sharingofexperience.views.why_partdage, name='why_partdage'),
    path('how_partdage_was_made/', sharingofexperience.views.how_partdage_was_made, name='how_partdage_was_made'),

    path('login/', authentication.views.login_page, name='login'),
    path('logout/', authentication.views.logout_user, name='logout'),

    path('home/', sharingofexperience.views.home, name='home'),
    path('signup/', authentication.views.signup_page, name='signup'),

    path('sharing_experiences_menu/', sharingofexperience.views.sharing_experiences_menu, name='sharing_experiences_menu'),
    path('sharing_an_experience_create/<int:experienced_age>/', sharingofexperience.views.sharing_an_experience_create, name='sharing_an_experience_create'),
    path('sharing_an_experience_update/<int:sharing_of_experience_id>/', sharingofexperience.views.sharing_an_experience_update, name='sharing_an_experience_update'),

    path('learning_from_others/', sharingofexperience.views.learning_from_others, name='learning_from_others'),

    path('like_a_sharing_of_experience/<int:id_sharing_of_experience_to_be_liked>/', sharingofexperience.views.like_a_sharing_of_experience, name='like_a_sharing_of_experience'),

    # https://docs.djangoproject.com/en/4.1/topics/http/urls/#how-django-processes-a-request
    # slug: Matches any slug string consisting of ASCII letters or numbers, plus the hyphen and underscore characters. 
    path('spend_credits/<slug:past_or_future_sharings>/', sharingofexperience.views.spend_credits, name='spend_credits'),
]
