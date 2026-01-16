[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ltgmuiIo)
# Werkplaats 2 - Accessibility hub

Bij inlevering moet hier het volgende staan:
- Installatie instructies
- Opstart instructies
- Inloggegevens van gebruikers
- Screenshots
- Andere dingen die je wilt melden of belangrijk zijn (bonus functionaliteiten bijvoorbeeld)
- APA bronnen


## Installatie en starten van programma
Het installeer van alle dependencies is platform specefiek, voer uit welke platform voor jou is

#### 1. Git Clone
```bash
git clone https://github.com/Rac-Software-Development/wp2-2025-mvc-1b1-codingenterprice.git
```

#### 2. verplaatsen naar map
```bash
cd wp2-2025-mvc-1b1-codingenterprice
```
#### 3. Installeren
```bash
pip install -r requirements.txt
```
#### 4. Environment
1. Dupliceer .env.example en maar er .env van
2. Vul de volgende waardes in voor een locale email test:
```env
smtp_host=
smtp_port=
```
Let Op:
Er wordt vanuit gegaan dat er een locale smtp sever draait zoals bijvoorbeeld: smtp4dev
Een manier om dit te draaien is via docker. gebruik dan het volgende commando in de terminal:
```bash
docker run -p 4999:80 -p 2525:25 -p 110:110 rnwood/smtp4dev
```
Voor meer informatie zie: https://github.com/rnwood/smtp4dev

Bij gebruik van dit command zal de .env er alvolgt uit moeten zien:
```env
smtp_host=127.0.0.1
smtp_port=2525
```

#### 5a. Starten van spel met terminal
vanuit de root van je git folder in je terminal voer het volgende uit:
```bash
python src/app.py
```

#### 5b. Starten van programma met pycharm
1. open de folder in pycharm
2. navigeer naar src/app.py
3. klik de play button in pycharm en de app start up
<img width="1898" height="795" alt="icture1" src="https://github.com/user-attachments/assets/1d79446e-22b6-4519-b4d3-f272afc350a4" />
