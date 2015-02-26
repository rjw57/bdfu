from setuptools import setup, find_packages

setup(
    name="bdfu",
    version="1.0.0",
    packages=find_packages(),
    entry_points=dict(
        console_scripts=[
            'bdfu = bdfu.tool:main',
        ],
    ),
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

        # Command-line tool
        "docopt",
    ],
    tests_require=[
        "pytest",
        "mock",
        "responses",
    ],
)
