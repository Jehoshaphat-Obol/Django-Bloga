from rest_framework.test import APIRequestFactory
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.authentication.permissions import IsAccountOwnerOrReadOnly
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import Profile
from rest_framework.reverse import reverse
from blog.models import *
from api.blog.permissions import *

class IsAccountOwnerOrReadOnlyPermissionTest(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.factory = APIRequestFactory()

    def test_permission_granted_for_get_request(self):
        request = self.factory.get('/fake-url/')
        permission = IsAccountOwnerOrReadOnly()

        # GET request should allow access regardless of ownership
        self.assertTrue(permission.has_object_permission(request, None, self.user1))

    def test_permission_granted_for_owner_put_request(self):
        request = self.factory.put('/fake-url/')
        request.user = self.user1
        permission = IsAccountOwnerOrReadOnly()

        # PUT request should be allowed if the request user is the object owner
        self.assertTrue(permission.has_object_permission(request, None, self.user1))

    def test_permission_denied_for_non_owner_put_request(self):
        request = self.factory.put('/fake-url/')
        request.user = self.user2
        permission = IsAccountOwnerOrReadOnly()

        # PUT request should be denied if the request user is not the object owner
        self.assertFalse(permission.has_object_permission(request, None, self.user1))


class HasProfileorCanCreatePermissionTest(APITestCase):
    def setUp(self):
        self.user_with_profile = User.objects.create_user(username='user_with_profile', password='password')
        profile = Profile.objects.create(user=self.user_with_profile)
        self.profile_detail_url = reverse('profile-detail', kwargs={'pk': profile.pk})
        self.profile_list_url = reverse('profile-list')
        self.user_without_profile = User.objects.create_user(username='user_without_profile', password='password')

    def test_post_request_with_existing_profile_denied(self):
        self.client.login(username='user_with_profile', password='password')
        response = self.client.post(self.profile_list_url, data={"bio": "Hello World"})  
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_request_without_profile_allowed(self):
        self.client.login(username='user_without_profile', password='password')
        response = self.client.post(self.profile_list_url, data={"bio": "Hello World"})  
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  

    def test_get_request_allowed(self):
        self.client.login(username='user_without_profile', password='password')
        response = self.client.get(self.profile_list_url)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(self.profile_detail_url)  
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class IsSuperUserPermissionTest(APITestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(username='superuser', password='password')
        self.regular_user = User.objects.create_user(username='regular_user', password='password')
        

    def test_super_user_permission(self):
        self.client.login(username='superuser', password='password')
        response = self.client.get(reverse('group-list'))  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_permission_denied(self):
        self.client.login(username='regular_user', password='password')
        response = self.client.get(reverse('group-list'))  
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_super_user_object_permission(self):
        obj = Group.objects.create(name="group1")  
        self.client.login(username='superuser', password='password')
        response = self.client.get(reverse('group-detail', kwargs={"name": obj.name}))  
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_object_permission_denied(self):
        obj = Group.objects.create(name="group1")  
        self.client.login(username='regular_user', password='password')
        response = self.client.get(reverse('group-detail', kwargs={"name": obj.name}))  
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        
class IsPostOwnerOrReadOnlyPermissionTest(APITestCase):
    
    def setUp(self):
        # Create users
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.user_non_owner = User.objects.create_user(username='non_owner', password='password123')

        # Create a post for the owner
        self.post = Posts.objects.create(author=self.user_owner, title="Owner's Post", status="PB", link='owners-post')

        # URL for detail view (assuming 'posts-detail' is the route name and uses 'link' as lookup field)
        self.detail_url = reverse('posts-detail', kwargs={'link': self.post.link})

    def test_post_update_by_owner(self):
        """
        Test that the owner can update their own post.
        """
        self.client.login(username='owner', password='password123')

        updated_data = {
            'title': "Updated Owner's Post",
            "content": "Some upto date content",
            "status": "PB",
            }
        response = self.client.put(self.detail_url, data=updated_data, format='json')

        # Check if the update was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Owner's Post")

    def test_post_update_by_non_owner(self):
        """
        Test that a non-owner cannot update the post.
        """
        self.client.login(username='non_owner', password='password123')

        updated_data = {
            'title': "Updated Owner's Post",
            "content": "Some upto date content",
            "status": "PB",
            }
        
        response = self.client.put(self.detail_url, updated_data, format='json')

        # Check if the update was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.title, "Non-Owner's Update")

    def test_post_delete_by_non_owner(self):
        """
        Test that a non-owner cannot delete the post.
        """
        self.client.login(username='non_owner', password='password123')

        response = self.client.delete(self.detail_url)

        # Check if the delete was forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Posts.objects.filter(pk=self.post.pk).exists())        
        
        
class IsCommentOwernerOrReadOnlyTest(APITestCase):
    
    def setUp(self):
        # Create users
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.user_non_owner = User.objects.create_user(username='non_owner', password='password123')

        self.post = Posts.objects.create(title="Title 1", status="PB", author=self.user_owner, content="Hello world")
        self.post_url = reverse("posts-detail", kwargs={"link": self.post.link})
        # Create a comment for the owner
        self.comment = Comments.objects.create(user=self.user_owner,post = self.post, content='Owner\'s Comment')

        # URL for the comment detail view (assuming 'comments-detail' is the route name)
        self.detail_url = reverse('comments-detail', kwargs={'pk': self.comment.pk})

    def test_get_comment(self):
        """Test that anyone can GET a comment."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_by_owner(self):
        """Test that the owner can update their own comment."""
        self.client.login(username='owner', password='password123')

        updated_data = {
            'content': 'Updated Owner\'s Comment',
            "post": self.post_url,
            }
        response = self.client.put(self.detail_url, data=updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated Owner\'s Comment')

    def test_update_comment_by_non_owner(self):
        """Test that a non-owner cannot update the comment."""
        self.client.login(username='non_owner', password='password123')

        updated_data = {'content': 'Non-Owner\'s Comment'}
        response = self.client.put(self.detail_url, data=updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.comment.refresh_from_db()
        self.assertNotEqual(self.comment.content, 'Non-Owner\'s Comment')        
        
        
class IsPostReactionOwernerOrReadOnlyTest(APITestCase):
    
    def setUp(self):
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.user_non_owner = User.objects.create_user(username='non_owner', password='password123')

        self.post = Posts.objects.create(title="Title 1", status="PB", author=self.user_owner, content="Hello world")
        self.post_url = reverse("posts-detail", kwargs={"link": self.post.link})
        
        
        self.post_reaction = PostReactions.objects.create(user=self.user_owner, post=self.post, reaction='LK') 
        self.detail_url = reverse('postreactions-detail', kwargs={'pk': self.post_reaction.pk})

    def test_get_post_reaction(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_post_reaction(self):
        self.client.login(username="owner", password="password123")
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
      
    def test_non_owner_delete_post_reaction(self):
        self.client.login(username="non_owner", password="password123")
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
      
        
class IsCommentReactionOwernerOrReadOnlyTest(APITestCase):
    
    def setUp(self):
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.user_non_owner = User.objects.create_user(username='non_owner', password='password123')
        

        self.post = Posts.objects.create(title="Title 1", status="PB", author=self.user_owner, content="Hello world")
        self.post_url = reverse("posts-detail", kwargs={"link": self.post.link})
        
        self.comment = Comments.objects.create(user=self.user_owner, content="Hellow world", post=self.post)
        
        self.comment_reaction = CommentReactions.objects.create(user=self.user_owner, comment=self.comment, reaction='LK')  # Assuming a reaction model
        self.detail_url = reverse('commentreactions-detail', kwargs={'pk': self.comment_reaction.pk})

    def test_get_comment_reaction(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.login(username='owner', password='password123')

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment_reaction.refresh_from_db()


    def test_delete_comment_reaction(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='owner', password='password123')

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_non_owner_delete_comment_reaction(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.login(username='non_owner', password='password123')

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class IsSavedPostOwernerTest(APITestCase):
    
    def setUp(self):
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.user_non_owner = User.objects.create_user(username='non_owner', password='password123')
                
        
        self.post = Posts.objects.create(title="Title 1", status="PB", author=self.user_owner, content="Hello world")
        self.post_url = reverse("posts-detail", kwargs={"link": self.post.link})
        
        self.saved_post = SavedPost.objects.create(user=self.user_owner, post = self.post)  # Assuming a saved post model

        self.detail_url = reverse('savedpost-detail', kwargs={'pk': self.saved_post.pk})

    def test_get_saved_post_by_owner(self):
        self.client.login(username='owner', password='password123')

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_saved_post_by_non_owner(self):
        self.client.login(username='non_owner', password='password123')        
        response = self.client.get(self.detail_url)        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

        