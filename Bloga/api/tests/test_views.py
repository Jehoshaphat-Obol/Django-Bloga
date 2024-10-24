from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework import status
from api.authentication.serializers import UserSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from authentication.models import Profile


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
        self.login_url = reverse('login')  # Assuming 'login' is the name of the login URL

    def test_login_success(self):
        """
        Test successful login with valid credentials.
        """
        data = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(self.login_url, data, format='json')

        # Check if the login was successful and Knox token is returned
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)  # Knox token should be in the response

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
        



        