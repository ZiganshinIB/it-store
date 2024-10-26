import json
from distutils.log import fatal

from django.contrib.auth.models import Group, Permission
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    ApprovalRoute,
    ApproveStep,
    TaskTemplate,
    Task
)

from .serializers import (
    ListApprovalRouteSerializer,
    DetailApprovalRouteSerializer,
    UpdateApprovalRouteSerializer, TaskTemplateSerializer
)


User = get_user_model()


class ApprovalRouteModelTest(APITestCase):

    def setUp(self):
        self.group_admin = Group.objects.create(name='Admin')
        self.group_admin.permissions.add(Permission.objects.get(codename='add_approvalroute'))
        self.group_admin.permissions.add(Permission.objects.get(codename='view_approvalroute'))
        self.group_admin.permissions.add(Permission.objects.get(codename='change_approvalroute'))
        self.group_admin.permissions.add(Permission.objects.get(codename='delete_approvalroute'))
        self.admin = User.objects.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        self.admin.groups.add(self.group_admin)
        self.user = User.objects.create_user(
            username='testuser2',
            first_name='Test',
            last_name='User',
            password='testpassword'
        )
        ApprovalRoute.objects.create(title='test', author=self.admin)

    def client_login(self, username='testuser', password='testpassword'):
        url = reverse('login')
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(url, data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')

    def test_create_approvalroute_without_steps(self):
        url_list = reverse('api_tasker:approvalroute-list')

        data = {
            'title': 'test',
        }
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'test')

        self.client_login(self.user.username, 'testpassword')
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_approvalroute_with_steps(self):
        url_list = reverse('api_tasker:approvalroute-list')
        data = {
            'title': 'test',
            'steps': [
                {
                    'title': 'step-test',
                    'approval_type': 'manager',
                },
                {
                    'title': 'step-test2',
                    'approval_type': 'manager',
                }
            ]
        }
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'test')
        self.assertEqual(response.data['steps'][0]['approval_type'], 'manager')


    def test_create_approvalroute_with_wrong_steps(self):
        url_list = reverse('api_tasker:approvalroute-list')
        data = {
            'title': 'test',
            'steps': [
                {
                    'title': 'step-test',
                    'approval_type': 'group',
                },
                {
                    'title': 'step-test2',
                    'approval_type': 'manager',
                }
            ]
        }
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {
            'title': 'test',
            'steps': [
                {
                    'title': 'step-test',
                    'approval_type': 'group',
                    'group_approver': self.group_admin.pk
                },
                {
                    'title': 'step-test2',
                    'approval_type': 'manager',
                }
            ]
        }
        response = self.client.post(url_list, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_approvalroute(self):
        url = reverse('api_tasker:approvalroute-detail', args=[1])
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_login(self.user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_list_approvalroute(self):
        url = reverse('api_tasker:approvalroute-list')
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_login(self.user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_approvalroute(self):
        url = reverse('api_tasker:approvalroute-detail', args=[1])
        self.client_login(self.admin.username, 'testpassword')
        data = {
            'title': 'test5',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'test5')

        self.client_login(self.user.username, 'testpassword')
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TaskTemplateAPITest(APITestCase):
    def setUp(self):
        self.group_admin = Group.objects.create(name='admin')
        self.group_admin.permissions.add(Permission.objects.get(codename='add_tasktemplate'))
        self.group_admin.permissions.add(Permission.objects.get(codename='view_tasktemplate'))
        self.group_admin.permissions.add(Permission.objects.get(codename='change_tasktemplate'))
        self.group_admin.permissions.add(Permission.objects.get(codename='delete_tasktemplate'))

        self.user = User.objects.create_user(
            username='testuser1',
            first_name='Test',
            last_name='User',
            password='testpassword')
        self.admin = User.objects.create_user(
            username='testuser3',
            first_name='Test',
            last_name='User',
            password='testpassword')
        self.admin.groups.add(self.group_admin)
        TaskTemplate.objects.create(
            title='test',
            description='test',
        )

    def client_login(self, username='testuser1', password='testpassword'):
        url = reverse('login')
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(url, data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')

    def test_get_list_tasktemplate(self):
        url = reverse('api_tasker:tasktemplate-list')
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_login(self.user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_tasktemplate(self):
        url = reverse('api_tasker:tasktemplate-detail', args=[1])
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_login(self.user.username, 'testpassword')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_tasktemplate(self):
        url = reverse('api_tasker:tasktemplate-list')
        self.client_login(self.admin.username, 'testpassword')
        data = {
            'title': 'test',
            'description': 'test',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client_login(self.user.username, 'testpassword')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_tasktemplate(self):
        url = reverse('api_tasker:tasktemplate-detail', args=[1])
        self.client_login(self.admin.username, 'testpassword')
        data = {
            'title': 'test5',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'test5')

        self.client_login(self.user.username, 'testpassword')
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_tasktemplate(self):
        url = reverse('api_tasker:tasktemplate-detail', args=[1])
        self.client_login(self.admin.username, 'testpassword')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client_login(self.user.username, 'testpassword')
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TaskAPITest(APITestCase):
    def setUp(self):
        self.group_admin = Group.objects.create(name='admin')
        self.group_admin.permissions.add(Permission.objects.get(codename='add_task'))
        self.group_admin.permissions.add(Permission.objects.get(codename='view_task'))
        self.group_admin.permissions.add(Permission.objects.get(codename='change_task'))
        self.group_admin.permissions.add(Permission.objects.get(codename='delete_task'))
        self.group_it = Group.objects.create(name='it')
        self.group_it.permissions.add(Permission.objects.get(codename='add_task'))
        self.group_programmer = Group.objects.create(name='programmer')
        self.user_author = User.objects.create_user(
            username='testuser1',
            first_name='Test1',
            last_name='User',
            password='testpassword'
        )
        self.user_executor = User.objects.create_user(
            username='testuser3',
            first_name='Test3',
            last_name='User',
            password='testpassword'
        )
        self.user_it = User.objects.create_user(
            username='testuser5',
            first_name='Test5',
            last_name='User',
            password='testpassword'
        )
        self.user_it.groups.add(self.group_it)
        self.user_programmer = User.objects.create_user(
            username='testuser7',
            first_name='Test7',
            last_name='User',
            password='testpassword'
        )
        self.user_programmer.groups.add(self.group_programmer)
        self.admin = User.objects.create_user(
            username='admin',
            first_name='admin',
            last_name='User',
            password='testpassword'
        )
        self.admin.groups.add(self.group_admin)

        # create tasks
        self.task_author_executor = Task.objects.create(
            title='task1',
            description='test',
            dedlin_date=timezone.now(),
            author=self.user_author,
            executor=self.user_executor,
            group=self.group_it
        )
        self.task_author_userit = Task.objects.create(
            title='task2',
            description='test',
            dedlin_date=timezone.now(),
            author=self.user_author,
            executor=self.user_it,
            group=self.group_it
        )
        self.task_userit_executor = Task.objects.create(
            title='task3',
            description='test',
            dedlin_date=timezone.now(),
            author=self.user_it,
            executor=self.user_executor,
            group=self.group_programmer
        )
        self.task_userit_userprogrammer = Task.objects.create(
            title='task4',
            description='test',
            dedlin_date=timezone.now(),
            author=self.user_it,
            executor=self.user_programmer,
            group=self.group_programmer
        )


    def client_login(self, username='testuser1', password='testpassword'):
        url = reverse('login')
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(url, data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')

    def test_get_tasks_author(self):
        # author
        self.client_login(self.user_author.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # userit
        self.client_login(self.user_it.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        # programmer
        self.client_login(self.user_programmer.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # admin
        self.client_login(self.admin.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        # executor
        self.client_login(self.user_executor.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_task_cansel(self):
        self.client_login(self.user_author.username, 'testpassword')
        url = reverse('api_tasker:task-cansel', args=[self.task_author_userit.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cans')

    def test_task_cansel_error(self):
        self.client_login(self.user_it.username, 'testpassword')
        url = reverse('api_tasker:task-cansel', args=[self.task_author_userit.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client_login(self.user_programmer.username, 'testpassword')
        url = reverse('api_tasker:task-cansel', args=[self.task_author_userit.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_task_create(self):
        self.client_login(self.user_it.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        data = {
            'title': 'test',
            'description': 'test',
            'dedlin_date': timezone.now(),
            'executor': self.user_executor.id,
            'group': self.group_it.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



