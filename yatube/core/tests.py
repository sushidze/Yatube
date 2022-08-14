from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class CoreUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()

    def test_404_url_uses_correct_template(self):
        response = self.authorized_client.get('/not_found')
        self.assertTemplateUsed(response, 'core/404.html')
