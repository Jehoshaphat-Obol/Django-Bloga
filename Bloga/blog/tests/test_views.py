from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from blog.models import *
from blog.forms import *
from authentication.models import *
from django.contrib.auth import authenticate
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image

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


class PostWriteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='iamgroot'
        )
        
    def setUp(self):
        self.client.login(username='testuser', password='iamgroot')

    def test_write_view_loads_for_authenticated_user(self):
        response = self.client.get(reverse('blog:write'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/write.html')

    def test_successful_post_creation_with_tags(self):
        data = {
            "title": "Test Post",
            "tags": "tag1, tag2, tag3",
            "status": "PB",
            "content": "This is a test post."
        }

        response = self.client.post(reverse('blog:write'), data=data)
        self.assertRedirects(response, reverse('blog:home'))

        post = Posts.objects.get(title="Test Post")
        self.assertEqual(post.content, data['content'])
        self.assertEqual(post.status, data['status'])

        tags = set([tag.strip() for tag in data['tags'].split(",")])
        post_tags = set([tag.name for tag in post.tags.all()])
        self.assertSetEqual(tags, post_tags)

    def test_successful_post_creation_without_tags(self):
        data = {
            "title": "Test Post without Tags",
            "tags": "",
            "status": "DF",
            "content": "This is a test post without tags."
        }

        response = self.client.post(reverse('blog:write'), data=data)
        self.assertRedirects(response, reverse('blog:home'))

        post = Posts.objects.get(title="Test Post without Tags")
        self.assertEqual(post.content, data['content'])
        self.assertEqual(post.status, data['status'])
        self.assertFalse(post.tags.exists())

    def test_post_creation_with_invalid_data(self):
        data = {
            "title": "",  # Invalid title
            "tags": "tag1, tag2",
            "status": "PB",
            "content": "This post has an invalid title."
        }

        response = self.client.post(reverse('blog:write'), data=data)
        self.assertEqual(response.status_code, 200)

    def test_post_creation_with_invalid_status(self):
        data = {
            "title": "Test Post with Invalid Status",
            "tags": "tag1",
            "status": "INVALID_STATUS",  # Invalid status
            "content": "This post has an invalid status."
        }

        response = self.client.post(reverse('blog:write'), data=data)
        self.assertEqual(response.status_code, 200)
        # Check if the post was not created
        self.assertFalse(Posts.objects.filter(title=data['title']).exists())
        
        
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
    
                 
    def test_post_not_found(self):
        post = Posts.objects.first()
        response = self.client.get(reverse("blog:post", kwargs={"link": "alksdlas"}))
        self.assertEqual(response.status_code, 404)
    
    
    
    def test_view_has_comment_form_loaded(self):
        post = Posts.objects.first()
        response = self.client.get(reverse('blog:post', kwargs={"link": post.link}))
        form = response.context.get('form')
        self.assertIsInstance(form, CommentsForm)
    
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
    
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        post = Posts.objects.first()
        
        response = self.client.get(reverse("blog:post", kwargs={"link": post.link}))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
    
    def test_view_loads_for_authenticated_user_only(self):
        post = Posts.objects.first()
        url = reverse("blog:post_edit", kwargs={"link": post.link})
        users = User.objects.all()
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        
        for user in users:
            login = self.client.login(username=user.username, password="iamgroot")
            self.assertTrue(login)
            if user == post.author:
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                response = self.client.post(url)
                self.assertEqual(response.status_code, 200)
            else:
                response = self.client.get(url)
                self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
                response = self.client.post(url)
                self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))           
            
            self.client.logout()
                
    def test_view_loads_any_post_for_post_owner_only(self):
        post = Posts.objects.first()
        users = User.objects.all()
        url = reverse("blog:post_edit", kwargs={"link": post.link})
        
        for user in users:
            login = self.client.login(username=user.username, password="iamgroot")
            self.assertTrue(login)
            
            response = self.client.get(url)
            if post.author != user:
                self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
            else:
                self.assertEqual(response.status_code, 200)
            
            self.client.logout()
                
    def test_view_url_accessible_by_name(self):
        post = Posts.objects.first()
        users = User.objects.all()
        url = reverse("blog:post_edit", kwargs={"link": post.link})
        
        for user in users:
            login = self.client.login(username=user.username, password='iamgroot')
            self.assertTrue(login)
            if user == post.author:
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                response = self.client.post(url)
                self.assertEqual(response.status_code, 200)
            else:
                response = self.client.get(url)
                self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
                response = self.client.post(url)
                self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))           
            
            self.client.logout()
            
    def test_post_not_found(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_edit", kwargs={"link": "askdaskdfasdf"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        
                        
    def test_post_editing(self):
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        
        user = User.objects.get(username="testuser")
        post = Posts.objects.filter(author=user).first()
        
        url = reverse("blog:post_edit", kwargs={"link": post.link})
        
        # update post and publish
        data = {
            "title": "edit",
            "tags": "tag1,tag2,tag3",
            "status": "PB",
            "content": "edit",            
        }
        
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
                
        post = Posts.objects.filter(id=post.id).first()
        tags = set(data['tags'].split(","))
        post_tags = set([tag.name for tag in post.tags.all()])
        
        self.assertEqual(post.title, data['title'])
        self.assertEqual(post.status, data['status'])
        self.assertEqual(post.content, data['content'])
        self.assertSetEqual(tags, post_tags)
        
        
        # update post and save as draft
        data = {
            "title": "edit",
            "tags": "tag1, tag2, tag3",
            "status": "DF",
            "content": "edit",            
        }
        
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
        
        post = Posts.objects.filter(id=post.id).first()
        
        self.assertEqual(post.title, data['title'])
        self.assertEqual(post.status, data['status'])
        self.assertEqual(post.content, data['content'])
        
        # update post with invalid status/data
        data = {
            "title": "edit",
            "tags": "tag1, tag2, tag3",
            "status": "FD",
            "content": "edit",            
        }
        
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        
        post = Posts.objects.filter(id=post.id).first()
        
        self.assertEqual(post.title, data['title'])
        self.assertEqual(post.status, "DF")
        self.assertEqual(post.content, data['content'])
                     
        
class PostDeleteViewTest(TestCase):
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
 
    def test_view_loads_for_authenticated_user_only(self):
        post = Posts.objects.first()
        url = reverse("blog:post_delete", kwargs={"link": post.link})
        users = User.objects.all()
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        for user in users:            
            login = self.client.login(username=user.username, password="iamgroot")
            self.assertTrue(login)
            if user == post.author:
                response = self.client.get(url)
                self.assertRedirects(response, reverse("blog:home"))
            else:
                response = self.client.get(url)
                if response.status_code != 404:
                    self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
                response = self.client.post(url)
                if response.status_code != 404:
                    self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))           
                        
            self.client.logout()
                
    def test_view_loads_any_post_for_post_owner_only(self):
        post = Posts.objects.first()
        users = User.objects.all()
        url = reverse("blog:post_delete", kwargs={"link": post.link})
        
        for user in users:
            login = self.client.login(username=user.username, password="iamgroot")
            self.assertTrue(login)
            
            response = self.client.get(url)
            if post.author != user:
                self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
            else:
                self.assertRedirects(response, reverse("blog:home"))
            
            self.client.logout()
                
    def test_view_url_accessible_by_name(self):
        post = Posts.objects.first()
        users = User.objects.all()
        url = reverse("blog:post_delete", kwargs={"link": post.link})
        
        
        for user in users:
            login = self.client.login(username=user.username, password='iamgroot')
            self.assertTrue(login)
            if user == post.author:
                response = self.client.get(url)
                self.assertRedirects(response, reverse("blog:home"))
            else:
                response = self.client.get(url)
                if response.status_code != 404:
                    self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
            
            self.client.logout()  
                 
    def test_post_not_found(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_delete", kwargs={"link": "askdaskdfasdf"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        
     
class PostCommentViewTest(TestCase):
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

 
    def test_view_loads_for_authenticated_user_only(self):
        post = Posts.objects.first()
        url = reverse("blog:post_comment", kwargs={"link": post.link})
        user = User.objects.first()
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        login = self.client.login(username=user.username, password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
            
    def test_view_url_accessible_by_name(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_comment", kwargs={"link": post.link})
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))            
        
            
    def test_view_post_a_comment(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_comment", kwargs={"link": post.link})
        
        response = self.client.post(url, data={"content": "test comment"})
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
        
        self.assertTrue(Comments.objects.filter(post=post, content="test comment", user=user).exists(), "Failed to post a comment")        
                                  
    def test_post_not_found(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_comment", kwargs={"link": "askdaskdfasdf"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        
          
class PostLikeViewTest(TestCase):
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
 
    def test_view_loads_for_authenticated_user_only(self):
        post = Posts.objects.first()
        url = reverse("blog:post_like", kwargs={"link": post.link})
        user = User.objects.first()
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        login = self.client.login(username=user.username, password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
            
    def test_view_url_accessible_by_name(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_like", kwargs={"link": post.link})
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))            
            
    def test_view_post_like_and_unlike(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_like", kwargs={"link": post.link})
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
        self.assertTrue(PostReactions.objects.filter(post=post, user=user, reaction="LK").exists(), "Failed to like a post")
        
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
        self.assertFalse(PostReactions.objects.filter(post=post, user=user, reaction="LK").exists(), "Failed to like a post")        
                                  
    def test_post_not_found(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_like", kwargs={"link": "askdaskdfasdf"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        

class PostSaveViewTest(TestCase):
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
 
    def test_view_loads_for_authenticated_user_only(self):
        post = Posts.objects.first()
        url = reverse("blog:post_save", kwargs={"link": post.link})
        user = User.objects.first()
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        login = self.client.login(username=user.username, password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
            
    def test_view_url_accessible_by_name(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_save", kwargs={"link": post.link})
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))            
            
    def test_view_post_save_and_unsave(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_save", kwargs={"link": post.link})
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
        self.assertTrue(SavedPost.objects.filter(post=post, user=user).exists(), "Failed to like a post")
        
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
        self.assertFalse(SavedPost.objects.filter(post=post, user=user).exists(), "Failed to like a post")        
        
                                  
    def test_post_not_found(self):
        post = Posts.objects.first()
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_save", kwargs={"link": "askdaskdfasdf"})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        

class CommentLikeViewTest(TestCase):
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
 
    def test_view_loads_for_authenticated_user_only(self):
        post = Posts.objects.first()
        user = User.objects.first()
        comment = Comments.objects.create(user=user, post=post, content="test comment")
        url = reverse("blog:comment_like", kwargs={"comment_id": comment.id})

        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        login = self.client.login(username=user.username, password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
            
    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        
        post = Posts.objects.first()
        user = User.objects.get(username="testuser")
        comment = Comments.objects.create(user=user, post=post, content="test comment")
        url = reverse("blog:comment_like", kwargs={"comment_id": comment.id})

        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))            
            
    def test_view_comment_like_and_unlike(self):
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        
        post = Posts.objects.first()
        user = User.objects.get(username="testuser")
        comment = Comments.objects.create(user=user, post=post, content="test comment")
        url = reverse("blog:comment_like", kwargs={"comment_id": comment.id})

        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
        self.assertTrue(CommentReactions.objects.filter(comment=comment, user=user).exists(), "Failed to like a post")
        
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))        
        self.assertFalse(CommentReactions.objects.filter(comment=comment, user=user).exists(), "Failed to like a post")        
        
                                  
    def test_comment_not_found(self):
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        
        post = Posts.objects.first()
        user = User.objects.get(username="testuser")
        comment = Comments.objects.create(user=user, post=post, content="test comment")
        url = reverse("blog:comment_like", kwargs={"comment_id": 99999999})

        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        

class TagListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        tags = ['tag1', 'tag2', 'tag3']
        
        for item in range(6):
            post = Posts.objects.create(
                author=user,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
            
            post.tags.set(tags)
            post.save()
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:tags_list"))
        self.assertEqual(response.status_code, 200)
    
    def test_view_list_tags(self):
        response = self.client.get(reverse("blog:tags_list"))
        tags = response.context.get('tags')
        
        self.assertEqual(tags.count(), 3)

    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:tags_list"))
        user = response.context.get('user')
        self.assertIsNone(user)
        
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:tags_list"))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        

class TagViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        tags = ['tag1', 'tag2', 'tag3']
        
        for item in range(6):
            post = Posts.objects.create(
                author=user,
                title=f"Title {item}",
                content=f"Content {item}",
                status="DF" if item % 2 == 0  else "PB"
            )
            
            post.tags.set(tags)
            post.save()
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:tag", kwargs={"name": "tag1"}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_show_post_with_tag(self):
        response = self.client.get(reverse("blog:tag", kwargs={"name": "tag1"}))
        tag = response.context.get('tag')
        posts = response.context.get('posts')
        
        # tag name
        self.assertEqual(tag, "tag1")
        
        for post in posts:
            # post is published
            self.assertEqual(post.status, "PB")
            
            tags = [tag.name for tag in post.tags.all()]
            
            # post has tag
            self.assertIn("tag1", tags)

    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:tag", kwargs={"name": "tag1"}))
        user = response.context.get('user')
        self.assertIsNone(user)
        
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:tag", kwargs={"name": "tag1"}))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        

class UserListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls): 
        for i in range(5):
            User.objects.create_user(
                username=f"testuser{i}",
                password="iamgroot"
            )
        
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:user_list"))
        self.assertEqual(response.status_code, 200)
    
    def test_view_list_users(self):
        response = self.client.get(reverse("blog:user_list"))
        users = response.context.get('users')
        users_list = User.objects.all()
        
        self.assertEqual(users.count(), users_list.count())

    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:user_list"))
        user = response.context.get('user')
        self.assertIsNone(user)
        
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser0", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:user_list"))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser0")
        

class UserFollowingViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        for item in range(6):
            User.objects.create_user(
                username=f"testuser{item}",
                password=f"iamgroot"
            )
        
        users = User.objects.all()
        profile, create = Profile.objects.get_or_create(user=user)
        
        # follow all users
        for user in users:
            profile2, create = Profile.objects.get_or_create(user=user)
            profile.follow(profile2)
            
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:user_following", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 200)
    

    def test_view_list_users_following_list(self):
        response = self.client.get(reverse("blog:user_following", kwargs={"username": "testuser"}))
        users = response.context.get('users')
        user = User.objects.get(username="testuser")
        profile, created = Profile.objects.get_or_create(user=user)
        
        for user in users:
            self.assertIn(user, profile.follows.all())
                    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:user_following", kwargs={"username": "testuser"}))
        user = response.context.get('user')
        self.assertIsNone(user)
        
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:user_following", kwargs={"username": "testuser"}))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        

class UserFollowersViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        for item in range(6):
            User.objects.create_user(
                username=f"testuser{item}",
                password=f"iamgroot"
            )
        
        users = User.objects.all()
        profile, create = Profile.objects.get_or_create(user=user)
        
        # follow all users
        for user in users:
            profile2, create = Profile.objects.get_or_create(user=user)
            profile2.follow(profile)
            
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:user_followers", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 200)
    

    def test_view_list_users_followers_list(self):
        response = self.client.get(reverse("blog:user_followers", kwargs={"username": "testuser"}))
        users = response.context.get('users')
        user = User.objects.get(username="testuser")
        profile, created = Profile.objects.get_or_create(user=user)
        
        for user in users:
            self.assertIn(user, profile.followers.all())
                    
    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:user_followers", kwargs={"username": "testuser"}))
        user = response.context.get('user')
        self.assertIsNone(user)
        
    def test_user_is_loaded_in_context_after_authentication(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:user_followers", kwargs={"username": "testuser"}))
        
        user = response.context.get('user')
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "testuser")
        

class UserEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.user = User.objects.create_user(
            username="testuser",
            password="iamgroot",
            first_name="Test",
            last_name="User",
            email="testuser@example.com"
        )
        
        # Create a second user
        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="iamgroot"
        )
        
        # Create profiles for both users
        cls.profile = Profile.objects.create(user=cls.user, bio="I am Groot", dp="avatar.jpg")
        cls.other_profile = Profile.objects.create(user=cls.other_user)

    def test_view_url_accessible_by_name(self):
        self.client.login(username="testuser", password="iamgroot")
        response = self.client.get(reverse("blog:user_edit", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username="testuser", password="iamgroot")
        response = self.client.get(reverse("blog:user_edit", kwargs={"username": "testuser"}))
        self.assertTemplateUsed(response, "blog/user_edit.html")

    def test_only_profile_owner_can_access_edit_view(self):
        # Test with a different user
        self.client.login(username="otheruser", password="iamgroot")
        response = self.client.get(reverse("blog:user_edit", kwargs={"username": "testuser"}))
        self.assertRedirects(response, reverse("blog:profile", kwargs={"username": "testuser"}))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Forbidden Action")

    def test_form_initial_data_is_correct(self):
        self.client.login(username="testuser", password="iamgroot")
        response = self.client.get(reverse("blog:user_edit", kwargs={"username": "testuser"}))
        form = response.context.get("form")
        self.assertEqual(form.initial['first_name'], "Test")
        self.assertEqual(form.initial['last_name'], "User")
        self.assertEqual(form.initial['bio'], "I am Groot")
        self.assertEqual(form.initial['dp'], "avatar.jpg")
        self.assertEqual(form.initial['email'], "testuser@example.com")

    def test_form_submission_valid_data(self):
        self.client.login(username="testuser", password="iamgroot")
        
        # Create an in-memory image to simulate a valid image file
        image = io.BytesIO()
        Image.new('RGB', (100, 100)).save(image, format='JPEG')
        image.seek(0)

        uploaded_image = SimpleUploadedFile("avatar.jpg", image.read(), content_type="image/jpeg")
    
        # Simulate form submission
        data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'bio': 'New bio information',
            'dp': uploaded_image,
            'email': 'updateduser@example.com',
            'password': 'iamgroot',
            'password1': 'iamgrooty',
            'password2': 'iamgrooty',
        }
        response = self.client.post(reverse("blog:user_edit", kwargs={"username": "testuser"}), data=data, format="multipart")
            
        # Check that the form was submitted successfully with a 302 redirect
        self.assertEqual(response.status_code, 302)

        # Follow the redirect
        self.client.login(username="testuser", password="iamgrooty")
        final_response = self.client.get(response.url)

        # Now check that the final response after the redirect is 200
        self.assertEqual(final_response.status_code, 200)
        
        # Check that data was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updateduser@example.com')
        self.assertEqual(self.user.profile.bio, 'New bio information')
        self.assertTrue(self.user.profile.dp.name.endswith('.jpg'))
        self.assertTrue(self.user.check_password('iamgrooty'))

    def test_form_submission_invalid_data(self):
        self.client.login(username="testuser", password="iamgroot")
        
        # Simulate invalid form submission (e.g., empty email)
        response = self.client.post(reverse("blog:user_edit", kwargs={"username": "testuser"}), {
            'first_name': 'Updated',
            'last_name': 'User',
            'bio': 'New bio information',
            'dp': '',
            'email': ''  # Invalid email
        })
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("email", messages[0].message)

    def test_user_redirect_after_save(self):
        self.client.login(username="testuser", password="iamgroot")
        
        # Submit the form with valid data
        response = self.client.post(reverse("blog:user_edit", kwargs={"username": "testuser"}), {
            'first_name': 'Updated',
            'last_name': 'User',
            'bio': 'New bio information',
            'dp': '',
            'email': 'updateduser@example.com'
        })
        
        # Assert redirect to edit view after form save
        self.assertRedirects(response, reverse("blog:user_edit", kwargs={"username": "testuser"}))



class UserSavedViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user and a second user
        cls.user = User.objects.create_user(
            username="testuser",
            password="iamgroot",
            email="testuser@example.com"
        )
        
        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="iamgroot"
        )
        
        # Create some posts for test purposes
        cls.post1 = Posts.objects.create(
            author=cls.user, status="PB", title="First Post", content="This is the first post."
        )
        
        cls.post2 = Posts.objects.create(
            author = cls.other_user, status="PB", title="Second Post", content="This is the second post."
        )
        
        # Save posts for the user
        SavedPost.objects.create(user=cls.user, post=cls.post1)
        SavedPost.objects.create(user=cls.user, post=cls.post2)
    
    def test_view_url_accessible_by_name(self):
        self.client.login(username="testuser", password="iamgroot")
        response = self.client.get(reverse("blog:user_saved", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        self.client.login(username="testuser", password="iamgroot")
        response = self.client.get(reverse("blog:user_saved", kwargs={"username": "testuser"}))
        self.assertTemplateUsed(response, "blog/home.html")
    
    def test_view_redirects_if_user_is_not_owner(self):
        self.client.login(username="otheruser", password="iamgroot")
        response = self.client.get(reverse("blog:user_saved", kwargs={"username": "testuser"}))
        self.assertRedirects(response, reverse("blog:profile", kwargs={"username": "testuser"}))
    
    def test_view_correctly_loads_saved_posts_for_owner(self):
        self.client.login(username="testuser", password="iamgroot")
        response = self.client.get(reverse("blog:user_saved", kwargs={"username": "testuser"}))
        
        # Verify that the posts context contains the correct saved posts
        posts = response.context.get("posts")
        self.assertEqual(len(posts), 2)
        self.assertIn(self.post1, posts)
        self.assertIn(self.post2, posts)
    
    def test_view_page_title(self):
        self.client.login(username="testuser", password="iamgroot")
        response = self.client.get(reverse("blog:user_saved", kwargs={"username": "testuser"}))
        page_title = response.context.get("page_title")
        self.assertEqual(page_title, "My Saved Posts 🔖")
        
        
class UserFavoritesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        cls.another_user = User.objects.create_user(
            username="otheruser",
            password="iamgroot"
        )
        
        cls.published_post = Posts.objects.create(
            title="Published Post",
            author=cls.user,
            status="PB",
            content="Dummy content for the post",
        )
        
        cls.draft_post = Posts.objects.create(
            title="Draft Post",
            author=cls.user,
            status="DF",
            content="Dummy content for the post",
        )

        # Create PostReactions for the user
        PostReactions.objects.create(user=cls.user, post=cls.published_post)
        PostReactions.objects.create(user=cls.user, post=cls.draft_post)
        
    def test_view_url_accessible_by_name(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_favorites", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 200)

    def test_view_redirects_if_user_is_not_owner(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_favorites", kwargs={"username": "otheruser"}))
        self.assertEqual(response.status_code, 302)

    def test_view_displays_only_published_posts(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_favorites", kwargs={"username": "testuser"}))
        posts = response.context.get('posts')
        
        # Verify that only the published post is returned
        self.assertIn(self.published_post, posts)
        self.assertNotIn(self.draft_post, posts)

    def test_view_contains_correct_context_data(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_favorites", kwargs={"username": "testuser"}))
        
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['profile'], self.user)
        self.assertEqual(response.context['page_title'], "My Favorites ❤")
        
    def test_user_is_not_loaded_in_context_without_authentication(self):
        url = reverse("blog:user_favorites", kwargs={"username": "testuser"})
        response = self.client.get(url)
        
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        

class ProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create two users
        cls.user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="iamgroot"
        )
        
        # Create some posts for both users
        cls.user_post = Posts.objects.create(
            title="User's Published Post",
            author=cls.user,
            status="PB",
            content="Dummy content"
        )
        cls.user_draft_post = Posts.objects.create(
            title="User's Draft Post",
            author=cls.user,
            status="DF",
            content="Dummy content"
        )
        cls.other_user_post = Posts.objects.create(
            title="Other User's Published Post",
            author=cls.other_user,
            status="PB",
            content="Dummy content"
        )
        cls.other_user_draft_post = Posts.objects.create(
            title="Other User's Draft Post",
            author=cls.other_user,
            status="DF",
            content="Dummy content"
        )
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:profile", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 200)
    
    def test_view_own_profile_displays_all_posts(self):
        # Log in as the user
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:profile", kwargs={"username": "testuser"}))
        posts = response.context.get('posts')
        
        # Verify both published and draft posts are displayed
        self.assertIn(self.user_post, posts)
        self.assertIn(self.user_draft_post, posts)
    
    def test_view_another_profile_displays_only_published_posts(self):
        # Log in as the user
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:profile", kwargs={"username": "otheruser"}))
        posts = response.context.get('posts')
        
        # Verify only the published post of the other user is displayed
        self.assertIn(self.other_user_post, posts)
        self.assertNotIn(self.other_user_draft_post, posts)
    
    def test_view_displays_correct_page_title_for_own_profile(self):
        # Log in as the user
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:profile", kwargs={"username": "testuser"}))
        page_title = response.context.get('page_title')
        
        self.assertEqual(page_title, "My Posts")
    
    def test_view_displays_correct_page_title_for_other_user_profile(self):
        # Log in as the user
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        response = self.client.get(reverse("blog:profile", kwargs={"username": "otheruser"}))
        page_title = response.context.get('page_title')
        
        self.assertEqual(page_title, "Explore otheruser's Posts")
        
    def test_user_is_not_loaded_in_context_without_authentication(self):
        response = self.client.get(reverse("blog:profile", kwargs={"username": "testuser"}))
        user = response.context.get('user')
        self.assertIsNone(user)


class UserFollowViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="iamgroot"
        )
        
    def test_view_url_accessible_by_name(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_follow", kwargs={"username": "otheruser"}))
        self.assertEqual(response.status_code, 302)  # Should redirect to profile

    def test_user_can_follow_another_user(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        
        # Before following
        follower_profile, created = Profile.objects.get_or_create(user=self.user)
        followed_profile, created = Profile.objects.get_or_create(user=self.other_user)
        self.assertNotIn(followed_profile.user, follower_profile.follows.all())
        
        response = self.client.get(reverse("blog:user_follow", kwargs={"username": "otheruser"}))
        
        # After following
        follower_profile.refresh_from_db()
        self.assertIn(followed_profile.user, follower_profile.follows.all())

    def test_user_redirects_to_profile_if_following_self(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_follow", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 302)  # Should redirect to their own profile

    def test_view_redirects_to_profile_after_following(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_follow", kwargs={"username": "otheruser"}))
        self.assertRedirects(response, reverse("blog:profile", kwargs={"username": "otheruser"}))


class UserUnfollowViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="iamgroot"
        )
        
        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="iamgroot"
        )

        # Create profiles and follow the other user
        cls.follower_profile, _ = Profile.objects.get_or_create(user=cls.user)
        cls.followed_profile, _ = Profile.objects.get_or_create(user=cls.other_user)
        cls.follower_profile.follow(cls.followed_profile)

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_unfollow", kwargs={"username": "otheruser"}))
        self.assertEqual(response.status_code, 302)  # Should redirect to profile

    def test_user_can_unfollow_another_user(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)

        # Before unfollowing
        self.assertIn(self.followed_profile.user, self.follower_profile.follows.all())
        
        response = self.client.get(reverse("blog:user_unfollow", kwargs={"username": "otheruser"}))
        
        # After unfollowing
        self.follower_profile.refresh_from_db()
        self.assertNotIn(self.followed_profile.user, self.follower_profile.follows.all())

    def test_user_redirects_to_profile_if_unfollowing_self(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_unfollow", kwargs={"username": "testuser"}))
        self.assertEqual(response.status_code, 302)  # Should redirect to their own profile

    def test_view_redirects_to_profile_after_unfollowing(self):
        login = self.client.login(username="testuser", password="iamgroot")
        self.assertTrue(login)
        response = self.client.get(reverse("blog:user_unfollow", kwargs={"username": "otheruser"}))
        self.assertRedirects(response, reverse("blog:profile", kwargs={"username": "otheruser"}))


