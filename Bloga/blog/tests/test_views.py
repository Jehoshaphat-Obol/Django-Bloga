from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from blog.models import *
from django.contrib.auth import authenticate

class HomeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        for item in range(6):
            Posts.objects.create(
                author=user,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:home"))
        self.assertEqual(response.status_code, 200)
    
    def test_view_list_only_published_posts(self):
        response = self.client.get(reverse("blog:home"))
        posts = response.context.get('posts')
        
        self.assertNotEqual(posts.count(), 0, "posts are not being loaded")
        for post in posts:
            self.assertEqual(post.status, "PB")
    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:home"))
        user = response.context.get('user')
        self.assertIsNone(user)
        
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:home"))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        
        
class PostListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        for item in range(6):
            Posts.objects.create(
                author=user,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
    
    def test_view_list_only_published_posts(self):
        response = self.client.get(reverse("blog:post_list"))
        posts = response.context.get('posts')
        
        self.assertNotEqual(posts.count(), 0, "posts are not being loaded")
        for post in posts:
            self.assertEqual(post.status, "PB")
    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:post_list"))
        user = response.context.get('user')
        self.assertIsNone(user)
        
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:post_list"))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        
        
class PostDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        user2 = User.objects.create_user(
            username="testuser2",
            password="iamgroot"
        )
        
        
        for item in range(6):
            Posts.objects.create(
                author=user,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
        
        for item in range(6):
            Posts.objects.create(
                author=user2,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
             
    def test_view_url_accessible_by_name(self):
        post = Posts.objects.first()
        response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_loads_any_published_post_for_any_user(self):
        posts = Posts.objects.all()
        
        for post in posts:
            response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
            
            if post.status == "PB":
                self.assertEqual(response.status_code, 200)
                loaded = response.context.get('post')
                self.assertEqual(post, loaded)
            else:
                self.assertEqual(response.status_code, 404)
                        
    def test_view_loads_draft_post_only_to_authenticated_owner(self):
        user = User.objects.get(username='testuser')
        
        # authenticate a user
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        posts = Posts.objects.filter(status="DF").all()
        self.assertNotEqual(posts.count(), 0,msg="No posts to test")
        
        for post in posts:
            response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
            
            if post.author == user:
                self.assertEqual(response.status_code, 200)
                loaded = response.context.get('post')
                self.assertEqual(post, loaded)
            else:
                self.assertEqual(response.status_code, 404)         
                    
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        post = Posts.objects.first()
        
        response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        
    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        post = Posts.objects.first()
        response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
        user = response.context.get('user')
        self.assertIsNone(user)
             
        
class PostEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        user2 = User.objects.create_user(
            username="testuser2",
            password="iamgroot"
        )
        
        
        for item in range(6):
            Posts.objects.create(
                author=user,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
        
        for item in range(6):
            Posts.objects.create(
                author=user2,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
             
    def test_view_url_accessible_by_name(self):
        post = Posts.objects.first()
        response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_loads_any_published_post_for_any_user(self):
        posts = Posts.objects.all()
        
        for post in posts:
            response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
            
            if post.status == "PB":
                self.assertEqual(response.status_code, 200)
                loaded = response.context.get('post')
                self.assertEqual(post, loaded)
            else:
                self.assertEqual(response.status_code, 404)
                        
    def test_view_loads_draft_post_only_to_authenticated_owner(self):
        user = User.objects.get(username='testuser')
        
        # authenticate a user
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        posts = Posts.objects.filter(status="DF").all()
        self.assertNotEqual(posts.count(), 0,msg="No posts to test")
        
        for post in posts:
            response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
            
            if post.author == user:
                self.assertEqual(response.status_code, 200)
                loaded = response.context.get('post')
                self.assertEqual(post, loaded)
            else:
                self.assertEqual(response.status_code, 404)         
                    
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        post = Posts.objects.first()
        
        response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        
    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        post = Posts.objects.first()
        response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
        user = response.context.get('user')
        self.assertIsNone(user)
             
 