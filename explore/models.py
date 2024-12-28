from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='explore_follow_followers', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='explore_follow_following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
