from django.contrib import admin
from sharingofexperience.models import SharingOfExperience

class SharingOfExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'experienced_age', 'description', 'moderator_validation', 'likes')

admin.site.register(SharingOfExperience, SharingOfExperienceAdmin)
