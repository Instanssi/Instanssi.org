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

### /blog-admin/

* Ajastettu julkaisu ?
* Saisi minne tahansa näkyviin templatetagilla {% render_blog %} (pääsivulle)

### /schedule-admin/

* Aikataulunhallinta. Kalenteriin tapahtumien lisääminen/poisto/muokkaus.
* Esim. Kompot, esitelmät, jne.
* Tapahtumiin voisi linkata kompoja, jolloin tarkemmat tiedot haettaisiin kompomaatista.
* Saisi minne vaan näkyviin templatetagilla {% render_schedule %} (pääsivulle)

### /upload/

* Tehty
  
### /diashow-admin/

* Tehty

### /kompomaatti-admin/

* Tehty

### /arkisto-admin/

* Kunnollinen käyttöliittymä arkistointi-operaatioiden hallintaan.
  * mm. teosten siirto openid-käyttäjiltä arkisto-käyttäjälle.
  * vanha entryarchivaltool voisi tulla osaksi tätä.
  
### /screenshow-admin/

* Hakisi tietoja aikataulusta ja demokompoista, ja näyttäisi niiden tietoja screenillä satunnaisesti
* Voisi myös näyttää upload-palvelulla upattuja kuvia kun halutaan (sponsorit?)
* Ääntä, videoita ? (HTML5)

### /tv-stuff/
* Telkkaristreamin alareunan tapahtumajutskien generointi
