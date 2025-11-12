# Werkplekopdracht – Accessibility Hub

## Doel van de opdracht

Je bouwt een webapplicatie voor **Stichting Accessibility**. Deze webapplicatie verbindt een groep van ongeveer 125 ervaringsdeskundigen met organisaties die **toegankelijkheidsonderzoek** willen doen. De stichting beheert de gegevens en keurt nieuwe registraties en inschrijvingen goed. Deze taak wordt op dit moment met Excel-sheets gedaan en Stichting Accessibility wil dit graag automatiseren.

De webapplicatie is gemaakt met **Flask**, **Jinja2**, **HTML**, **CSS** en **SQL**.
Alle schermen worden op de server opgebouwd (server-side rendering). Formulieren werken met **GET/POST** en het **POST/Redirect/GET**-patroon.

---

## Rollen
Er zijn 3 verschillende rollen in de webapplicatie:

* **Ervaringsdeskundige**: De ervaringsdeskundige is een vrijwilliger van de stichting. Hij/zij heeft een beperking en wil helpen met het onderzoeken van toegankelijkheid. De ervaringsdeskundige kan een profiel aanmaken (registreren), zoekt passende onderzoeken en kan zich inschrijven voor onderzoeken.

* **Beheerder**: De beheerder is iemand van Stichting Accessibility. Hij/zij controleert of nieuwe registraties, onderzoeken en inschrijvingen compleet zijn. De beheerder kan deze vervolgens goedkeuren of afkeuren en kan ook nieuwe accounts aanmaken voor organisaties.

* **Organisatie**: Zodra de organisatie inloggegevens heeft gekregen van een beheerder, kan ze nieuwe onderzoeken indienen. Daarna kan de organisatie zien hoeveel ervaringsdeskundigen zich hebben ingeschreven voor haar onderzoeken. Denk hierbij aan organisaties als Albert Heijn, VGZ of Bol.com.

---

## Hoofdproces

1. **Registratie nieuwe ervaringsdeskundige**
   De ervaringsdeskundige vult zijn/haar profiel in, inclusief beperkingen, voorkeuren en eventueel een toezichthouder.
2. **Beoordeling door beheerder**
   De beheerder beoordeelt de registratie en keurt deze goed of af. Goed- of afkeuren kan via het beheerdersportaal.
3. **Inloggen**
   Na goedkeuring kan de ervaringsdeskundige inloggen.
4. **Dashboard**
   De ervaringsdeskundige ziet zijn/haar profiel en kan zich inschrijven voor onderzoeken die passen bij zijn/haar beperking en/of voorkeuren.
6. **Detailpagina**
   De ervaringsdeskundige kan details bekijken van onderzoeken en zich hier vervolgens voor inschrijven.
7. **Beheerder keurt deze inschrijving**
   Vervolgens kan de beheerder via het beheerderspagina de inschrijving inzien en goed- of afkeuren.

### Organisatieproces

1. **De beheerder maakt een organisatieaccount aan**
   Hierna kan de organisatie met aangeleverde inloggegevens van Stichting Accessibility inloggen.
2. **Nieuwe onderzoeken aanmaken**
   De organisatie kan nieuwe onderzoeken aanmaken aan de hand van een formulier.
3. **Beoordeling door beheerder**
   De beheerder beoordeelt de onderzoeken en keurt deze goed of af. Goed- of afkeuren kan via het beheerdersportaal.
4. **Overzicht van inschrijvingen**
   De organisatie ziet een overzicht van inschrijvingen.

![img.png](attachments/img.png)

---

## Schermen en functies

### Algemeen

* **Overbrengen van data** met Jinja2-templates.
* **Validatie**: bij fouten komt dezelfde pagina terug met duidelijke foutmeldingen per veld.
* **Toegankelijk**: WCAG 2.1 AA.
* **Zoeken en filteren** via **GET-parameters**.
* **Paginatie** voor lijsten.

### Registratie
Bij het registreren is het belangrijk dat de ervaringsdeskundige aangeeft welke beperkingen hij/zij heeft en wat de voorkeur is qua onderzoeken. Elke stap is een eigen pagina:

