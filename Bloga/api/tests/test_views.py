from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework import status
from api.authentication.serializers import UserSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from authentication.models import Profile
from blog.models import Posts, PostReactions, CommentReactions, Comments, SavedPost
from api.blog.serializers import PostReactionsSerializer, CommentReactionsSerializer


class RootViewTest(APITestCase):
    def test_root_endpoint(self):
        """
        Test the API V1 root endpoint returns the correct URLs.
        """
        url = reverse('root') 
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_keys = [
            "login", "logout", "logoutall", "user", "profile",
            "group", "post", "comment", "post-reaction",
            "comment-reaction", "saved-post"
        ]
        
        # Assert that all expected keys are present in the response data
        for key in expected_keys:
            self.assertIn(key, response.data)

        # Optional: Assert that the URLs are valid (not empty)
        for key in expected_keys:
            self.assertNotEqual(response.data[key], '')


class UserListViewTest(APITestCase):

    def setUp(self):
        # Create some test users
        self.user1 = User.objects.create_user(
            username="user1",
            first_name="User",
            last_name="One",
            email="user1@example.com",
            password="password123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            first_name="User",
            last_name="Two",
            email="user2@example.com",
            password="password123"
        )
        

    def test_get_user_list(self):
        url = reverse('user-list')  # Assuming the URL name is 'user-list'
        response = self.client.get(url)

        # Ensure status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Mock DRF request object to handle pagination
        factory = APIRequestFactory()
        request = factory.get(url)  # Create a DRF request object

        # Get the paginated response from the API and compare
        users = User.objects.all().order_by('id')  # Ensure queryset is ordered
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Or match the page size in your view
        paginated_users = paginator.paginate_queryset(users, request=Request(request))

        serializer = UserSerializer(paginated_users, many=True, context={'request': request})

        # Compare only the results part of the paginated response
        self.assertEqual(response.data['results'], serializer.data)


    def test_create_user(self):
        url = reverse('user-list')  # Assuming the URL name is 'user-list'
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }

        # Create a new user (requires authentication for this view)
        self.client.force_authenticate(user=self.user1)  # Authenticate as user1
        response = self.client.post(url, data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure the user was created
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.last().username, 'newuser')

    def test_create_user_unauthenticated(self):
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }

        # Attempt to create a new user without authentication
        response = self.client.post(url, data, format='json')

        # Should return a 403 Forbidden since the user is not authenticated
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailViewTest(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            first_name="User",
            last_name="One",
            email="user1@example.com",
            password="password123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            first_name="User",
            last_name="Two",
            email="user2@example.com",
            password="password123"
        )
        
    def test_get_user_detail(self):
        url = reverse('user-detail', kwargs={'username': self.user1.username})  # Assuming 'user-detail' as URL name
        response = self.client.get(url)

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the returned data
        serializer = UserSerializer(self.user1, context={'request': response.wsgi_request})  # Pass the request context
        self.assertEqual(response.data, serializer.data)

    def test_update_user(self):
        url = reverse('user-detail', kwargs={'username': self.user1.username})
        data = {
            'first_name': 'UpdatedName'
        }

        self.client.force_authenticate(user=self.user1)  # User1 updates their own data
        response = self.client.patch(url, data, format='json')

        # Check response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the data is updated
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'UpdatedName')

    def test_update_other_user_forbidden(self):
        url = reverse('user-detail', kwargs={'username': self.user1.username})
        data = {
            'first_name': 'UpdatedName'
        }

        self.client.force_authenticate(user=self.user2)  # User2 tries to update user1's data
        response = self.client.patch(url, data, format='json')

        # Should return 403 Forbidden due to permission issues
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_forbidden(self):
        url = reverse('user-detail', kwargs={'username': self.user1.username})

        self.client.force_authenticate(user=self.user2)  # User2 tries to delete user1
        response = self.client.delete(url)

        # Should return 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_account(self):
        url = reverse('user-detail', kwargs={'username': self.user1.username})

        self.client.force_authenticate(user=self.user1)  # User1 deletes their own account
        response = self.client.delete(url)

        # Should return 204 No Content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the user is deleted
        self.assertFalse(User.objects.filter(username='user1').exists())


