from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile

class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username="testuser1", email="testuser1@gmail.com", password='iamgroot')
        user2 = User.objects.create_user(username="testuser2", email="testuser2@gmail.com", password='iamgroot')
        dp1 = SimpleUploadedFile(
            "user1.jpeg",
            b"user1 dp",
            "image/jpeg"
        )
        dp2 = SimpleUploadedFile(
            "user1.jpeg",
            b"user1 dp",
            "image/jpeg"
        )
        
        Profile.objects.create(user=user1, dp=dp1)
        Profile.objects.create(user=user2, dp=dp2)
        
    def test_profile_dp_are_stored_with_a_secure_filename(self):
        profiles = Profile.objects.all()
        initial_filenames = ['user1.jpeg', 'user2.jpeg']
        for profile in profiles:
            self.assertNotIn(profile.dp.url, [f"media/uploads/dp/{filename}" for filename in initial_filenames])
            
    def test_profile_dp_url_are_always_unique(self):
        urls = [profile.dp.url for profile in Profile.objects.all()]
        for url in urls:
            self.assertEqual(urls.count(url), 1)
    
    def test_user_passwords_are_hashed_and_salted(self):
        passwords = [user.password for user in User.objects.all()]
        
        # test hashing
        self.assertNotIn("iamgroot", passwords)
        
        # test salting
        for password in passwords:
            self.assertEqual(passwords.count(password), 1)

    def test_user_follows_no_one_initially(self):
        profiles = Profile.objects.all()
        for profile in profiles:
            self.assertEqual(profile.follows.count(), 0)
    
    def test_user_has_no_followers_initially(self):
        profiles = Profile.objects.all()
        for profile in profiles:
            self.assertEqual(profile.followers.count(), 0)
    
    def test_user_can_not_follow_himself(self):
        profiles = Profile.objects.all()
        
        # follow self
        for profile in profiles:
            profile.follow(profile)
        
        # check if added to follow list
        for profile in profiles:
            self.assertNotIn(profile.user, profile.follows.all())
            self.assertNotIn(profile.user, profile.followers.all())

    
    def test_user_can_follow_other_users(self):
        user1 = Profile.objects.all()[0]
        user2 = Profile.objects.all()[1]
        
        # user1 follows user2
        user1.follow(user2)
        
        self.assertIn(user2.user, user1.follows.all())
        self.assertIn(user1.user, user2.followers.all())
        
    
    def test_user_can_unfollow_other_users(self):
        user1 = Profile.objects.all()[0]
        user2 = Profile.objects.all()[1]
        
        # user1 follows and unfollow user2
        user1.follow(user2)
        user1.unfollow(user2)
        
        self.assertNotIn(user2.user, user1.follows.all())
        self.assertNotIn(user1.user, user2.followers.all())
        