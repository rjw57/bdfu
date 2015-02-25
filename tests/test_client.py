from io import BytesIO
import uuid
from mock import patch

from future import standard_library
standard_library.install_aliases()

from urllib.parse import urljoin

from flask.ext.testing import TestCase
import pytest
import responses

from bdfu.auth import make_user_token
from bdfu.client import Client, ClientError
from bdfu.webapp import app

def add_responses_post_handler(from_url, client, to_url):
    """Add a responses handler for from_url mapping to the werkzeug HTTP test
    client at to_url.

    """
    def post_callback(request):
        resp = client.post(to_url, data=request.body, headers=list(request.headers.items()))
        return resp.status_code, resp.headers, resp.data

    responses.add_callback(
        responses.POST, from_url,
        callback=post_callback, content_type='application/json'
    )

class ClientTestCase(TestCase):
    def create_app(self):
        # Create and record a secret key
        self.secret = uuid.uuid4().hex

        # Create a mock endpoint
        self.endpoint = 'http://mock.endpoint.example.com/root/'

        # Configure application
        app.config['JWT_SECRET_KEY'] = self.secret
        app.debug = True
        app.config
        return app

    def _add_post_handler(self, url):
        add_responses_post_handler(urljoin(self.endpoint, url), self.client, url)

    @responses.activate
    @patch('bdfu.webapp._get_storage')
    def test_simple_upload(self, gs_mock):
        """Simple uploading should succeed."""
        # Create the client and auth token
        username = 'myusername'
        token = make_user_token(username, self.secret)
        client = Client(self.endpoint, token)

        # Create a random file contents
        file_contents = uuid.uuid4().bytes

        # Add responses wrapper
        self._add_post_handler('upload')

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

        # Perform upload
        created_id = client.upload(BytesIO(file_contents))

        # Check write was called exactly once
        assert gs_mock().write.call_count == 1

        # Check that the storage was passed the right values
        assert stored_state['username'] == username
        assert stored_state['contents'] == file_contents

        # Check the id made its way back to us
        assert created_id == new_id

    @responses.activate
    def test_wrong_endpoint(self):
        """A bad endpoint should fail."""
        # Create the client and auth token
        username = 'myusername'
        token = make_user_token(username, self.secret)
        client = Client(self.endpoint, token)
        file_contents = uuid.uuid4().bytes

        # Attempt upload
        with pytest.raises(responses.ConnectionError):
            client.upload(BytesIO(file_contents))