class LoginAPITest(APITestCase):
    
    def setUp(self):
        # Create a user for testing
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.login_url = reverse('login')  # Ensure this is the correct URL name for your login endpoint

    def test_login_success(self):
        """
        Test successful login with valid credentials.
        """
        data = {
            'username': self.username,
            'password': self.password
        }

        # Send credentials directly to the login endpoint
        response = self.client.post(self.login_url, data, format='json')

        # Verify that the login was successful and that a Knox token is returned in the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


    def test_login_failure(self):
        """
        Test failed login with invalid credentials.
        """
        data = {
            'username': self.username,
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')

        # Check if the login failed due to invalid credentials
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)  # Knox token should not be present
        
              
class ProfileDetailViewTest(APITestCase):
    
    def setUp(self):
        # Create two users, one who owns the profile and one who doesn't
        self.user_owner = User.objects.create_user(username='owner', password='password123')
        self.user_other = User.objects.create_user(username='other', password='password123')

        # Create a profile for the owner
        self.profile_owner = Profile.objects.create(user=self.user_owner, bio="Owner's bio")
        
        # URL for profile detail view (assuming 'profile-detail' is the route name and it takes a 'pk' argument)
        self.url = reverse('profile-detail', kwargs={'pk': self.profile_owner.pk})

    def test_retrieve_profile(self):
        """
        Test retrieving a profile successfully by the owner.
        """
        # Authenticate as the owner
        self.client.login(username='owner', password='password123')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], self.profile_owner.bio)

    def test_update_profile_by_owner(self):
        """
        Test updating the profile by the owner successfully.
        """
        # Authenticate as the owner
        self.client.login(username='owner', password='password123')
        
        updated_data = {'bio': "Updated owner's bio"}
        
        response = self.client.put(self.url, updated_data, format='json')
        
        # Check if the update was successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile_owner.refresh_from_db()
        self.assertEqual(self.profile_owner.bio, updated_data['bio'])

    def test_update_profile_by_non_owner(self):
        """
        Test that a non-owner cannot update the profile.
        """
        # Authenticate as the non-owner
        self.client.login(username='other', password='password123')
        
        updated_data = {'bio': "Updated by non-owner"}
        
        response = self.client.put(self.url, updated_data, format='json')
        
        # Check if the update was forbidden due to permission
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.profile_owner.refresh_from_db()
        self.assertNotEqual(self.profile_owner.bio, updated_data['bio'])  # Ensure the bio wasn't updated

    def test_update_profile_unauthenticated(self):
        """
        Test that an unauthenticated user cannot update the profile.
        """
        updated_data = {'bio': "Unauthenticated update attempt"}
        
        response = self.client.put(self.url, updated_data, format='json')
        
        # Check if the request was denied for unauthenticated user
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
   
   
class PostsListViewTest(APITestCase):
    
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        # Create posts
        self.published_post = Posts.objects.create(author=self.user1, title="Published Post", status="PB", link='published-post')
        self.draft_post = Posts.objects.create(author=self.user1, title="Draft Post", status="DF", link='draft-post')
        self.other_published_post = Posts.objects.create(author=self.user2, title="Other Published Post", status="PB", link='other-published-post')

        self.list_url = reverse('posts-list')  # Assuming the URL is named 'posts-list'

    def test_list_posts_unauthenticated(self):
        """
        Test that unauthenticated users can only see published posts.
        """
        response = self.client.get(self.list_url)
        
        # Should only see published posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        for post in response.data['results']:
            self.assertEqual(post['status'], "PB")

    def test_list_posts_authenticated(self):
        """
        Test that authenticated users see their drafts and published posts.
        """
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.list_url)

        # Should see both published and draft posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        for post in response.data['results']:
            self.assertTrue((post['status'] == "PB") or (post['status'] == "DF" and post['author'].endswith(reverse('user-detail', kwargs={"username": "user1"}))))
        
    def test_create_post_authenticated(self):
        """
        Test that authenticated users can create new posts.
        """
        self.client.login(username='user1', password='password123')
        
        new_post_data = {
            'title': 'New Post',
            'content': 'Content of the new post',
            'status': 'PB',
            'link': 'new-post'
        }

        response = self.client.post(self.list_url, new_post_data, format='json')
        
        # Check if post creation was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Posts.objects.count(), 4)
        self.assertEqual(Posts.objects.filter(title=new_post_data['title']).first().title, 'New Post')

    def test_create_post_unauthenticated(self):
        """
        Test that unauthenticated users cannot create new posts.
        """
        new_post_data = {
            'title': 'New Post',
            'content': 'Content of the new post',
            'status': 'PB',
            'link': 'new-post'
        }

        response = self.client.post(self.list_url, new_post_data, format='json')
        
        # Check if post creation was forbidden
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)     


