from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from post.models import Post
from .models import Follow
from authy.models import Profile

@login_required
def explore(request):
    user = request.user

    # Get users the logged-in user is following
    following_profiles = Follow.objects.filter(follower=user)
    followed_users = [friend.following for friend in following_profiles]  # Followed users are in `friend.following`

    # Profile suggestions: excluding users the current user is following
    followed_user_ids = [user.id for user in followed_users]  # Extract the IDs of followed users
    profile_suggestions = Profile.objects.exclude(user__in=followed_user_ids).exclude(user=user)

    context = {
        'following_profiles': followed_users,
        'profile_suggestions': profile_suggestions,
    }
    
    return render(request, 'explore/explore.html', context)
