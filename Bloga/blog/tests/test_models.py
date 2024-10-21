from django.test import TestCase
from ..models import (
    Posts, random_string_generator,
    Comments, PostReactions, CommentReactions,
    SavedPost)
from django.utils import timezone
from taggit.models import Tag
from django.contrib.auth.models import User
from django.utils.text import slugify

class PostsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username="testuser", email="testuser@gmail.com", password="iamgroot")
        
        items = ['one', 'two','three']
        
        for item in items:
            post = Posts.objects.create(
                title = f"Post {item}",
                content = f'Content {item}',
                author = user,
                status = "DF" if items.index(item) % 2 == 0 else "PB",
            )
            
            
                    

    def test_published_manager_returns_published_posts_only(self):
        posts = Posts.published.all()
        
        for post in posts:
            self.assertEqual(post.status, 'PB')
    
    
    def test_random_string_generator(self):
        string1 = random_string_generator()
        string2 = random_string_generator()
        
        self.assertNotEqual(string1, string2)
        
        
    def test_post_str_method(self):
        posts = Posts.objects.all()
        
        for post in posts:
            self.assertEqual(str(post), post.title)
    
    
    def test_addition_of_tags(self):
        items = ['one', 'two','three']
        for item in items:
            tag = Tag.objects.create(name=item)
            posts = Posts.objects.all()
            for post in posts:
                post.tags.add(tag)

        for post in posts:
            self.assertEqual(post.tags.all().count(), 3)
            self.assertListEqual([tag.name for tag in post.tags.all()], items)
    
    
    def test_publish_date_update_with_status_field(self):
        posts = Posts.objects.all()
        
        for post in posts:
            if post.status == 'DF':
                self.assertEqual(post.publish, None)
                # update for the next round
                post.status ='PB'
            else:
                self.assertNotEqual(post.publish, None)
                post.status ='DF'

            post.save(update=True)
        
        
        for post in posts:
            if post.status == 'DF':
                self.assertEqual(post.publish, None)
            else:
                self.assertNotEqual(post.publish, None)

            post.save(update=True)
        
    
    def test_links_are_derived_from_title(self):
        posts = Posts.objects.all()
        for post in posts:
            self.assertIn(slugify(post.title), post.link)
    
    def test_links_are_always_unique(self):
        author = User.objects.get(username="testuser")
        post1 = Posts.objects.create(title="unique post", author=author)
        post2 = Posts.objects.create(title="unique post", author=author)
        
        self.assertNotEqual(post1.link, post2.link)
        
        
class CommentsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="testuser", email="testuser@email.com",password="iamgroot")
        
        Posts.objects.create(title="post1", content="hello world", author=user, status = "DF")
        Posts.objects.create(title="post1", content="hello world", author=user, status = "PB")
    
        posts = Posts.objects.all()        
        for post in posts:
            Comments.objects.create(user=user, post=post, content="I love this post")
        
    def test_users_can_comment_on_published_post_only(self):
        comments = Comments.objects.all()
        statuses = [comment.post.status for comment in comments]
        
        self.assertIn('PB', statuses)
        self.assertNotIn('DF', statuses)
        
    def test_comments_to_string_method(self):
        comments = Comments.objects.all()
        
        for comment in comments:
            self.assertEqual(str(comment), f"comment: {comment.content[:10]}... on {comment.post.title[:10]}..."
        )
            
            
class PostReactionsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="testuser", email="testuser@email.com", password="iamgroot")
        post1 = Posts.objects.create(title="draft post", content="This is a draft post", status="DF", author=user)
        post2 = Posts.objects.create(title="publised post", content="This is a published post", status="PB", author=user)
        
        
    def test_user_can_react_to_published_posts_only(self):
        posts = Posts.objects.all()
        user = User.objects.get(username="testuser")
        
        for post in posts:
            PostReactions.objects.create(user=user, post=post)
        
        reactions = PostReactions.objects.all()
        statuses = [reaction.post.status for reaction in reactions]
        
        self.assertIn("PB", statuses)
        self.assertNotIn("DF", statuses)
        
    def test_user_can_react_to_a_post_only_once(self):
        posts = Posts.objects.all()
        user = User.objects.get(username="testuser")
        
        for post in posts:
            PostReactions.objects.create(user=user, post=post)
            PostReactions.objects.create(user=user, post=post)
            
        posts = Posts.published.all()
        reactions = PostReactions.objects.all()
        
        self.assertEqual(posts.count(), reactions.count())


class CommentReactionsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="testuser", email="testuser@email.com",password="iamgroot")
        
        Posts.objects.create(title="post1", content="hello world", author=user, status = "DF")
        Posts.objects.create(title="post1", content="hello world", author=user, status = "PB")
    
        posts = Posts.objects.all()        
        for post in posts:
            Comments.objects.create(user=user, post=post, content="I love this post")
           
        
    def test_user_can_react_to_comments_in_published_posts_only(self):
        comments = Comments.objects.all()
        user = User.objects.get(username="testuser")
        
        for comment in comments:
            CommentReactions.objects.create(user=user, comment=comment)
        
        reactions = CommentReactions.objects.all()
        statuses = [reaction.comment.post.status for reaction in reactions]
        
        self.assertIn("PB", statuses)
        self.assertNotIn("DF", statuses)
        
    def test_user_can_react_to_a_comment_only_once(self):
        comments = Comments.objects.all()
        user = User.objects.get(username="testuser")
        
        for comment in comments:
            CommentReactions.objects.create(user=user, comment=comment)
            CommentReactions.objects.create(user=user, comment=comment)
            
        comments = Comments.objects.all()
        reactions = CommentReactions.objects.all()
        
        self.assertEqual(comments.count(), reactions.count())


class SavedPostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username="testuser", email="testuser@gmail.com", password="iamgroot")
        for i in range(5):
            Posts.objects.create(
                title= f"Title {i}",
                content= f"Content {i}",
                author=user,
                status = "DF" if i % 2 == 0 else "PB"
            )
            
    def test_only_published_post_can_be_saved(self):
        posts = Posts.objects.all()
        user = User.objects.get(username="testuser")
        
        for post in posts:
            SavedPost.objects.create(
                user=user,
                post=post,
            )
            
        saves = SavedPost.objects.all()
        published = Posts.published.all()
        
        self.assertEqual(saves.count(), published.count())
        
        
    def test_user_can_save_a_post_once(self):
        posts = Posts.objects.all()
        user = User.objects.get(username="testuser")
        
        for post in posts:
            SavedPost.objects.create(
                user=user,
                post=post,
            )
            SavedPost.objects.create(
                user=user,
                post=post,
            )
            
        saves = SavedPost.objects.all()
        published = Posts.published.all()
        
        self.assertEqual(saves.count(), published.count())