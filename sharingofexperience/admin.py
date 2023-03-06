from django.contrib import admin
from sharingofexperience.models import SharingOfExperience, ProfileModelSharingOfExperiencesUserHasAccess


class SharingOfExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'experienced_age', 'description', 'moderator_validation', 'likes')


class ProfileModelSharingOfExperiencesUserHasAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'sharing_of_experiences_user_has_access',)


admin.site.register(SharingOfExperience, SharingOfExperienceAdmin)
admin.site.register(ProfileModelSharingOfExperiencesUserHasAccess, ProfileModelSharingOfExperiencesUserHasAccessAdmin)
