from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages

CustomUser = get_user_model()

class AutenticarTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_group = Group.objects.create(name='admin')
        self.clientes_group = Group.objects.create(name='clientes')
        self.admin_user = CustomUser.objects.create_user(username='adminuser', password='adminpassword')
        self.cliente_user = CustomUser.objects.create_user(username='clienteuser', password='clientepassword')

        # Add users to groups
        self.admin_user.groups.add(self.admin_group)
        self.cliente_user.groups.add(self.clientes_group)

    def test_admin_user_authentication(self):
        response = self.client.post(reverse('acceder'), {
            'username': 'adminuser',
            'password': 'adminpassword'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirection
        self.assertRedirects(response, '/gestionar_usuarios/')  # Check redirection URL with trailing slash

        # Check if the user is authenticated
        user = CustomUser.objects.get(username='adminuser')
        self.assertTrue(user.is_authenticated)

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('satisfactoriamente', str(messages[0]))

    def test_cliente_user_authentication(self):
        response = self.client.post(reverse('acceder'), {
            'username': 'clienteuser',
            'password': 'clientepassword'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirection
        self.assertRedirects(response, '/visualizar_existencias_medicamentos/')  # Check redirection URL with trailing slash

        # Check if the user is authenticated
        user = CustomUser.objects.get(username='clienteuser')
        self.assertTrue(user.is_authenticated)

        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('satisfactoriamente', str(messages[0]))

    def test_invalid_authentication(self):
        response = self.client.post(reverse('acceder'), {
            'username': 'invaliduser',
            'password': 'invalidpassword'
        })
        self.assertEqual(response.status_code, 200)  # No redirection, stays on the same page
        self.assertContains(response, 'form')  # Ensure form is displayed again

        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 0)  # No success message
