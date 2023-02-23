from django.shortcuts import render
from .models import SharingOfExperience

def index(request):
    objects=SharingOfExperience.objects.all()
    context={
        "objects":objects,
    }
    return render(request, 'index.html', context)

def home(request):
    return render(request, 'sharingofexperience/home.html')
