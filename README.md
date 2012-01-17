Instanssi.org 2012 website project
==================================

What is this ?
--------------
This project right here is the website of instanssi.org demoparty. It contains the main website (main2012),
Kompomaatti (our compo entry management interface), and Instanssi Arkisto (our entry archive site). Most
of the comments and language used is in Finnish, because the programmers weren't interested in 
internationalization :D

License:
--------
MIT. Please refer to `LICENSE` for more information.

Mikä on tämä ?
--------------
En jaksa kirjoittaa suomeksi, lue ylläolevat :D

Oppaita
-------
* Djangon asennus: https://docs.djangoproject.com/en/dev/topics/install/?from=olddocs#installing-an-official-release
* Tutoriaali: https://docs.djangoproject.com/en/1.3/intro/tutorial01/

Windows-asennus
---------------
1. Asenna Python, 2.6 tai 2.7 on ok (http://www.python.org). Varmista, että pythonin bin- 
   ja scripts-kansiot ovat windowsin PATHissa.
2. Asenna setuptools (http://pypi.python.org/pypi/setuptools). 
3. Asenna PIP (http://pypi.python.org/pypi/pip) komennolla `easy_install pip`.
4. Asenna allaolevat kirjastot PIPillä.
5. Nouki tämä projekti gitillä (git clone ...).
6. Suorita syncdb projektihakemistossa (`python manage.py syncdb`).
7. Testaa ajamalla runserver (`python manage.py runserver`).

Linux-asennus
-------------
1. Asenna PIP distrosi paketinhallinnalla, esim. `apt-get install python-pip`.
2. Asenna allaolevat kirjastot joko käyttäen PIP:ä tai distron pakettienhallintaa.
3. Nouki tämä projekti gitillä (git clone ...).
4. Suorita syncdb projektihakemistossa (`python manage.py syncdb`).
5. Testaa ajamalla runserver (`python manage.py runserver`).

Kirjastot
---------
* [Django 1.3.1] (https://www.djangoproject.com/download/) `pip install django`
* [django-openid-auth 0.4] (https://launchpad.net/django-openid-auth) `pip install django-openid-auth`
* [python-openid 2.2.5 or later] (https://github.com/openid/python-openid/) `pip install python-openid`
* [PIL 1.1.7 or later] (http://www.pythonware.com/products/pil/) `pip install pil`
* [django-imagekit 1.1.0 or later] (https://github.com/jdriscoll/django-imagekit) `pip install django-imagekit`
* [South 0.7.3 or later] (http://south.aeracode.org/) `pip install south`

IDEjä
-----
* Eclipse (addonit: PyDev + EGIt)
* Aptana Studio 3
