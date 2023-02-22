from django.shortcuts import render
from .models import SharingOfExperience

# Create your views here.
def index(request):
    objects=SharingOfExperience.objects.all()
    context={
        "objects":objects,
    }
    return render(request, 'index.html', context)