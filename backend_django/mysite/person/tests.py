from django.contrib.auth.models import Permission, Group
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
        Group.objects.create(name='hr')
        self.hr_group = Group.objects.get(name='hr')
        self.hr_group.permissions.add(Permission.objects.get(codename='add_person'))
        self.hr_group.permissions.add(Permission.objects.get(codename='view_person'))
        self.hr_group.permissions.add(Permission.objects.get(codename='change_person'))
        self.user = Person.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.hr_user = Person.objects.create_user(
            username='hruser',
            first_name='HR',
            last_name='User',
            password='testpassword',
            manager=self.user,
            is_staff=True
        )
        self.hr_user.groups.add(self.hr_group)


    def test_login(self):
        url = reverse('login')
        data = {
            'username': self.user.username,
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


    def client_login(self, username='testuser', password='testpassword'):
        url = reverse('login')
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(url, data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')

    def test_logout(self):
        url = reverse('logout')
        self.client_login(self.user.username, 'testpassword')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_user(self):
        url = reverse('person-list')
        response = self.client.post(url, {'username': 'testuser1', 'first_name': 'Test', 'last_name': 'User', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_with_hr_user(self):
        url = reverse('person-list')
        self.client_login(self.hr_user.username, 'testpassword')
        data = {
            'username': 'testuser1',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_users(self):
        url = reverse('person-list')
        self.client_login(self.user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_users_with_hr(self):
        url = reverse('person-list')
        self.client_login(self.hr_user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_user(self):
        url = reverse('person-detail', args=[self.hr_user.pk])
        self.client_login(self.user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        url = reverse('person-detail', args=[self.user.pk])
        self.client_login(self.hr_user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_me(self):
        url = reverse('person-me')
        self.client_login(self.user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        url = reverse('person-detail', args=[self.user.pk])
        self.client_login(self.user.username, 'testpassword')
        data = {
            'phone_number': '+79001234567',
            'first_name': 'Test',
            'last_name': 'User',
            'surname': 'User',
            'birthday': '2000-01-01'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_login(self.hr_user.username, 'testpassword')
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete(self):
        url = reverse('person-detail', args=[self.user.pk])
        self.client_login(self.user.username, 'testpassword')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client_login(self.hr_user.username, 'testpassword')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_me(self):
        url = reverse('person-me')
        self.client_login(self.user.username, 'testpassword')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)