class PostReactionsListViewTest(APITestCase):

    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username='user1', password='password123')
        self.other_user = User.objects.create_user(username='user2', password='password123')
        
        # Create a post
        self.published_post = Posts.objects.create(title="Published Post", content="Some content", status="PB", author=self.user)
        self.unpublished_post = Posts.objects.create(title="Unpublished Post", content="Other content", status="DF", author=self.user)
        
        self.published_url = reverse('posts-detail', kwargs={"link": self.published_post.link})
        self.unpublished_url = reverse('posts-detail', kwargs={"link": self.unpublished_post.link})
        
        # Create some reactions
        self.reaction1 = PostReactions.objects.create(user=self.user, post=self.published_post, reaction='LK')
        self.reaction2 = PostReactions.objects.create(user=self.other_user, post=self.published_post, reaction='love')
        
        # URL for listing and creating reactions
        self.url = reverse('postreactions-list')  

    def test_list_post_reactions(self):
        """
        Test listing reactions for posts.
        """
        response = self.client.get(self.url)
        
        # Get reactions for published posts
        reactions = PostReactions.objects.all()
        serializer = PostReactionsSerializer(reactions, many=True, context={"request": response.wsgi_request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_reaction_authenticated(self):
        """
        Test creating a reaction when authenticated and the post is published.
        """
        self.client.login(username='user1', password='password123')

        data = {
            'post': self.published_url,
            'reaction': 'LK'
        }
        
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reaction'], 'LK')
        self.assertTrue(response.data['user'].endswith(reverse("user-detail", kwargs={"username": self.user.username})))

    def test_create_reaction_unauthenticated(self):
        """
        Test that unauthenticated users cannot create reactions.
        """
        data = {
            'post': self.published_url,
            'reaction': 'LK'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Check for unauthorized response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentReactionsListViewTest(APITestCase):

    def setUp(self):
        # Create users
        self.user = User.objects.create_user(username='user1', password='password123')
        self.other_user = User.objects.create_user(username='user2', password='password123')
        
        # Create a published post and an unpublished post
        self.published_post = Posts.objects.create(title="Published Post", content="Some content", status="PB", author=self.user)
        self.unpublished_post = Posts.objects.create(title="Unpublished Post", content="Other content", status="DF", author=self.user)
        
        # Create comments for the published post
        self.comment1 = Comments.objects.create(post=self.published_post, user=self.user, content="First comment")
        self.comment2 = Comments.objects.create(post=self.published_post, user=self.other_user, content="Second comment")

        # Create reactions for the comments
        self.reaction1 = CommentReactions.objects.create(user=self.user, comment=self.comment1, reaction='LK')
        self.reaction2 = CommentReactions.objects.create(user=self.other_user, comment=self.comment2, reaction='love')
        
        # URL for listing and creating comment reactions
        self.url = reverse('commentreactions-list')  
        
        # Hyperlink URLs for comments using reverse
        self.comment1_url = reverse('comments-detail', kwargs={'pk': self.comment1.pk})
        self.comment2_url = reverse('comments-detail', kwargs={'pk': self.comment2.pk})

    def test_list_comment_reactions(self):
        """
        Test listing comment reactions.
        """
        response = self.client.get(self.url)
        
        # Get reactions for comments
        reactions = CommentReactions.objects.all()
        serializer = CommentReactionsSerializer(reactions, many=True, context={'request': response.wsgi_request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_reaction_authenticated(self):
        """
        Test creating a reaction for a comment when authenticated and the post is published.
        """
        self.client.login(username='user1', password='password123')

        data = {
            'comment': self.comment1_url,  # Using URL instead of ID
            'reaction': 'LK'
        }
        
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reaction'], 'LK')
        self.assertEqual(response.data['user'], reverse('user-detail', kwargs={'username': self.user.username}, request=response.wsgi_request))  
        self.assertTrue(response.data['comment'].endswith(self.comment1_url))  

    def test_create_reaction_unauthenticated(self):
        """
        Test that unauthenticated users cannot create reactions.
        """
        data = {
            'comment': self.comment1_url,  # Using URL instead of ID
            'reaction': 'LK'
        }
        
        response = self.client.post(self.url, data, format='json')

        # Check for unauthorized response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)      
        

class CommentsListViewTest(APITestCase):
    
    def setUp(self):
        # Create a user and a post for testing
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.post_published = Posts.objects.create(author=self.user, title='Published Post', content='Content', status='PB')
        self.post_unpublished = Posts.objects.create(author=self.user, title='Unpublished Post', content='Content', status='DF')

        # Comments URL (assuming 'comments-list' is the route name)
        self.comments_url = reverse('comments-list')

    def test_list_comments(self):
        """
        Test that anyone can list all comments.
        """
        response = self.client.get(self.comments_url)
        
        # Check that the response status is 200 OK for unauthenticated users
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment_authenticated_on_published_post(self):
        """
        Test that an authenticated user can create a comment if the post is published.
        """
        # Authenticate the user
        self.client.login(username='testuser', password='testpass123')

        data = {
            'post': reverse("posts-detail", kwargs={"link": self.post_published.link}),
            'content': 'This is a test comment',
        }

        response = self.client.post(self.comments_url, data, format='json')

        # Check if the comment was successfully created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comments.objects.count(), 1)
        self.assertEqual(Comments.objects.first().content, 'This is a test comment')
        self.assertEqual(Comments.objects.first().user, self.user)

    def test_create_comment_unauthenticated(self):
        """
        Test that an unauthenticated user cannot create a comment.
        """
        data = {
            'post': reverse("posts-detail", kwargs={"link": self.post_published.link}),
            'content': 'Anonymous comment',
        }

        response = self.client.post(self.comments_url, data, format='json')

        # Check if the request was denied for unauthenticated users
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Comments.objects.count(), 0)  # No comment should be created


class SavedPostListViewTest(APITestCase):
    
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

        # Create posts for testing
        self.post1 = Posts.objects.create(author=self.user1, status="PB", title="Post 1", content="Content 1")
        self.post2 = Posts.objects.create(author=self.user2, status="PB", title="Post 2", content="Content 2")

        # Create saved posts for user1
        self.saved_post1 = SavedPost.objects.create(user=self.user1, post=self.post1)
        self.saved_post2 = SavedPost.objects.create(user=self.user1, post=self.post2)

        self.post1_url = reverse("posts-detail", kwargs={"link": self.post1.link})
        self.post2_url = reverse("posts-detail", kwargs={"link": self.post2.link})
        
        # URL for saved post list (assuming 'saved-post-list' is the route name)
        self.saved_posts_url = reverse('savedpost-list')

    def test_list_saved_posts_authenticated(self):
        """
        Test that an authenticated user can view only their own saved posts.
        """
        # Authenticate as user1
        self.client.login(username='user1', password='pass123')

        response = self.client.get(self.post1_url)
        self.post1_url = response.wsgi_request.build_absolute_uri()
        
        response = self.client.get(self.post2_url)
        self.post2_url = response.wsgi_request.build_absolute_uri()
        
        
        response = self.client.get(self.saved_posts_url)

        # Ensure user1 sees only their saved posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # User1 has 2 saved posts
        saved_post_ids = [saved_post['post'] for saved_post in response.data['results']]
        self.assertIn(self.post1_url, saved_post_ids)
        self.assertIn(self.post2_url, saved_post_ids)

    def test_list_saved_posts_other_user(self):
        """
        Test that a different authenticated user cannot see other users' saved posts.
        """
        # Authenticate as user2 (who has no saved posts)
        self.client.login(username='user2', password='pass123')

        response = self.client.get(self.saved_posts_url)

        # Ensure user2 does not see any saved posts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)  # User2 should not see any saved posts

    def test_create_saved_post_authenticated(self):
        """
        Test that an authenticated user can save a post.
        """
        # Authenticate as user2
        self.client.login(username='user2', password='pass123')

        data = {'post': reverse('posts-detail', kwargs={"link": self.post1.link})}

        response = self.client.post(self.saved_posts_url, data, format='json')

        # Check if the post was successfully saved
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SavedPost.objects.filter(user=self.user2).count(), 1)  # User2 should have 1 saved post
        saved_post = SavedPost.objects.get(user=self.user2, post=self.post1)
        self.assertEqual(saved_post.post, self.post1)
        self.assertEqual(saved_post.user, self.user2)

    def test_create_saved_post_unauthenticated(self):
        """
        Test that an unauthenticated user cannot save a post.
        """
        data = {'post': reverse('posts-detail', kwargs={"link": self.post1.link})}

        response = self.client.post(self.saved_posts_url, data, format='json')

        # Check if the request was denied for unauthenticated users
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(SavedPost.objects.count(), 2)  # No new saved post should be created

    def test_access_saved_posts_unauthenticated(self):
        """
        Test that an unauthenticated user cannot access the saved posts list.
        """
        response = self.client.get(self.saved_posts_url)

        # Check if the request was denied for unauthenticated users
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


        