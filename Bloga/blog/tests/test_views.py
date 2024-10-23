from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from blog.models import *
from blog.forms import *
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
        user = User.objects.first()
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
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
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_edit", kwargs={"link": post.link})
        
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
        user = User.objects.first()
        
        response = self.client.get(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        response = self.client.post(url)
        self.assertRedirects(response, reverse("authentication:sign_in") + f"?next={url}")
        
        login = self.client.login(username=user.username, password="iamgroot")
        self.assertTrue(login)
        
        if user == post.author:
            response = self.client.get(url)
            self.assertRedirects(response, reverse("blog:home"))
            response = self.client.post(url)
            self.assertRedirects(response, reverse("blog:home"))
        else:
            response = self.client.get(url)
            self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
            response = self.client.post(url)
            self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))           
                
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
        login = self.client.login(username='testuser', password='iamgroot')
        self.assertTrue(login)
        user = User.objects.get(username="testuser")
        url = reverse("blog:post_delete", kwargs={"link": post.link})
        
        
        if user == post.author:
            response = self.client.get(url)
            self.assertRedirects(response, reverse("blog:home"))
            response = self.client.post(url)
            self.assertRedirects(response, reverse("blog:home"))
        else:
            response = self.client.get(url)
            self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))
            response = self.client.post(url)
            self.assertRedirects(response, reverse("blog:post", kwargs={"link": post.link}))           
                                   
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
        
         