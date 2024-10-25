import os
from django.core.wsgi import get_wsgi_application
from django.core.asgi import get_asgi_application

from django.test import TestCase

class WSGIApplicationTest(TestCase):
    def setUp(self):
        # Set the DJANGO_SETTINGS_MODULE environment variable
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bloga.settings')

    def test_wsgi_application(self):
        """Test that the WSGI application is properly initialized."""
        application = get_wsgi_application()
        self.assertIsNotNone(application)  # Ensure the application is not None
        self.assertTrue(callable(application))  # Ensure the application is callable


class ASGIApplicationTest(TestCase):
    def setUp(self):
        # Set the DJANGO_SETTINGS_MODULE environment variable
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Bloga.settings')

    def test_asgi_application(self):
        """Test that the ASGI application is properly initialized."""
        application = get_asgi_application()
        self.assertIsNotNone(application)  # Ensure the application is not None
        self.assertTrue(callable(application))  # Ensure the application is callable
        