1. **Persoonsgegevens**
2. **Beperkingen en voorkeuren**
3. **Toezichthouder** (alleen als dit nodig is, bijvoorbeeld bij minderjarigen)
4. **Bevestigen en voorwaarden**

### Portal ervaringsdeskundigen

* Na goedkeuring van de beheerder kan de ervaringsdeskundige inloggen.
* Na inloggen kan de ervaringsdeskundige een **Dashboard** bekijken met:

    * het profiel bekijken en bijwerken;
    * een overzicht zien van **passende onderzoeken** (gefilterd op profiel en status);
    * een **detailpagina** openen en zich **inschrijven** via een formulier;
    * een lijst zien met eigen inschrijvingen per status: **In beoordeling**, **Goedgekeurd**, **Afgekeurd**.

### Portal beheerders

* **Dashboard** met:

    * nieuwe registraties;
    * onderzoeken in beoordeling;
    * nieuwe inschrijvingen bij onderzoeken.

* Acties: **goedkeuren** of **afkeuren** (via POST).
* **Lijsten** met zoeken en paginatie voor ervaringsdeskundigen, organisaties, onderzoeken en inschrijvingen.
* Beheerder kan organisaties toevoegen.

### Portal organisaties

* Inloggen met een account (door beheerder aangemaakt).
* Onderzoeken aanmaken en bewerken (titel, data, omschrijving, beloning, status).
* Overzicht van inschrijvingen met goedgekeurde deelnemers.

---

## Statussen

We slaan de volgende statussen op in de database:

* **Ervaringsdeskundigen**: `nieuw` → `goedgekeurd`
* **Onderzoek**: `nieuw` → `goedgekeurd` → `afgekeurd` → `gesloten`
* **Inschrijving**: `nieuw` → `goedgekeurd` → `afgekeurd`

---

## Techniek

### Backend

* **Flask is verplicht** voor routes, templates en sessies.
* **Jinja2 is verplicht** voor het overbrengen van data van backend naar frontend.
* **Structuur volgens MVC**:

    * **Model**: SQLite-tabellen en SQL-query’s in een apart Python-bestand, bijvoorbeeld `database.py`.
    * **View**: Jinja2-templates in een map `templates/`.
    * **Controller**: routes in `app.py`.

### Database

* **SQLite is verplicht.** Je gebruikt SQL-query’s en eenvoudige migraties/seed-scripts.
* Tabellen (voorstel):
    * `users` (rol, status, inlog)
    * `profiles` (geboortedatum, beperkingen, voorkeuren, toezichthouder)
    * `organizations`
    * `studies` (onderzoeken)
    * `enrollments` (inschrijvingen)
    * `disabilities` en koppel-tabellen
* **Demo-data** voor testen en een **ERD**.

### Frontend

* **HTML is verplicht** met semantische elementen en formulieren.
* **CSS is verplicht** voor een duidelijk en rustig ontwerp.

### Bonus

* **CSV-export** van onderzoeken en inschrijvingen.
* **ICS-bestanden** voor de agenda van de organisaties.
* **E-mailmeldingen**: stuur een e-mail naar het contactadres van organisaties en ervaringsdeskundigen wanneer een **registratie**, **onderzoek** of **inschrijving** wordt **goedgekeurd** of **afgekeurd**. Gebruik `smtplib` om e-mails te versturen en gebruik bijvoorbeeld **Mailpit** of **smtp4dev** om deze lokaal op te vangen en te testen (zonder echte mails). E-mails mogen eenvoudig zijn en mogen vanuit een tekst- of HTML-template worden opgebouwd.

---

## Toegankelijkheid (WCAG 2.1 AA)

Omdat deze opdracht voor Stichting Accessibility is, is het belangrijk dat de applicatie toegankelijk is.

* **Duidelijk contrast** en **schaalbare tekst** (rem/em).
* **Toetsenbordvriendelijk**: logische tabvolgorde, skip-links, zichtbare focus.
* **Formulieren**: labels gekoppeld, foutmelding met duidelijke tekst.
* **Alt-tekst**: afbeeldingen hebben een duidelijke beschrijving.
* **Voorwaarden** als PDF met een goede linktekst.

