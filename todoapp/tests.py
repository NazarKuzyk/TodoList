import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from todoapp.models import Task, STATUS_CHOICES, PRIORITY_CHOICES


class TaskModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_task_creation(self):
        task = Task.objects.create(
            user = self.user, 
            title = 'Test Task', 
            description = 'Test Description', 
            status = 'Completed',     
            priority = 'High'
        )
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'Test Description')
        self.assertEqual(task.status, 'Completed')
        self.assertEqual(task.priority, 'High')

    def test_default_status_and_priority(self): 
        task = Task.objects.create(
            user=self.user,
            title='Default Task',
            description='Default Description',
        )

        self.assertEqual(task.status, 'Incomplete')
        self.assertEqual(task.priority, 'Medium')

    def test_status_choices(self): 
        for choice in STATUS_CHOICES:
            task = Task.objects.create(
                user=self.user,
                title='Status Test',
                description='Status Description',
                status=choice[0]
            )

            self.assertIn(task.status, dict(STATUS_CHOICES).keys())

    def test_priority_choices(self): 
        for choice in PRIORITY_CHOICES:
            task = Task.objects.create(
                user=self.user,
                title='Priority Test',
                description='Priority Description',
                priority=choice[0]
            )

            self.assertIn(task.priority, dict(PRIORITY_CHOICES).keys())

    def test_str_representation(self): 
        task = Task.objects.create(
            user=self.user,
            title='String Test Task',
            description='String Test Description',
        )

        self.assertEqual(str(task), 'String Test Task')


class UserLoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')

    def test_login_authenticated_user(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task'))

    def test_login_unauthenticated_user_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todoapp/login.html')


class LogoutViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = reverse('logout')
        self.login_url = reverse('login')

    def test_logout_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.login_url)

    def test_logout_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, self.login_url)


class UserRegisterViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('register')
        self.login_url = reverse('login')
        self.task_url = reverse('task')
        self.form_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

    def test_register_authenticated_user(self):
        user = User.objects.create_user(username='existinguser', password='existingpassword')
        self.client.login(username='existinguser', password='existingpassword')
        response = self.client.get(self.url)
        self.assertRedirects(response, self.task_url)

    def test_register_unauthenticated_user_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TaskListViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.task1 = Task.objects.create(user=self.user, title='Task 1')
        self.task2 = Task.objects.create(user=self.user, title='Task 2')
        self.other_user = User.objects.create_user(username='otheruser', password='otherpassword')
        self.task3 = Task.objects.create(user=self.other_user, title='Other User Task')
        self.url = reverse('task')

    def test_task_list_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        tasks = response.context['task']
        self.assertEqual(list(tasks), [self.task1, self.task2])

    def test_task_list_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('login') + '?next=/')


class TaskDetailViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.task = Task.objects.create(user=self.user, title='Test Task')
        self.url = reverse('tasks-detail', kwargs={'pk': self.task.pk})

    def test_task_detail_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['task'], self.task)
        self.assertTemplateUsed(response, 'todoapp/task.html')

    def test_task_detail_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse( 'login') + '?next=/' + 'task/1/')


class TaskCreateViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.url = reverse('task-create')  
        self.login_url = reverse('login')
        self.task_data = {
            'title': 'New Task',
            'description': 'Task Description',
            'status': 'Completed',
            'priority': 'High',
        }

    def test_task_create_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, data=self.task_data)
        self.assertRedirects(response, reverse('task'))

    def test_task_create_unauthenticated_user(self):
        response = self.client.post(self.url, data=self.task_data)
        self.assertRedirects(response, reverse( 'login') + '?next=/' + 'task-create/')


class TaskUpdateViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.task = Task.objects.create(user=self.user, title='Test Task')
        self.url = reverse('task-update', kwargs={'pk': self.task.pk})
        self.login_url = reverse('login')
        self.task_data = {
            'title': 'Updated Task',
            'description': 'Updated Task Description',
            'status': 'Completed',
            'priority': 'High',
        }

    def test_task_update_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, data=self.task_data)
        self.assertRedirects(response, reverse('task'))

    def test_task_update_unauthenticated_user(self):
        response = self.client.post(self.url, data=self.task_data)
        self.assertRedirects(response, reverse( 'login') + '?next=/' + 'task-update/1/')


class TaskDeleteViewTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.task = Task.objects.create(user=self.user, title='Test Task')
        self.url = reverse('task-delete', kwargs={'pk': self.task.pk})
        self.login_url = reverse('login')  

    def test_task_delete_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('task')) 

    def test_task_delete_unauthenticated_user(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse( 'login') + '?next=/' + 'task-delete/1/')


if __name__ == '__main__':
    unittest.main()