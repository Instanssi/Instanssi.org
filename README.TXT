### Instanssi.org 2012 website project

--- What is this ?
This project right here is the website of instanssi.org demoparty. It contains the main website (main2012),
Kompomaatti (our compo entry management interface), and Instanssi Arkisto (our entry archive site). Most
of the comments and language used is in Finnish, because the programmers weren't interested in 
internationalization :D

--- License:
MIT. Please refer to LICENSE.TXT for more information.

--- Mikä on tämä ?
En jaksa kirjoittaa suomeksi, lue ylläolevat :D

--- Oppaita:
Django:
- Asennus: https://docs.djangoproject.com/en/dev/topics/install/?from=olddocs#installing-an-official-release
- Tutoriaali: https://docs.djangoproject.com/en/1.3/intro/tutorial01/

--- Dependencyt:
Python [2.6, 2.7] (http://python.org/)
django [1.3.1] (https://www.djangoproject.com/download/)
django-openid-auth [0.4] (https://launchpad.net/django-openid-auth)
python-openid [2.2.5 or later] (https://github.com/openid/python-openid/)
PIL [1.1.7 or later] (http://www.pythonware.com/products/pil/)
Django-imagekit [1.1.0 or later] (https://github.com/jdriscoll/django-imagekit)

--- Lyhyehköt asennusohjeet:
1. Hommaa Python ja dependenssit. Asenna ne ohjeiden mukaan.
2. Aja djangon syncdb (python manage.py syncdb)
3. Devaa
4. Testaa ajamalla runserver (python manage.py runserver)

--- IDEjä:
- Eclipse (addonit: PyDev + EGIt)
- Aptana Studio 3