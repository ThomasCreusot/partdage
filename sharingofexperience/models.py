from django.db import models
from django.conf import settings

class SharingOfExperience(models.Model):
    """Represents a sharing of experience"""

    NOTPROCESSED = 'NOP'
    VALIDATED = 'VAL'
    REJECTED = 'REJ'

    MODERATION_CHOICES = (
        (NOTPROCESSED, 'Not processed yet'),
        (VALIDATED, 'Validated'),
        (REJECTED, 'Rejected'),
    )

    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='SharingOfExperience_author')
    experienced_age = models.fields.PositiveIntegerField()
    description = models.fields.TextField(max_length=2500, blank=False)
    moderator_validation = models.fields.CharField(max_length=20, choices=MODERATION_CHOICES, blank=False)
    likes = models.JSONField()

    def receive_like(self, id_user_who_send_liked):
        self.likes['likes'][str(id_user_who_send_liked)] = 1
        self.save()

    def total_likes_calculation(self):
        # self.total_likes = len(self.likes['likes'])
        self.total_likes = 0
        for like_key in self.likes['likes']:
            if self.likes['likes'][like_key] == 1:
                self.total_likes += self.likes['likes'][like_key]
