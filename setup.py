from setuptools import setup, find_packages

setup(
    name="bdfu",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Py2/3 compat
        "future",

        # Authentication
        "pyjwt",

        # Client
        "requests",

        # Server
        "flask",
        "flask-jwt",
        "flask-script",
    ],
    tests_require=[
        "pytest",
    ],
)
