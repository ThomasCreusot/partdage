from django import forms
from sharingofexperience.models import SharingOfExperience


class SharingOfExperienceFormCreate(forms.ModelForm):
   class Meta:
    model = SharingOfExperience
    # fields = '__all__'
    # fields = ['description',]
    exclude = ('user_id',)  