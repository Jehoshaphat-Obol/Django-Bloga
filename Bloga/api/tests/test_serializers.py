from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from api.authentication.serializers import UserSerializer, ProfileSerializer
from rest_framework import serializers
from rest_framework import status
from authentication.models import Profile
from blog.models import Posts
from api.blog.serializers import PostsSerializer
from rest_framework.reverse import reverse

class UserSerializerTest(APITestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username="testuser",
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            password="old_password"
        )

    def test_user_creation(self):
        data = {
            "username": "newuser",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "janesmith@example.com",
            "password": "newpassword123"
        }
        
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Check if user is created
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.email, data['email'])
        # Ensure the password is hashed
        self.assertTrue(user.check_password(data['password']))

    def test_user_update(self):
        # Simulate the user updating their information
        data = {
            "username": "updateduser",
            "first_name": "Johnny",
            "last_name": "Doe",
            "email": "newemail@example.com"
        }
        
        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        # Ensure fields are updated correctly
        self.assertEqual(updated_user.username, data['username'])
        self.assertEqual(updated_user.first_name, data['first_name'])
        self.assertEqual(updated_user.last_name, data['last_name'])
        self.assertEqual(updated_user.email, data['email'])

    def test_password_update(self):
        # User provides correct old password and new password for updating
        data = {
            "old_password": "old_password",
            "password": "new_password123"
        }

        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        # Check if password is updated
        self.assertTrue(updated_user.check_password(data['password']))

    def test_incorrect_old_password(self):
        # User provides incorrect old password
        data = {
            "old_password": "wrong_old_password",
            "password": "new_password123"
        }

        serializer = UserSerializer(self.user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        # Assert that the correct validation error is raised
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.save()
            

        # Check if the error is raised as expected
        self.assertIn("old_password", context.exception.detail)
        self.assertEqual(context.exception.detail['old_password'], "Old password is incorrect.")
        

    def test_password_not_updated_without_old_password(self):
        # Attempt to update password without providing old password
        data = {
            "password": "new_password123"
        }

        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        # Password should not be updated because the old password wasn't provided
        self.assertTrue(updated_user.check_password("old_password"))
        self.assertFalse(updated_user.check_password(data['password']))


class ProfileSerializerTestCase(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')

        # Create profiles
        self.profile1 = Profile.objects.create(user=self.user1, bio='User 1 bio')
        self.profile2 = Profile.objects.create(user=self.user2, bio='User 2 bio')
        self.profile3 = Profile.objects.create(user=self.user3, bio='User 3 bio')

        # URLs for profiles
        self.url = self.profile_url = reverse('profile-detail', kwargs={'pk': self.profile1.pk})
        
        # Create user serializer instances
        self.user2_url = reverse('user-detail', kwargs={'username': self.user2.username})
        self.user3_url = reverse('user-detail', kwargs={'username': self.user3.username})
        
        
    def test_get_profile(self):
        # Test the retrieval of a profile
        self.client.login(username='user1', password='password1')
        response = self.client.get(self.profile_url)
        
        user = UserSerializer(self.user1, context={'request' : response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], user.data.get('url'))
    
    def test_update_profile_follows_success(self):
        # Test that the owner of the profile can update the 'follows' field
        self.client.login(username='user1', password='password1')
        response = self.client.get(self.profile_url)
        
        user2 = UserSerializer(self.user2, context={'request': response.wsgi_request})
        data = {
            'bio': 'Updated bio',
            'follows': [user2.data.get('url')]  # user1 wants to follow user2
        }
        response = self.client.patch(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.bio, 'Updated bio')
        self.assertIn(self.user2, self.profile1.follows.all())
        self.assertIn(self.user1, self.user2.profile.followers.all())

    def test_update_profile_follows_fail(self):
        # Test that a non-owner cannot modify the 'follows' field
        self.client.login(username='user2', password='password2')
        
        response = self.client.get(self.profile_url)
        user3 = UserSerializer(self.user3, context={'request': response.wsgi_request})
        
        data = {
            'bio': 'Another update',
            'follows': [user3.data.get('url')]
        }
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.profile1.refresh_from_db()
        self.assertNotEqual(self.profile1.bio, 'Another update')
    
    def test_followers_field_read_only(self):
        # Ensure that the 'followers' field is read-only
        self.client.login(username='user1', password='password1')
        
        data = {
            'followers': [self.user2_url]  
        }
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # Should ignore this field, not throw an error
        self.profile1.refresh_from_db()
        self.assertNotIn(self.user2, self.profile1.followers.all())  # Followers field shouldn't change


    def test_update_profile_permission_denied(self):
        """Test that an unauthorized user cannot modify the profile."""
        self.client.login(username='user2', password='password2')
        response = self.client.get(self.profile_url)

        # Setup the serializer with user2's context trying to update user1's profile
        serializer = ProfileSerializer(instance=self.profile1, data={'follows': []}, context={'request': response.wsgi_request})

        # Validate and attempt to update
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
            serializer.update(self.profile1, serializer.validated_data)

        self.assertEqual(str(context.exception.detail[0]), "You do not have permission to modify this profile.")
        
        
    def test_update_profile_remove_follower_on_unfollow(self):
        """Test that followers are removed when unfollowing."""
        self.client.login(username='user1', password='password1')
        
        # Initially user1 follows user2
        self.profile1.follows.add(self.user2)
        self.profile2.followers.add(self.user1)

        # Now user1 will unfollow user2
        data = {
            'follows': [],  # Clear the follows to unfollow user2
        }

        response = self.client.patch(self.url, data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that user1 no longer follows user2
        self.profile1.refresh_from_db()
        self.profile2.refresh_from_db()
        self.assertNotIn(self.user2, self.profile1.follows.all())
        
        # Check that user1 is also removed from user2's followers
        self.assertNotIn(self.user1, self.profile2.followers.all())

    def test_update_profile_follows_and_sync_followers(self):
        """Test that the followers are synced correctly when follows are updated."""
        self.client.login(username='user1', password='password1')

        # Initially user1 follows user2
        self.profile1.follow(self.profile2)
        self.profile1.refresh_from_db()

        # Now user1 will follow user3
        data = {
            'follows': [self.user3_url],  # Follow user3 using the URL
        }

        response = self.client.patch(self.url, data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that user1 follows user3
        self.profile1.refresh_from_db()
        self.profile3.refresh_from_db()
        self.assertIn(self.user3, self.profile1.follows.all())

        # Check that user1 is now a follower of user3
        self.assertIn(self.user1, self.profile3.followers.all())

        # Check that user2 is no longer a follower of user1
        self.assertNotIn(self.user1, self.profile2.followers.all())
        
        
class PostSerializerTest(APITestCase):
    def setUp(self):
        # Set up the API client and create test user and post
        self.user = self.create_user(username='testuser', password='testpassword')  # Create a user
        self.client.force_authenticate(user=self.user)  # Authenticate the user

    def create_user(self, username, password):
        # Helper method to create a user for testing
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username=username, password=password)
        return user

    def test_create_post_with_valid_data(self):
        # Test creating a post with valid data
        data = {
            'title': 'Test Post',
            'content': 'This is a test post content.',
            'status': 'DF',  
            'tags': ['tag1', 'tag2'],
        }
        response = self.client.post(reverse('posts-list'), data, format='json') 
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Posts.objects.filter(title='Test Post').exists())

    def test_create_post_with_invalid_data(self):
        # Test creating a post with missing required fields
        data = {
            'title': '',  
            'content': 'This post has no title.',
            'status': 'DF',
        }
        response = self.client.post(reverse('posts-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_update_post(self):
        # Test updating an existing post
        post = Posts.objects.create(
            title='Original Title',
            content='Original content.',
            status='DF',
            author=self.user
        )
        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content.',
            'status': 'PB',
            'tags': ['tag3'],
        }
        response = self.client.patch(reverse('posts-detail', kwargs={'link': post.link}), update_data, format='json')  # Adjust the URL
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, 'Updated Title')
        self.assertEqual(post.status, 'PB')

    def test_update_post_with_invalid_data(self):
        # Test updating a post with invalid data
        post = Posts.objects.create(
            title='Title',
            content='Content.',
            status='DF',
            author=self.user
        )
        update_data = {
            'title': '',  # Invalid title
        }
        response = self.client.patch(reverse('posts-detail', kwargs={'link': post.link}), update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_serialization_of_post(self):
        # Test if the serializer outputs the expected data
        post = Posts.objects.create(
            title='Test Post',
            content='This is a test post content.',
            status='DF',
            author=self.user
        )
        response = self.client.get(reverse('posts-list'))
        serializer = PostsSerializer(post, context = {'request': response.wsgi_request})
        self.assertEqual(serializer.data['title'], post.title)
        self.assertEqual(serializer.data['content'], post.content)
        self.assertEqual(serializer.data['status'], post.status)
        