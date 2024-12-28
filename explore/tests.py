from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from post.models import Follow  # Assuming Follow model is in the post app
from authy.models import Profile  # Assuming Profile model is in the authy app

class ExplorePageTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Create test data
        self.suggested_user = User.objects.create_user(username='suggested_user', password='password')
        self.friend_user = User.objects.create_user(username='friend_user', password='password')

        Profile.objects.create(user=self.suggested_user, bio="Suggested user profile")
        Follow.objects.create(follower=self.user, following=self.friend_user)

    def test_explore_page_status_code(self):
        response = self.client.get(reverse('explore'))
        self.assertEqual(response.status_code, 200)

    def test_explore_page_template(self):
        response = self.client.get(reverse('explore'))
        self.assertTemplateUsed(response, 'explore/explore.html')

    def test_explore_page_context(self):
        response = self.client.get(reverse('explore'))
        self.assertIn('profile_suggestions', response.context)
        self.assertIn('following_profiles', response.context)

    def test_profile_suggestions_content(self):
        response = self.client.get(reverse('explore'))
        profile_suggestions = response.context['profile_suggestions']
        self.assertEqual(profile_suggestions.count(), 1)
        self.assertEqual(profile_suggestions.first().user.username, 'suggested_user')

    def test_following_profiles_content(self):
        response = self.client.get(reverse('explore'))
        following_profiles = response.context['following_profiles']
        self.assertEqual(following_profiles.count(), 1)
        self.assertEqual(following_profiles.first().user.username, 'friend_user')
