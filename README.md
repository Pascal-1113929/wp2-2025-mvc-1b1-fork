[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ltgmuiIo)
# Werkplaats 2 - Accessibility hub

Bij inlevering moet hier het volgende staan:
- Installatie instructies
- Opstart instructies
- Inloggegevens van gebruikers
- Screenshots
- Andere dingen die je wilt melden of belangrijk zijn (bonus functionaliteiten bijvoorbeeld)
- APA bronnen


## Installatie en starten van game
Het installeer van alle dependencies is platform specefiek, voer uit welke platform voor jou is

#### 1. Git Clone
```bash
git clone https://github.com/Rac-Software-Development/wp1-2025-pygame-1b1-codingenterprice.git
```

#### 2. Git Clone
```bash
cd wp1-2025-pygame-1b1-codingenterprice
```

#### 3a. Installeren (Windows)
```bash
pip install -r requirements_windows.txt
```

#### 3b. Installeren (Linux/MacOS)
```bash
pip install -r requirements_unix.txt
```
#### 4. Starten van smtp4dev client voor email (docker nodig)
Voer uit in terminal:
```bash
docker run -p 4999:80 -p 2525:25 -p 110:110 rnwood/smtp4dev
```
smtp4dev web ui: http://127.0.0.1:4999/
smtp4dev smtp port: 2525

#### 5a. Starten van spel met terminal
vanuit de root van je git folder in je terminal voer het volgende uit:
```bash
python src/app.py
```

#### 4b. Starten van spel met pycharm
1. open de folder in pycharm
2. navigeer naar  src/app.py
3. klik de play button in pycharm en de app start up
<img width="1898" height="795" alt="icture1" src="https://github.com/user-attachments/assets/1d79446e-22b6-4519-b4d3-f272afc350a4" />