---

## Gegevensmodellen (overzicht)

### Profiel ervaringsdeskundige

| Veld                    | Type                | Opmerking                                      |
| ----------------------- | ------------------- | ---------------------------------------------- |
| Voornaam                | String              |                                                |
| Achternaam              | String              |                                                |
| Postcode                | String              |                                                |
| Geslacht                | String              |                                                |
| E-mail                  | String              |                                                |
| Telefoon                | String              |                                                |
| Geboortedatum           | Date                | **Filterveld**                                 |
| Type beperking          | Verwijzing/meervoud | **Filterveld**                                 |
| Hulpmiddelen            | Tekst               |                                                |
| Korte intro             | Tekst               |                                                |
| Bijzonderheden          | Tekst               |                                                |
| Akkoord voorwaarden     | Boolean             |                                                |
| Toezichthouder          | Boolean             |                                                |
| Naam toezichthouder     | String              | Indien van toepassing                          |
| E-mail toezichthouder   | String              | Indien van toepassing                          |
| Telefoon toezichthouder | String              | Indien van toepassing                          |
| Voorkeur contact        | Keuze               | Telefoon of e-mail                             |
| Type onderzoek          | Keuze               | Telefonisch, online of op locatie (**filter**) |
| Beschikbaarheid         | Tekst               |                                                |

### Onderzoek

| Veld                   | Type       | Opmerking                                       |
| ---------------------- | ---------- | ----------------------------------------------- |
| Titel                  | String     |                                                 |
| Status                 | Keuze      | `nieuw`, `goedgekeurd`, `afgekeurd`, `gesloten` |
| Beschikbaar            | Boolean    | Kan men zich nog inschrijven?                   |
| Beschrijving           | Tekst      |                                                 |
| Datum vanaf            | Date       |                                                 |
| Datum tot              | Date       |                                                 |
| Type onderzoek         | Keuze      | Telefonisch, online, op locatie (**filter**)    |
| Locatie                | String     | Bij onderzoek op locatie                        |
| Met beloning           | Boolean    |                                                 |
| Beloning               | Tekst      | Indien van toepassing                           |
| Doelgroep leeftijd van | Number     | **Filterveld**                                  |
| Doelgroep leeftijd tot | Number     | **Filterveld**                                  |
| Doelgroep beperking    | Verwijzing | **Filterveld**                                  |

### Organisatie

| Veld            | Type   | Opmerking                 |
| --------------- | ------ | ------------------------- |
| Naam            | String |                           |
| Type            | Keuze  | Commercieel of non-profit |
| Website         | String |                           |
| Beschrijving    | String |                           |
| Contactpersoon  | String |                           |
| E-mail          | String |                           |
| Telefoon        | String |                           |
| Overige details | Tekst  |                           |

### Lijst met beperkingen

**Auditief**: Doof, Slechthorend, Doofblind
**Visueel**: Blind, Slechtziend, Kleurenblind, Doofblind
**Motorisch/lichamelijk**: Amputatie en mismaaktheid, Artritis, Fibromyalgie, Reuma, Verminderde handvaardigheid, Spierdystrofie, RSI, Tremor en Spasmen, Quadriplegie/tetraplegie
**Cognitief/neurologisch**: ADHD, Autisme, Dyslexie, Dyscalculie, Leerstoornis, Geheugenbeperking, Multiple Sclerose, Epilepsie, Migraine

---

## Inleveren

* Broncode (Flask + Jinja2 + SQL + CSS) met **installatie-instructies en opstart-instructies in de README.md** via Brightspace (link + ZIP van Git tqg).
* **ERD** en **demo-data** (dump of seed-scripts).
* **Schermafbeeldingen** van de belangrijkste flows.

---

## Acceptatiecriteria (kort)

* Het hoofdproces werkt.
* Het organisatieproces werkt.
* Voldoet aan **WCAG 2.1 AA**.
* **ERD** en **demo-data** aanwezig.
