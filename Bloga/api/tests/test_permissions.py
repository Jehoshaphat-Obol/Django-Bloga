from rest_framework.test import APIRequestFactory
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.authentication.permissions import IsAccountOwnerOrReadOnly
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import Profile
from rest_framework.reverse import reverse

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
        
        
        
        
        