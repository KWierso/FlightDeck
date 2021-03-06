import httplib2
import json

from django.conf import settings
from django.test import TestCase
from django.contrib.auth import authenticate

from mock import Mock
from nose import SkipTest
from nose.tools import eq_

from amo.authentication import AMOAuthentication
from amo.helpers import fetch_amo_user
from utils.amo import AMOOAuth


OLD_AMOOAUTH_SEND = AMOOAuth._send
OLD_AMOOAUTH_REQUEST = AMOOAuth._request
OLD_HTTPLIB2_HTTP = httplib2.Http

class AuthTest(TestCase):

    def tearDown(self):
        AMOOAuth._send = OLD_AMOOAUTH_SEND
        AMOOAuth._request = OLD_AMOOAUTH_REQUEST
        httplib2.Http = OLD_HTTPLIB2_HTTP

    def test_failing_login(self):
        # testing failed authentication on AMO
        # this test assumes FlightDeck has access to AMO database
        self.assertEqual(
            None,
            authenticate(
                username='non existing',
                password='user')
            )

    @staticmethod
    def test_successful_login():
        # if settings_local contains AMO user data  check if login is
        # successful
        # assumes that FlightDeck has access to AMO database
        if not (settings.TEST_AMO_USERNAME and settings.TEST_AMO_PASSWORD):
            raise SkipTest()
        assert authenticate(
                username=settings.TEST_AMO_USERNAME,
                password=settings.TEST_AMO_PASSWORD)

    @staticmethod
    def test_get_user():
        class Response:
            status = 200

        class Http:
            request = Mock(return_value=(
                Response(),
                json.dumps({
                    "username": "some",
                    "display_name": "Some User",
                    "created": "2007-03-05 13:09:38",
                    "modified": "2012-01-31 12:38:50",
                    "id": 12345,
                    "location": "Portland, OR",
                    "homepage": "http://example.com",
                    "email": "some@example.com",
                    "occupation": "addon developer"
                })))
        httplib2.Http = Mock(return_value=Http())
        eq_(fetch_amo_user('some@example.com')['username'],
                'some')
