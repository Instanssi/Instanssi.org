Instanssi.org 2012 website project
==================================

What is this ?
--------------
This project right here is the website of instanssi.org demoparty. It contains the main website (main2012),
Kompomaatti (our compo entry management interface), and Arkisto (our entry archive site). Most
of the comments and language used is in Finnish, because the programmers weren't interested in 
internationalization :D

License
-------
MIT. Please refer to `LICENSE` for more information.

Mikä on tämä ?
--------------
En jaksa kirjoittaa suomeksi, lue ylläolevat :D

Oppaita
-------
* Djangon asennus: https://docs.djangoproject.com/en/dev/topics/install/?from=olddocs#installing-an-official-release
* Tutoriaali: https://docs.djangoproject.com/en/1.4/intro/tutorial01/

Ympäristön asentaminen Windowsille
----------------------------------
1. Asenna Python, 2.6 tai 2.7 on ok (http://www.python.org). Varmista, että pythonin juurikansio (se josta löytyy python.exe)
   ja scripts-kansiot ovat windowsin PATHissa. Kannattaa ladata 32bit versio, vaikka olisikin 64bit windows. Helpompi saada
   kirjastot. Mikäli ehdottomasti haluat asentaa 64bit versiot, niin osa paketeista on ladattavissa osoitteesta 
   http://www.lfd.uci.edu/~gohlke/pythonlibs/ .
2. Asenna setuptools (http://pypi.python.org/pypi/setuptools). 
3. Asenna PIP (http://pypi.python.org/pypi/pip) komennolla `easy_install pip`.
4. Asenna kappaleessa "Projektin asentaminen" mainitut kirjastot PIP:llä.

Ympäristön asentaminen Linuxeille
---------------------------------
1. Asenna PIP distrosi paketinhallinnalla, esim. `apt-get install python-pip`.
2. Asenna kappaleessa "Projektin asentaminen" mainitut kirjastot joko käyttäen PIP:iä tai distrosi pakettienhallintaa. 
   PIL-kirjaston asennus käyttäen PIP:ä saattaa vaatia jotain lisäkirjastoja kääntämiseen. Lisäkirjastojen asentamisen
   saattaa pystyä välttämään asentamalla PIL:n suoraan distron pakettienhallinnasta, esim. `apt-get install python-imaging` tjsp.
   Mikäli asennat virtualenv:n, kannattaa käyttää PIL-kirjaston sijasta PILLOW-kirjastoa.

Projektin asentaminen
---------------------
1. Kloonaa tämä projekti gitillä (git clone ...).
2. Kopioi `settings.py-dist` tiedostoksi `settings.py`.
2. Suorita syncdb projektihakemistossa (`python manage.py syncdb`).
3. Suorita migrate projektihakemistossa (`python manage.py migrate`).
4. Testaa ajamalla runserver (`python manage.py runserver`). Jos gittiin ilmestyy tietokantamallimuutoksia, saattaa
   joskus olla tarpeen suorittaa migrate ja syncdb uudelleen.

Kirjastot
---------
* [Django 1.5 tai uudempi] (https://www.djangoproject.com/download/) `pip install django`
* [django-openid-auth] (https://launchpad.net/django-openid-auth) `pip install django-openid-auth`
* [django-countries] (https://bitbucket.org/smileychris/django-countries) `pip install django-countries`
* [python-openid] (https://github.com/openid/python-openid/) `pip install python-openid`
* [PIL] (http://www.pythonware.com/products/pil/) `pip install pil`
* [django-imagekit] (https://github.com/jdriscoll/django-imagekit) `pip install django-imagekit`
* [South] (http://south.aeracode.org/) `pip install south`
* [django-crispy-forms] (http://django-crispy-forms.readthedocs.org/) `pip install django-crispy-forms`
* [reportlab] (http://www.reportlab.com/software/opensource/rl-toolkit/download/) `pip install reportlab`
* [django-twitter-tag] (https://github.com/coagulant/django-twitter-tag) `pip install django-twitter-tag`

Onelineri kirjastojen asentamiseen
----------------------------------
Seuraava koodirimpsu hakee kaikki tarpeelliset python-kirjastot ja dependenssit.

    pip install django django-openid-auth python-openid django-countries django-imagekit south django-crispy-forms reportlab pil django-twitter-tag

IDEjä
-----
* Eclipse (addonit: PyDev + EGIt)
* Aptana Studio 3

Testitapausten ajaminen
-----------------------

testing/ -hakemistossa on esimerkkejä Robot Framework - Selenium 2 -testeistä, joilla voidaan automatisoida nettisivujen klikkailua.

Testien ajamiseen tarvitset robotframework-selenium2library -palikan:

    pip install robotframework-selenium2library

Tämän jälkeen testin voi ajaa testing-hakemistossa komennolla

    pybot -d output/ testinnimi.txt

Testi tuottaa output-hakemistoon testiraportin ja kuvakaappauksen lopputilastaan.
