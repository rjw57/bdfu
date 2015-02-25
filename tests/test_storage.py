"""
Test the file storage backend.

"""
from contextlib import contextmanager
from io import BytesIO
import os
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

from bdfu.storage import Storage

@contextmanager
def temp_storage(prefix='storagetest'):
    """Create a new Storage object in a temporary directory. Delete temporary
    directory on exit from context.

    """
    destdir = mkdtemp(prefix=prefix)
    yield Storage(destdir)
    rmtree(destdir)

def test_context_manager():
    """Context manager should create temporary directory and delete it afterwards."""
    with temp_storage() as s:
        dd = s.destdir
        assert os.path.isdir(dd)
    assert not os.path.exists(dd)

def test_dest_dir():
    """Storage should set the destdir attribute."""
    with temp_storage('testing-destdir') as s:
        assert s.destdir is not None
        assert 'testing-destdir' in s.destdir

def test_simple_write():
    """Storage should write file's contents to <user>/<uuid> and return
    <uuid>.

    """
    # Get some random bytes to be file contents
    contents = os.urandom(1024)

    with temp_storage() as storage:
        # Write to "testuser"
        username = 'testuser'
        file_id = storage.write(username, BytesIO(contents))
        assert file_id is not None

        # Does file exist?
        expected_path = os.path.join(storage.destdir, username, file_id)
        assert os.path.isfile(expected_path)

        # Does it have correct contents?
        with open(expected_path, 'rb') as f:
            assert f.read() == contents


def test_repeat_write():
    """Storage should write file's contents to <user>/<uuid> and return
    <uuid>. It should support multiple writes and <uuid>s should differ/

    """
    # Get some random bytes to be file contents
    contents = os.urandom(1024)

    with temp_storage() as storage:
        # Write to "testuser"
        username = 'testuser'
        file_id_1 = storage.write(username, BytesIO(contents))
        assert file_id_1 is not None

        # Does file exist?
        expected_path = os.path.join(storage.destdir, username, file_id_1)
        assert os.path.isfile(expected_path)

        # Does it have correct contents?
        with open(expected_path, 'rb') as f:
            assert f.read() == contents

        file_id_2 = storage.write(username, BytesIO(contents))
        assert file_id_2 is not None

        # Does file exist?
        expected_path = os.path.join(storage.destdir, username, file_id_2)
        assert os.path.isfile(expected_path)

        # Does it have correct contents?
        with open(expected_path, 'rb') as f:
            assert f.read() == contents

        # File ids should differ
        assert file_id_1 != file_id_2

