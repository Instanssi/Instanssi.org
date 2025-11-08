Instanssi.org backend
=====================

This is the backend of the Instanssi.org website.

Requirements
------------

* Python 3.13.x (`https://www.python.org/`)
* Poetry package manager (`https://python-poetry.org/docs/#installation`)
* PostgreSQL or SQLite for database. SQLite should be fine for testing
  and development purposes. MariaDB/MySQL is not tested or supported.
* Redis 5 or later (production only, not required for development)

Installing stuff for development
--------------------------------

1. Install the dependencies and clone this project.
2. Copy `settings.py-dist` to `settings.py`. Change as needed. `settings.py` should never be added to
   git, as it may contain secrets.
3. Set up environment with poetry `poetry env use 3.13`.
4. Install packages with poetry `poetry install --no-root --sync`.
5. Make sure your database is set up and configured in settings.py, and then run database
   migrations to set up initial data `python manage.py migrate`.
6. Create test data using a command `python manage.py create_test_data`. This will also set up a test
   admin user (username and password is "admin").
7. That's all. Now just start local dev server by running `python manage.py runserver`.

Note that some background operations use celery. It can be started with following:
`python -m celery -A Instanssi worker -l info --autoscale 2,1`

Test Data and Credentials
--------------------------

The `create_test_data` management command creates comprehensive test data for development:

**What it creates:**
* Events & test users
* Compos (Graphics, Music, Demo) in different states
* Entries with realistic data and files
* Votes and voting data
* Competitions and participations
* Vote code requests
* Blog entries for events

**Login credentials (password = username):**
* `admin` / `admin` - Admin user (staff + superuser)
* `testuser1` / `testuser1` - Regular user with entries
* `testuser2` / `testuser2` - Regular user with entries
* `voter1` / `voter1` - User who votes in compos
* `voter2` / `voter2` - User who votes in compos

Running in production
---------------------

Either use gunicorn (WSGI) or uvicorn (ASGI). In production, preferably gunicorn
with uvicorn runner.

* With gunicorn: `gunicorn` (it automatically uses the gunicorn.conf.py config file)
* With uvicorn: `uvicorn Instanssi.asgi:application` (No other config needed)

Note that gunicorn does not work on windows due to missing fcntl package, so there your
best bet is uvicorn.

Deploying
---------

When deploying, the following steps need to be run:

```
python manage.py collectstatic --noinput --ignore **/*.scss
python manage.py compress
python manage.py migrate
```

After this, restart the WSGI/ASGI runner.

Running tests
-------------

Just do `pytest` in the main directory :)

To also get coverage, do `pytest --cov=Instanssi`

Also, you can run tests in parallel using `pytest -n 4`.
