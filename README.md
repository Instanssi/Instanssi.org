Instanssi.org website project
=============================

What is this ?
--------------
This project right here is the website of instanssi.org demoparty. It contains the main website (main20xx),
Kompomaatti (our compo entry management interface), and Arkisto (our entry archive site). Most
of the comments and language used is in Finnish, because the programmers weren't interested in 
internationalization :D

This project has been originally developed for Instanssi 2012. Project is still alive and current development
focus is to provide web site for Instanssi 2023.

Requirements
------------

* Python 3.9.x (`https://www.python.org/`)
* Poetry package manager (`https://python-poetry.org/docs/#installation`)
* PostgreSQL or SQLite for database. SQLite should be fine for testing
  and development purposes. MariaDB/MySQL is not tested or supported.

Installing stuff for development
--------------------------------

1. Install the dependencies and clone this project.
2. Copy `settings.py-dist` to `settings.py`. Change as needed. `settings.py` should never be added to
   git, as it may contain secrets.
3. Set up environment with poetry `poetry env use 3.9`.
4. Install packages with poetry `poetry install --no-root`.
5. Make sure your database is set up and configured in settings.py, and then run database
   migrations to set up initial data `python manage.py migrate`.
6. Create a superuser so that you can access the admin `python manage.py createsuperuser`.
7. That's all. Now just start local dev server by running `python manage.py runserver`.

Note that some background operations use celery. It can be started with following:
`python -m celery -A Instanssi worker -l info --autoscale 2,1`

Production deps
---------------

To install in production, remember to generate a new requirements.txt file.

`poetry export --with=runtime -f requirements.txt -o requirements.txt`.

License
-------
MIT. Please refer to `LICENSE` for more information.