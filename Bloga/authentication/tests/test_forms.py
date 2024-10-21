from django.test import TestCase, SimpleTestCase
from django.contrib.auth.models import User
from authentication.forms import SignUpForm, ProfileForm
from authentication.models import Profile
from itertools import product

class SignUpFormTest(TestCase):
    def test_password_validation(self):
        data = {
          "username": "testuser",
          "first_name": "test",
          "last_name": "user",
          "email": "testuser@email.com",
          "password1": "iamgroot",
          "password2": "iamgood"
        }

        form = SignUpForm(data = data)
        self.assertFalse(form.is_valid())


    def test_user_registration(self):
        data = {
          "username": "testuser",
          "first_name": "test",
          "last_name": "user",
          "email": "testuser@email.com",
          "password1": "iamgroot",
          "password2": "iamgroot"
        }

        form = SignUpForm(data = data)
        self.assertTrue(form.is_valid(), False)
        if form.is_valid():
            user = form.save()
            self.assertTrue(isinstance(user,User), True)
            
            
class ProfileFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username="testuser", first_name="test", last_name="user",email="testuser@email.com", password="iamgroot")
    
    
    def test_profile_new_email_must_be_unique(self):
        user = User.objects.create_user(
            username="newuser", 
            first_name="new", 
            last_name="user", 
            email="newuser@email.com", 
            password="iamgroot"
        )
        profile = Profile.objects.create(user=user)

        data = {
            "first_name": "test",
            "last_name": "user",
            "email": "testuser@email.com",
        }

        form = ProfileForm(instance=profile, data=data)
        self.assertFalse(form.is_valid())
        
        
    def test_password_change_logic(self):
        user = User.objects.create_user(
            username="newuser", 
            first_name="new", 
            last_name="user", 
            email="newuser@email.com", 
            password="iamgroot"
        )
        profile = Profile.objects.create(user=user)

        data = {
            "first_name": "new",
            "last_name": "user",
            "email": "user@email.com",
        }
        
        passwords = ["iamgroot", "newpassword", None, ""]
        
        for password, password1, password2 in product(passwords, repeat=3):
            data['password'] = password
            data['password1'] = password1
            data['password2'] = password2
            
          
            form = ProfileForm(instance=profile, data=data)
            
            if (password1 or password2) and not password:
                self.assertFalse(form.is_valid(), f"Failed for password={password}, password1={password1}, password2={password2}")
            
            if password:
                if not user.check_password(password):
                    self.assertFalse(form.is_valid(), "Validated user with wrong password")

                if password1 and password1 != password2:
                    self.assertFalse(form.is_valid(), "Validated user with password missmatch")
                    
                if not password1:
                    self.assertFalse(form.is_valid(), "Validated a form without a new password")
                    
                    
    def test_account_update(self):
        user = User.objects.create_user(
            username="newuser", 
            first_name="new", 
            last_name="user", 
            email="newuser@email.com", 
            password="iamgroot"
        )
        profile = Profile.objects.create(user=user)

        data = {
            "first_name": "first",
            "last_name": "last",
            "email": "firstlast@email.com",
            "password": "iamgroot",
            "password1": "newpassword",
            "password2": "newpassword",
        }

        form = ProfileForm(instance=profile, data=data)
        self.assertTrue(form.is_valid())
        if form.is_valid():
            form.save()
        
        user = User.objects.get(username="newuser")
        self.assertEqual(user.first_name, "first")
        self.assertEqual(user.last_name, "last")
        self.assertEqual(user.email, "firstlast@email.com")
        self.assertTrue(user.check_password("newpassword"))
        
    def test_retain_old_email_if_unchanged(self):
        user = User.objects.create_user(
            username="newuser", 
            first_name="new", 
            last_name="user", 
            email="newuser@email.com", 
            password="iamgroot"
        )
        profile = Profile.objects.create(user=user)
        data = {
            "first_name": "first",
            "last_name": "last",
            "email": "newuser@email.com",
            "password": "iamgroot",
            "password1": "newpassword",
            "password2": "newpassword",
        }

        form = ProfileForm(instance=profile, data=data)
        self.assertTrue(form.is_valid())
        
        if form.is_valid():
            user = User.objects.get(username="newuser")
            self.assertEqual(user.email, "newuser@email.com")