from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

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
        