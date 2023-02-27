from django import forms
from sharingofexperience.models import SharingOfExperience


class SharingOfExperienceFormCreate(forms.ModelForm):
   class Meta:
     model = SharingOfExperience
     fields = '__all__'
