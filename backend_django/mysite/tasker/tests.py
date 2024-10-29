import json
from distutils.log import fatal
from tokenize import group

from django.contrib.auth.models import Group, Permission
from django.template.defaultfilters import title
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
    Task, Request, RequestTemplate
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

        self.tasktemplate = TaskTemplate.objects.create(
            title='test',
            description='test',
            dedlin=timezone.timedelta(days=1),
            group=self.group_programmer
        )
        self.requst = Request.objects.create(
            title='test',
            dedlin_date=timezone.now(),
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
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('api_tasker:task-list')
        data = {
            'title': 'test',
            'description': 'test',
            'task_template': self.tasktemplate.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        self.client_login(self.user_programmer.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        data = {
            'title': 'test',
            'description': 'test',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client_login(self.user_it.username, 'testpassword')
        url = reverse('api_tasker:task-list')
        data = {
            'title': 'test',
            'description': 'test',
            'on_request': self.requst.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_comment(self):
        self.client_login(self.user_it.username, 'testpassword')
        url = reverse('api_tasker:task-comment', args=[self.task_author_userit.id])
        data = {
            'title': 'test',
            'content': 'test',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.client_login(self.user_author.username, 'testpassword')
        url = reverse('api_tasker:task-comment', args=[self.task_author_userit.id])
        data = {
            'title': 'test3',
            'content': 'test3',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        self.client_login(self.user_programmer.username, 'testpassword')
        url = reverse('api_tasker:task-comment', args=[self.task_author_userit.id])
        data = {
            'title': 'test',
            'content': 'test',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_change(self):
        self.client_login(self.user_author.username, 'testpassword')
        url = reverse('api_tasker:task-change', args=[self.task_author_userit.id])
        data = {
            'title': 'Super test',
            'description': 'test',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Super test')

        self.client_login(self.user_programmer.username, 'testpassword')
        url = reverse('api_tasker:task-change', args=[self.task_author_userit.id])
        data = {
            'title': 'Super test',
            'description': 'test',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client_login(self.user_it.username, 'testpassword')
        url = reverse('api_tasker:task-change', args=[self.task_author_userit.id])
        data = {
            'title': 'Super test',
            'description': 'test',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update(self):
        self.client_login(self.user_author.username, 'testpassword')
        url = reverse('api_tasker:task-detail', args=[self.task_author_userit.id])
        data = {
            'title': 'Super test',
            'description': 'test',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client_login(self.user_programmer.username, 'testpassword')
        url = reverse('api_tasker:task-detail', args=[self.task_author_userit.id])
        data = {
            'title': 'Super test',
            'description': 'test',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client_login(self.user_programmer.username, 'testpassword')
        url = reverse('api_tasker:task-detail', args=[self.task_userit_userprogrammer.id])
        data = {
            'title': 'Super test',
            'description': 'test',
            'dedlin_date': timezone.now(),
            'group': self.group_programmer.id,
        }
        response = self.client.patch(url, data, format='json')
        print(json.dumps(response.data, indent=4, ensure_ascii=False))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RequestAPITest(APITestCase):
    def setUp(self):
        # Groups
        self.group_admin = Group.objects.create(name='admin')
        self.group_it = Group.objects.create(name='it')
        self.group_programmer = Group.objects.create(name='programmer')
        # Permissions
        self.group_admin.permissions.add(Permission.objects.get(codename='view_request'))
        self.group_admin.permissions.add(Permission.objects.get(codename='add_request'))
        self.group_admin.permissions.add(Permission.objects.get(codename='change_request'))
        self.group_admin.permissions.add(Permission.objects.get(codename='delete_request'))

        # Users
        self.admin = User.objects.create_user(username='admin', first_name='admin', last_name='admin',
                                              password='testpassword')
        self.admin.groups.add(self.group_admin)
        self.user_it = User.objects.create_user(username='it', first_name='it', last_name='it',
                                                password='testpassword')
        self.user_it.groups.add(self.group_it)
        self.user_programmer = User.objects.create_user(username='programmer', first_name='programmer', last_name='programmer',
                                                        password='testpassword')
        self.user_programmer.groups.add(self.group_programmer)
        self.author = User.objects.create_user(username='author', first_name='author', last_name='author',
                                               password='testpassword')
        self.executor = User.objects.create_user(username='executor', first_name='executor', last_name='executor',
                                                 password='testpassword')

        self.user = User.objects.create_user(username='user', first_name='user', last_name='user',
                                            password='testpassword')
        # Requests
        self.request_author_executor_it = Request.objects.create(
            title='request_author_executor_it', description='request_author_executor_it#1',
            dedlin_date=timezone.now()+timezone.timedelta(days=1),
            author=self.author, executor=self.executor, group=self.group_it,
        )

        self.request_author_it = Request.objects.create(
            title='request_author_it', description='request_author_it#2',
            dedlin_date=timezone.now()+timezone.timedelta(days=1),
            author=self.author, group=self.group_it,
        )

        self.request_author_programmer = Request.objects.create(
            title='request_author_programmer', description='request_author_programmer#3',
            dedlin_date=timezone.now()+timezone.timedelta(days=1),
            author=self.author, group=self.group_programmer,
        )
        self.request_userit_programmer = Request.objects.create(
            title='request_userit_programmer', description='request_userit_programmer#4',
            dedlin_date=timezone.now()+timezone.timedelta(days=1),
            author=self.user_it, group=self.group_programmer,
        )

        # ApprovalRoute
        self.approval_route = ApprovalRoute.objects.create(
            title='test', description='test',
            author=self.admin,
        )
        ApproveStep.objects.create(
            title='approve_#1', route=self.approval_route,
            order_number=1, approval_type='manager',
        )
        ApproveStep.objects.create(
            title='approve_#2', route=self.approval_route,
            order_number=2, approval_type='manager',
        )
        # RequestTemplate
        self.request_template = RequestTemplate.objects.create(
            title='request_template', description='request_template',
            group=self.group_programmer, approval_route=self.approval_route,
            complexity='med',
        )
        self.request_template.tasks.add(
            TaskTemplate.objects.create(
                title='task_template', description='task_template',
                group=self.group_it,
            )
        )
        self.request_template.tasks.add(
            TaskTemplate.objects.create(
                title='task_template', description='task_template',
                group=self.group_programmer,
            )
        )

    def client_login(self, username='testuser1', password='testpassword'):
        url = reverse('login')
        data = {
            'username': username,
            'password': password,
        }
        response = self.client.post(url, data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')

    def test_list(self):
        self.client_login(self.admin.username, 'testpassword')
        url = reverse('api_tasker:request-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

        self.client_login(self.author.username, 'testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.client_login(self.user_it.username, 'testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        self.client_login(self.user_programmer.username, 'testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.client_login(self.executor.username, 'testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


    def test_detail(self):
        self.client_login(self.admin.username, 'testpassword')
        url = reverse('api_tasker:request-detail', args=[self.request_author_programmer.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'request_author_programmer')

        self.client_login(self.author.username, 'testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'request_author_programmer')

        self.client_login(self.user_programmer.username, 'testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'request_author_programmer')

        self.client_login(self.user_it.username, 'testpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        # Crete Request use
        self.client_login(self.user.username, 'testpassword')
        url = reverse('api_tasker:request-list')
        data = {
            'title': 'test',
            'description': 'test',
            'request_template': self.request_template.id,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'test')
        pass
    #
    # def test_update(self):
    #     pass
    #
    # def test_change(self):
    #     pass
    #
    # def test_cansel(self):
    #     pass
    #
    # def test_check(self):
    #     pass








