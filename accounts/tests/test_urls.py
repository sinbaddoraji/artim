from django.test import SimpleTestCase
from django.urls import resolve, reverse
from accounts.views import CompleteProfile, user_login

class TestUrls(SimpleTestCase):

    def test_login_url(self):
        # reverse gets the url using the url name
        url = reverse('accounts:login')

        # resolve gets the view details name using the url
        self.assertEquals(resolve(url).func, user_login)


    def test_complete_profile_url(self):
        url = reverse('accounts:social_complete_profile')
        self.assertEquals(resolve(url).func.view_class, CompleteProfile)