from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


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
        self.assertEqual(self.user.get_full_name(), 'User Test ')

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
        self.client.login(username='testuser', password='testpassword')  # Логинимся для тестов

    def test_create_user(self):
        url = reverse('user-create')  # Убедитесь, что это правильный URL для создания пользователя
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword'
        }

        response = self.client.post(url, data)

        # Проверка статус-кода ответа и наличия созданного объекта в базе данных
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Person.objects.filter(username='newuser').exists())

    def test_get_user_details(self):
        url = reverse('user-detail',
                      args=[self.user.id])  # Убедитесь, что это правильный URL для получения пользователя

        response = self.client.get(url)

        # Проверка статус-кода ответа и наличия объекта в ответе
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.user.username)

    def test_update_user(self):
        url = reverse('user-detail', args=[self.user.id])  # URL для обновления пользователя

        data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }

        response = self.client.patch(url, data)

        # Проверка статус-кода ответа и обновления объекта в базе данных
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка обновленных данных
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_delete_user(self):
        url = reverse('user-detail', args=[self.user.id])  # URL для удаления пользователя

        response = self.client.delete(url)

        # Проверка статус-кода ответа и отсутствия объекта в базе данных
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Person.objects.filter(id=self.user.id).exists())
# Create your tests here.
