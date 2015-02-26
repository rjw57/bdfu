"""
Basic functionality tests for web application.
"""
import uuid

from io import BytesIO

from flask import current_app
from flask.ext.testing import TestCase
import pytest
from mock import patch

from bdfu.auth import _jwt_token
from bdfu.webapp import app

def jwt_headers(*args, **kwargs):
    """Like _jwt_token() but return a dict of headers containing HTTP
    Authorization bearer token using the JWT.

    """
    return { 'Authorization': 'Bearer ' + _jwt_token(*args, **kwargs).decode('ascii') }

def jwt_payload(user=None):
    """Create a minimally valid JWT payload. If user is None, use "testuser".

    """
    if user is None:
        user = 'testuser'
    return dict(user=user)

class WebAppTestCase(TestCase):
    def create_app(self):
        # Create and record a secret key
        self.secret = uuid.uuid4().hex

        # Configure application
        app.config['JWT_SECRET_KEY'] = self.secret
        app.debug = True
        return app

    def test_have_secret_key(self):
        """We have a key and that key is a string."""
        assert isinstance(current_app.config['JWT_SECRET_KEY'], str)

    def test_get_not_allowed(self):
        """GET-ing .../upload returns Method Not Allowed (405)."""
        assert self.client.get('/upload').status_code == 405

    def test_empty_post_fails(self):
        """POST-ing without JWT is Unauthorized (401)."""
        assert self.client.post('/upload').status_code == 401

    def test_empty_post_fails(self):
        """POST-ing with incorrect JWT is a Bad Request (400)."""
        auth_headers = jwt_headers(jwt_payload(), 'this is not the secret')
        assert self.client.post('/upload', headers=auth_headers).status_code == 400

    def test_poorly_configured_app_fails(self):
        """POST-ing with JWT authentication but no secret raises an Exception in debug and
        is an Internal Server Error (500) in production.

        """
        # Check we have a secret at the moment
        assert self.secret is not None
        assert current_app.config['JWT_SECRET_KEY'] is not None

        # Remove secret
        current_app.config['JWT_SECRET_KEY'] = None

        # in debug...
        current_app.debug = True
        with pytest.raises(Exception):
            self.client.post(
                '/upload', headers=jwt_headers(jwt_payload(), self.secret)
            )

        # in production...
        current_app.debug = False
        assert self.client.post(
            '/upload', headers=jwt_headers(jwt_payload(), self.secret)
        ).status_code == 500

    def test_empty_authorised_post_fails(self):
        """POST-ing an authorised empty body is a Bad Request (400)."""
        auth_headers = jwt_headers(jwt_payload(), self.secret)
        assert self.client.post('/upload', headers=auth_headers).status_code == 400

    def test_authorised_post_needs_user(self):
        """POST-ing an authorized non-empty body with file results in a Bad
        Request (400) if the user is not present.

        """
        pl = jwt_payload()
        del pl['user']
        auth_headers = jwt_headers(pl, self.secret)

        # Create a random file contents
        file_contents = BytesIO(uuid.uuid4().bytes)

        resp = self.client.post(
            '/upload', headers=auth_headers,
            data=dict(file=(file_contents, 'test_file.bin')),
        )
        assert resp.status_code == 400

    @patch('bdfu.webapp._get_storage')
    def test_authorised_post_succeeds(self, gs_mock):
        """POST-ing an authorized non-empty body with file results in a file
        being Created (201).

        """
        auth_headers = jwt_headers(jwt_payload(user='myuser'), self.secret)

        # Create a random file contents
        file_contents = uuid.uuid4().bytes

        # Mock the storage's write method to record it's call values
        new_id = uuid.uuid4().hex
        stored_state = {}
        def side_effect(username, fobj):
            # HACK: we need to use str() here as a "copy" since the user is
            # passed as current_user which is only a proxy object for the real
            # username. Without the call to str(), the username would be
            # "None" by the time we check it.
            stored_state['username'] = str(username)
            stored_state['contents'] = fobj.read()
            return new_id
        gs_mock().write.side_effect = side_effect

        # Upload a file
        resp = self.client.post(
            '/upload', headers=auth_headers,
            data=dict(file=(BytesIO(file_contents), 'test_file.bin')),
        )

        # Check write was called exactly once
        assert gs_mock().write.call_count == 1

        # Check that the storage was passed the right values
        assert stored_state['username'] == 'myuser'
        assert stored_state['contents'] == file_contents

        # Check that we Created the correct file
        assert resp.status_code == 201
        assert resp.json['id'] == new_id
