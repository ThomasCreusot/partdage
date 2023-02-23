from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SharingOfExperience

def index(request):
    objects=SharingOfExperience.objects.all()
    context={
        "objects":objects,
    }
    return render(request, 'index.html', context)

@login_required
def home(request):
    return render(request, 'sharingofexperience/home.html')
