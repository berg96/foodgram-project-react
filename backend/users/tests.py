from django.test import TestCase

from users.models import User, Subscribe


class UserModelTestCase(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='User', email='user@user.com', password='password',
            first_name='Test', last_name='User'
        )
        self.assertEquals(user.username, 'User')
        self.assertEquals(user.email, 'user@user.com')
        self.assertEquals(user.first_name, 'Test')
        self.assertEquals(user.last_name, 'User')


class SubscribeModelTestCase(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='Author', email='author@author.com'
        )
        self.user = User.objects.create_user(
            username='User', email='user@user.com'
        )

    def test_subscribe_creation(self):
        subscribe = Subscribe.objects.create(
            author=self.author, subscriber=self.user
        )
        self.assertEquals(subscribe.author, self.author)
        self.assertEquals(subscribe.subscriber, self.user)
