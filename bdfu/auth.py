"""
User authentication.

"""

import jwt
import datetime

def make_user_token(username, secret):
    """Given a username and server secret, generate an authorization token for
    the given user.

    """
    return _jwt_token(dict(user=username), secret)

def _to_numeric(dt):
    """Convert a datetime instance to a numeric date as per JWT spec."""
    return int((dt - datetime.datetime.utcfromtimestamp(0)).total_seconds())

def _jwt_token(payload, secret, headers=None, algorithm='HS256',
        expires_in=30, with_times=True, **kwargs):
    """Return a JWT with the given payload. Any remaining keyword args are
    passed to jwt.encode().

    If payload is None, an empty payload is used.

    If headers is None, no headers are added beyone 'exp' and 'nbf'.

    The standard 'exp' and 'nbf' claims are added. In addition, the 'exp' claim
    is added into the header. The 'exp' time is now plus the number of seconds
    specified as expires_in.

    Note that if the passed payload has 'exp' and/or 'nbf' claims, these are
    used in preference.

    """
    if payload is None:
        payload = {}

    if headers is None:
        headers = {}

    if algorithm is None:
        raise ValueError('Bad algorithm')

    if secret is None:
        raise ValueError('Bad secret')

    if with_times:
        ext_payload = dict(
            exp=_to_numeric(datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)),
            nbf=_to_numeric(datetime.datetime.utcnow()),
        )

        # Update the extended payload with passed payload
        ext_payload.update(payload)
        payload = ext_payload

        # Add 'exp' to headers if not already present
        if 'exp' not in headers:
            headers['exp'] = ext_payload['exp']

    return jwt.encode(payload, secret, algorithm, headers=headers, **kwargs)


