# bdfu: a "brain dead"-simple file upload server

[![Build Status](https://travis-ci.org/rjw57/bdfu.svg?branch=master)](https://travis-ci.org/rjw57/bdfu)

BDFU is designed to solve the single problem of letting one or more users
upload files to some server in an authenticated manner. Specifically, the
following simplifications are made:

*   The users may not choose the filename of the uploaded file; each file is
    named with a
    [UUID](http://en.wikipedia.org/wiki/Universally_unique_identifier).

*   Users may not access the files once uploaded. Allowing users read-access to
    the uploaded files is an orthogonal problem.

*   Users are authenticated with finite-lifetime [JWT](http://jwt.io/) tokens
    which may be issued manually or automatically.

*   The server requires nothing more than Python and a CGI-capable web-server
    although is available as a
    [WSGI](http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)
    application for greater performance.

## Installation and getting started

Installation is done via ``pip`` or ``easy_install``:

```console
$ pip install bdfu
```

The development version may be installed directly from this repository:

```console
$ pip install -e git+https://github.com/rjw57/bdfu#egg=bdfu
```


