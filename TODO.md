# TODO

## Yleisesti

* Rosetta / i18n
* Englanninkielinen väännös ?

## Asiakkaille näkyvä osio

### Kompomaatti
* Kompomaatin asiakaspuoli pitäisi uudistaa
* Kilpailut, joissa ei tallenneta tuotoksia, mm. levykkeenheitto. Admin-paneelista voitaisiin lopuksi pisteyttää.
* Äänestysjärjestelmä voisi olla parempi... jokin viiva jota voisi siirrellä, ts. "tämän alapuolella
  olevat ovat kaikki saman arvoisia (i don't care)".
* Ei turhaan kysytä pikkukuvaa musiikkitiedostoille. Entryn lisääminen voisi olla hieman kustomoitavampi.

### main2012, main2013, ...

* Jatketaan joka vuodelle oma sivunsa, jätetään vanhat talteen
* Aikataulun jne. voisi sijoitella omiin järjestelmiinsä, jotka ladataan templatetageilla

### Arkisto

* Tehty

### openidauth

* Niputa tiukemmin kompomaattiin

## Admineille näkyvä osio

* Tablesorteriin pluggari, jotta osaa sortata aikaleimat formaatilla "dd.mm.yyyy klo. hh:ii"
* Kaikille sivuille oikeudet is_staff / has_perms -kamalla

### admin_blog

* Saisi minne tahansa näkyviin templatetagilla {% render_blog %} (pääsivulle)

### admin_calendar, admin_programme

* Saisi minne vaan näkyviin templatetagilla {% render_schedule %} (pääsivulle)

### admin_upload

* Tehty
  
### admin_slides

* Tehty

### admin_kompomaatti

* Tehty

### admin_arkisto

* Kunnollinen käyttöliittymä arkistointi-operaatioiden hallintaan.
  * mm. teosten siirto openid-käyttäjiltä arkisto-käyttäjälle.
  * vanha entryarchivaltool voisi tulla osaksi tätä.
  
### admin_screenshow

* Hakisi tietoja aikataulusta ja demokompoista, ja näyttäisi niiden tietoja screenillä satunnaisesti
* Voisi myös näyttää upload-palvelulla upattuja kuvia kun halutaan (sponsorit?)
* Ääntä, videoita ? (HTML5)

### admin_stream
* Telkkaristreamin alareunan tapahtumajutskien generointi
