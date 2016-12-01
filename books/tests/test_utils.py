from django.test import TestCase

from books.models import Customer

import logging


def pop_message(response):
    """Returns the first message from response context"""
    return list(response.context['messages']).pop(0)


class DisableLogging(TestCase):
    """
    Disables Django Logging Errors
    """
    logger = logging.getLogger('django.request')
    previous_level = logger.getEffectiveLevel()

    def setUp(self):
        # Before Tests
        self.logger.setLevel(logging.ERROR)
        super(DisableLogging, self).setUp()

    def tearDown(self):
        # After tests
        self.logger.setLevel(self.previous_level)
        super(DisableLogging, self).tearDown()


class RequiresLogin(TestCase):
    """
    Mixin for Test cases that require a user to be logged-in to view the
    contents of the page
    """
    def setUp(self):
        # Creates a mock user and logs in client as this user
        self.customer = Customer.objects.create_user(
            'test', 'test@mail.com', 'secret')
        self.client.login(username='test', password='secret')
        super(RequiresLogin, self).setUp()
