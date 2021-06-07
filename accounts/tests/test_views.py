from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import *


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

    def test_artisan_list_page(self):
        response = self.client.get(reverse('index', args=['barber']))

        self.assertEquals(response.status_code, 200)