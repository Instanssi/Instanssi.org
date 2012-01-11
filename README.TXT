### Instanssi.org 2012 website project

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
1. Hommaa Python, Django, dependenssikirjastot. Asenna ne ohjeiden mukaan.
2. Aja djangon syncdb (python manage.py syncdb)
3. Devaa
4. Testaa ajamalla runserver (python manage.py runserver)

--- Lyhyesti projektista:
Idea siis on, että appis hakemistossa Instanssi/main2012 toimii vuoden 2012 instanssin etusivuna. 
Muita appeja olisi esim. ensi vuoden instansseissa Instanssi/main2013 ja niin edelleen.
Myös kompomaatti ja arkisto olisivat appiksia täällä, eli Instanssi/kompomaatti ja Instanssi/arkisto. 