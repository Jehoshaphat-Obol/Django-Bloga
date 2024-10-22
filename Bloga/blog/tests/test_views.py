from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class SignInViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="testuser", password="iamgroot")
        
    
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authentication:sign_in'))
        self.assertEqual(response.status_code, 200)
        
    
    def test_valid_login(self):
        response = self.client.post(reverse("authentication:sign_in"), data={"username": "testuser", "password": "iamgroot"})
        self.assertRedirects(response, reverse("blog:home"), 302, 200)
        
    def test_invalid_login(self):
        response = self.client.post(reverse("authentication:sign_in"), data={"username": "testuser", "password": "iamgrooty"})
        self.assertEqual(response.status_code, 200)
        
    def test_redirected_login(self):
        url = reverse('authentication:sign_in') + f"?next={reverse('blog:write')}"
        data = {
            "username": 'testuser',
            "password": "iamgroot",
        }
        
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("blog:write"), 302, 200)


class SignUpViewTest(TestCase):
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authentication:sign_up'))
        self.assertEqual(response.status_code, 200)
        
    def test_successful_sign_up(self):
        data = {
            "username": "testuser",
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@email.com",
            "password1": "iamgroot",
            "password2": "iamgroot", 
        }
        
        response = self.client.post(reverse("authentication:sign_up"), data)
        self.assertRedirects(response, reverse("blog:home"), 302, 200)
        
    def test_unsuccessful_sign_up(self):
        data = {
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@email.com",
            "password1": "iamgroot",
            "password2": "iamgrooty", 
        }
        
        response = self.client.post(reverse("authentication:sign_up"), data)
        self.assertEqual(response.status_code, 200)
        
        
class SignOutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password='iamgroot'
        )
        
    def test_sign_out_view_deauthenticates_and_redirects_to_sign_in(self):
        # login a user
        self.client.login(username=self.user.username, password='iamgroot')
        
        # check user authenticity before sign out
        self.assertTrue(authenticate(username=self.user.username, password='iamgroot'))
        
        # sign out the user
        response = self.client.get(reverse('authentication:sign_out'))
        
        # test redirect
        self.assertRedirects(response, reverse("authentication:sign_in"))
        
        # test deauthentication
        response = self.client.get(reverse('blog:user_edit', kwargs={"username": self.user.username}))
        self.assertRedirects(response, reverse('authentication:sign_in') + f"?next={reverse("blog:user_edit", kwargs={"username": "testuser"})}")
        
        