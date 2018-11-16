from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, get_list_or_404
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import (
    User,
    Profile,
    Articles,
    Comments,
    Tags
)

class BaseTestClass(TestCase):

    # set up common variables that will be used throughout the lifetime of the tests
    def setUp(self):

        # default client
        self.client = APIClient()

        # default user
        self.testUser = User(username='testusername',email='test@email.co', password='123456')

        # save author user
        self.author = User.objects.create_user(username='author', email='author@haven.com', password='123456')

        # register a few articles for testing the GET end point
        Articles.objects.create(
            author = self.author,
            slug= 'post article 1', 
            title = 'This is a new post 1',
            description = 'This is a new post about django',
            body = 'Blah blah blah etc'
        )
        Articles.objects.create(
            author = self.author,
            slug= 'post article 2', 
            title = 'This is a new post 2',
            description = 'This is a new post about django',
            body = 'Blah blah blah etc'
        )
        Articles.objects.create(
            author = self.author,
            slug= 'post article 3', 
            title = 'This is a new post 3',
            description = 'This is a new post about django',
            body = 'Blah blah blah etc'
        )
        Articles.objects.create(
            author = self.author,
            slug= 'post article 4', 
            title = 'This is a new post 4',
            description = 'This is a new post about django',
            body = 'Blah blah blah etc'
        )
        
    
    def user_login(self, username, password):

        # login user
        response = self.client.post(reverse('auth-login'), data={'user':{'email':username, 'password':password}}, format="json")
        token = response.data.get('token')
        # create user authorisation header
        self.client.credentials(HTTP_AUTHORIZATION='Token '+ token)

    def get_article(self):
        return Articles.objects.get(title='This is a new post 1')

class ModelTest(BaseTestClass):

    def test_model_can_create_user(self):
        """This test checks if the model can create a user successfully"""
        oldCount = User.objects.count() #should be equal to 0
        self.testUser.save()

        newCount = User.objects.count()
        self.assertNotEqual(oldCount, newCount)

        # user profile
        user_profile = Profile(owner=self.testUser, first_name='John', last_name='Snow', bio='I know nothing')
        user_profile.save()
        profile = Profile.objects.get(owner=self.testUser)
        self.assertNotEqual(profile, None)

    def test_model_creates_unique_instances(self):
        """This tests if a unique user can be created"""
        self.testUser.save()
        newUser = User(username='testusername', email='another@test.user', password='123456')

        with self.assertRaises(IntegrityError):
            newUser.save()

    def test_model_creates_articles_and_comments(self):

        # save test user
        self.testUser.save()

        oldCount = Articles.objects.count()
        # create new article
        article = Articles(
            author=self.testUser,
            slug='test article',
            title='Test Article',
            description='describes article',
            body='article body goes here'
        )

        article.save()
        newCount = Articles.objects.count()

        # Test article creation
        self.assertNotEqual(oldCount, newCount)

        #test comments creation
        oldCommentCount = Comments.objects.count()

        # new comment
        comment = Comments(
            author=self.testUser,
            article=article,
            body='This is my comment'
        )
        comment.save()

        newCommentCount = Comments.objects.count()
        self.assertNotEqual(oldCommentCount, newCommentCount)

    def test_tags_creation(self):
        oldCount = Tags.objects.count()

        tag = Tags(tag='Horse Punching')
        tag.save()

        self.assertNotEqual(oldCount, Tags.objects.count())

class UserViewTests(BaseTestClass):

    """
    User Tests Go Here
    """
    # login user
    def test_user_registration(self):
        
        # create a new system user
        author = {
            'email':'test@email.com',
            'username':'myUsername',
            'password':'myPassword123@'
        }
        response = self.client.post(reverse('users-register'), data={'user':author}, format="json")

        # successful user registration
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # test for token returned
        self.assertIn('token', response.data)
    
    def test_user_login(self):
        # create user 
        User.objects.create_user(username='loginUser', email='login@user.com', password='123456')

        #login user
        user_credentials = {'email':'login@user.com' , 'password':'123456'}

        response = self.client.post(reverse('auth-login'), data={'user':user_credentials}, format="json")
        
        # login successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # token returned
        self.assertIn('token', response.data)

    def test_password_reset(self):

        # user requests password reset with valid email/username
        #response = self.client(reverse('user-reset-password'), data={'username':'william.muriuki@andela.com'}, format="json")

        # test for successful password reset request sent
        #self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # request failed due to wrong username 
        #response = self.client(reverse('user-reset-password'), data={'username':'wrong@username.email'}, format="json")
        #self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        pass

class ArticleViewTests(BaseTestClass):

    """
    Article Tests Go Here
    """
    def test_article_creation(self):

        # login author user
        self.user_login('author@haven.com', '123456')

        new_article = {
            'slug': 'post article',
            'title': 'This is a new post',
            'description': 'This is a new post about django',
            'body': 'Blah blah blah etc'
        }
        response = self.client.post(reverse('articles-register'), data={'article':new_article}, format="json")
        
        # test for successful article creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fetch_all_articles(self):
        all_articles = Articles.objects.count()
        response = self.client.get(reverse('articles-all'), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(all_articles, len(response.data['articles']))

    def test_fetch_one_article(self):
        article = Articles.objects.get(title='This is a new post 4')
        response = self.client.get(reverse('articles-single', kwargs={'pk':article.id}), format="json")

        #test successful get request
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test for single article returned
        self.assertContains(response, article)

    def test_update_article(self):
        # login author user
        self.user_login('author@haven.com', '123456')
        article = Articles.objects.get(title='This is a new post 4')

        update_article = {
            'slug': 'post 4 article edited',
            'title': 'This is a new post',
            'description': 'This is a new post about django',
            'body': 'Blah blah blah etc'
        }
        response = self.client.put(reverse('articles-single', kwargs={'pk':article.id}), data={'article':update_article}, format="json")

        # test successful edit
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_article(self):
        # login author user
        self.user_login('author@haven.com', '123456')

        article = Articles.objects.get(title='This is a new post 4')

        response  = self.client.delete(reverse('articles-single', kwargs={'pk':article.id}), format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CommentsViewTest(BaseTestClass):
    
    def test_create_comments_for_article(self):
        # login author user
        self.user_login('author@haven.com', '123456')
        
        # get article
        article = self.get_article()

        my_comment = {'article_id':article.id, 'body':'This is a comment'}
        response = self.client.post(reverse('article-comments-add', kwargs={'pk':article.id}), data= {'comment':my_comment}, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fetch_all_my_comments(self):
        # Fetch comments belonging to an article
        article = self.get_article()
        author = self.author

        for x in range(1,10):
            # registern 10 comments for this article
            Comments.objects.create(author=author, article=article, body='This is comment {}'.format(x))

        response = self.client.get(reverse('article-comments', kwargs={'pk':article.id}),format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(9, len(response.data['comments']))

