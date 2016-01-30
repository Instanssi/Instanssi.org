Instanssi.org website project
=============================

[![Build Status](https://travis-ci.org/Instanssi/Instanssi.org.svg?branch=master)](https://travis-ci.org/Instanssi/Instanssi.org)

What is this ?
--------------
This project right here is the website of instanssi.org demoparty. It contains the main website (main2012),
Kompomaatti (our compo entry management interface), and Arkisto (our entry archive site). Most
of the comments and language used is in Finnish, because the programmers weren't interested in 
internationalization :D

This project has been originally developed for Instanssi 2012. Project is still alive and current development
focus is to provide web site for Instanssi 2016.

License
-------
MIT. Please refer to `LICENSE` for more information.

Mikä on tämä ?
--------------
En jaksa kirjoittaa suomeksi, lue ylläolevat :D

Projektin asentaminen
---------------------
1. Kloonaa tämä projekti gitillä (git clone ...). Mikäli haluat tehdä muutoksia, forkkaa ja kloonaa omasta repositoriostasi.
2. Kopioi `settings.py-dist` tiedostoksi `settings.py`. Muuta tarpeen mukaan.
3. Asenna tarvittavat kirjastot. (kts. seuraava kappale)
4. Suorita tietokantamigraatiot projektihakemistossa `python manage.py migrate`.
5. Luo pääkäyttäjä `python manage.py createsuperuser`.
6. Testaa ajamalla runserver (`python manage.py runserver`). Jos gittiin ilmestyy tietokantamallimuutoksia, saattaa
   joskus olla tarpeen suorittaa migrate uudelleen.

Kirjastot
---------

Seuraava koodirimpsu hakee kaikki tarpeelliset python-kirjastot ja dependenssit.

    pip install --upgrade -r requirements.txt
    
Huom! Windowsilla saattaa olla tarpeellista asentaa pip:n pakettien käännösvaihetta varten
[Microsoft Visual C++ Compiler for Python 2.7](https://www.microsoft.com/en-us/download/details.aspx?id=44266).

Testitapausten ajaminen
-----------------------
testing/ -hakemistossa on esimerkkejä Robot Framework - Selenium 2 -testeistä, joilla voidaan automatisoida nettisivujen klikkailua.

Testien ajamiseen tarvitset robotframework-selenium2library -palikan:

    pip install robotframework-selenium2library

Tämän jälkeen testin voi ajaa testing-hakemistossa komennolla

    pybot -d output/ testinnimi.txt

Testi tuottaa output-hakemistoon testiraportin ja kuvakaappauksen lopputilastaan.
