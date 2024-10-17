from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


from .models import Person


User = get_user_model()


class PersonModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )

    def test_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'User Test')

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), 'User T.')


class UserAPITest(APITestCase):
    def setUp(self):
        self.user = Person.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )


    def test_login(self):
        url = reverse('login')
        data = {
            'username': self.user,
            'password': 'testpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['auth_token'])
        data = {
            'username': 'testuser1',
            'password': 'testpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'], ["Невозможно войти с предоставленными учетными данными."])


    def client_login(self):
        url = reverse('login')
        data = {
            'username': self.user.username,
            'password': 'testpassword',
        }
        response = self.client.post(url, data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')

    def test_logout(self):
        url = reverse('logout')
        self.client_login()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)