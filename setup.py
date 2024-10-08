import io

from setuptools import find_packages
from setuptools import setup

from hm_api.version import __version__ as HM_API_VERSION

with io.open("README.md", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="hm_api",
    version=HM_API_VERSION,
    url="",
    license="",
    author="Nick Sherron",
    # package_dir={"", "hm_api"},
    packages=find_packages(),
    package_data={
        "hm_api": ["*.db", "hm_api/*.db", "*.json", "hm_api/*.json"],
    },
    include_package_data=True,
    author_email="nsherron90@gmail.com",
    description="Howard Miller and Heckman rest api",
    long_description=readme,
    extras_require={
        "dev": [
            "black",
            "neovim",
            "jedi",
            "ipython @ git+https://github.com/mskar/ipython@auto_suggest",
            "pytest",
            "pytest-selenium",
            "isort",
            "pylint",
            "pylint_sqlalchemy",
            "pylint_flask",
            "pylint_flask_sqlalchemy",
            "flask-shell-ipython",
            "jupyterlab",
            "flask-sqlacodegen",
            # "data-science-types",
            "sqlalchemy-stubs",
            "yapf",
        ]
    },
    install_requires=[
        "flask",
        "pandas",
        "SQLAlchemy",
        "Flask-SQLAlchemy",
        "Flask-API",
        "requests",
        "gunicorn",
        "redis",
        "aiohttp",
        "gspread",
        "gspread_dataframe",
        "oauth2client",
        "sendgrid",
        "Flask-HTTPAuth",
        "lxml",
        "psycopg2-binary",
        "pangres",
        "Flask-CLI",
        "python-dotenv",
        "loguru",
        "stringcase",
        "pandas-gbq",
        "celery",
        "flower",
        "Flask-Uploads",
        "Flask-WTF",
        "werkzeug",
        "flask-admin @ git+https://github.com/nicksherron/flask-admin@v1.5.7-alpha#egg=flask-admin",
        "Flask-Session",
        "sqlalchemy-repr",
        "consulate",
        "blinker",
        "bs4",
        "html5lib",
        "pwkit",
        "flask-sse",
        "gunicorn",
        "gevent",
        "Flask-Opentracing",
        "jaeger-client",
        "influxdb",
        "dataset",
        "walrus",
        "eventlet",
        "google-cloud-pubsub",
        "google-api-python-client",
        "boto3",
        "python-docx",
        "docx2pdf",
        "google-cloud-storage",
        "xlrd==1.2.0",
        "fs",
        "appdirs",
    ],
)
