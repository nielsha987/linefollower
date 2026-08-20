# Gebruiksaanwijzing LineFollow Robot

Deze pagina beschrijft hoe je de LineFollow Robot veilig gebruikt, verbindt met de applicatie, kalibreert en instelt.

---

## 1. Batterij opladen en vervangen

De robot gebruikt een LiPo HV 2S-batterij met een volledig geladen spanning van 8,7 V.

> ⚠️ GEVAAR: LiPo-batterijen kunnen zeer brandgevaarlijk zijn bij verkeerd gebruik of beschadiging.

### Belangrijke veiligheidsregels

- Gebruik enkel een geschikte LiPo-lader die door de fabrikant wordt aanbevolen.
- Laad de batterij altijd op met de balansstekker aangesloten.
- Hierdoor worden de afzonderlijke cellen correct geladen en wordt celonbalans vermeden.
- Koppel de batterij altijd fysiek los van de robot tijdens het opladen.
- Sluit nooit gelijktijdig de batterij en de USB-kabel van de computer aan op de robot.

### Robot inschakelen

De robot wordt ingeschakeld door de batterij aan te sluiten.

### Robot uitschakelen

Koppel de batterij fysiek los van de robot.

---

## 2. Draadloze communicatie

De robot communiceert via Bluetooth met de bijbehorende GUI-applicatie.

Hierdoor zijn geen handmatige seriële commando's nodig.

### Verbinding maken

1. Zorg dat de robot is ingeschakeld en de batterij aangesloten is.
2. Open de applicatie.
3. Ga naar de Connectie Tab.
4. Druk op Verbinden.
5. Wanneer de verbinding gelukt is, geeft de applicatie de status Verbonden weer.

### Verbinding verbreken

De Bluetoothverbinding kan op verschillende manieren worden verbroken:

- Druk in de applicatie op Verbreken.
- Sluit de applicatie.
- Koppel de batterij los van de robot.

---

## 3. Applicatie

De applicatie bestaat uit vier tabs.

### 3.1 Connectie Tab

De Connectie Tab wordt gebruikt om de Bluetoothverbinding met de robot te beheren.

Beschikbare functies:

- Verbinden
- Verbreken
- Weergave van de huidige verbindingsstatus

---

### 3.2 Sensoren Tab

De Sensoren Tab toont de live waarden van de lijnsensoren.

De sensorwaarden worden weergegeven in de vorm van een balkgrafiek.

Hierdoor kan eenvoudig gecontroleerd worden:

- welke sensoren wit detecteren;
- welke sensoren zwart detecteren;
- of alle sensoren correct functioneren;
- of de kalibratie correct is uitgevoerd.

Vanuit deze tab kan ook de kalibratie van wit en zwart worden uitgevoerd.

---

### 3.3 Settings Tab

De Settings Tab wordt gebruikt om de robot te starten, stoppen en configureren.

#### Start

Met Start wordt de automatische lijnvolgroutine gestart.

De robot gebruikt hierbij de PID-regeling om de zwarte lijn te volgen.

#### Stop

Met Stop wordt de robot onmiddellijk gestopt en wordt de PID-regeling uitgeschakeld.

#### Parameters

| Parameter | Functie |
|---|---|
| Basis Snelheid | Basissnelheid van de robot, tussen 0 en 255 |
| Kp | Proportionele parameter van de PID-regelaar |
| Ki | Integrerende parameter van de PID-regelaar |
| Kd | Differentiërende parameter van de PID-regelaar |
| Minimaal contrast | Minimaal verschil tussen zwart en wit voordat de robot de lijn als verloren beschouwt |
| Laagdoorlaatfilter | Filter op de berekende positie van de lijn |

#### Testmodus – ZQSD

De robot kan vanuit de Settings Tab ook manueel worden bestuurd met de ZQSD-toetsen.

Hiermee kunnen de motoren afzonderlijk getest en bediend worden.

De testmodus is onder andere handig om:

- de motoren te controleren;
- de draairichting te controleren;
- de robot handmatig te verplaatsen;
- de robot na lijnverlies opnieuw op de lijn te plaatsen.

> Belangrijk: manuele besturing is enkel mogelijk wanneer de gebruiker zich in de Settings Tab bevindt.

---

### 3.4 Plot Tab

De Plot Tab wordt gebruikt om de prestaties van de robot na een run te analyseren.

Hier kunnen de geregistreerde gegevens van een uitgevoerde run bekeken worden.

De grafieken kunnen gebruikt worden om het gedrag van de robot en de PID-regeling te beoordelen.

---

## 4. Kalibratie

Kalibratie is het proces waarbij de sensorwaarden softwarematig worden genormaliseerd.

Het doel hiervan is:

- een zo groot mogelijk onderscheid te verkrijgen tussen wit en zwart;
- verschillen tussen de individuele sensoren te compenseren;
- een betrouwbare lijnpositie te kunnen berekenen.

> ⚠️ Belangrijk: voer de kalibratie uit op hetzelfde witte en zwarte materiaal dat ook tijdens de uiteindelijke run gebruikt wordt.

### 4.1 Verbinding maken

1. Schakel de robot in.
2. Open de applicatie.
3. Ga naar de Connectie Tab.
4. Verbind met de robot.
5. Ga daarna naar de Sensoren Tab.

### 4.2 Kalibratie WIT

1. Plaats de robot zodat alle sensoren boven de witte achtergrond van het parcours staan.
2. Controleer in de Sensoren Tab of de sensorbalken een lage waarde weergeven.
3. Druk op Kalibreer WIT.

De gemeten waarden worden gebruikt als referentiewaarden voor wit.

### 4.3 Kalibratie ZWART

1. Plaats de robot zodat de sensoren boven de zwarte lijn staan.
2. Controleer in de Sensoren Tab of de sensorbalken een hoge waarde weergeven.
3. Druk op Kalibreer ZWART.

De gemeten waarden worden gebruikt als referentiewaarden voor zwart.

---

## 5. Aanbevolen instellingen

De robot rijdt stabiel met volgende parameters:

| Parameter | Waarde |
|---|---:|
| Kp | 7 |
| Ki | 0 |
| Kd | 0 |
| Speed | 140 |

Speed 140 is de basissnelheid van de robot.

Deze waarden kunnen verder worden aangepast afhankelijk van het parcours en het gewenste rijgedrag.
