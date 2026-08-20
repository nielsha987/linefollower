# Instructable


### stap 1 Componenten Bestellen en 3D-printen
bestel alle componenten uit de bill of materials
3D-print de mechanische componenten die beschreven staan in de map

### stap 2 header pins op het soldeer board solderen
Soldeer de header pins aan alle componenten

### stap 3 voorbereiden van de print
1. Soldeer de vrouwelijke headerpinnen op de perforatieprint. Laat voldoende ruimte voor het 3D-geprinte frame.
2. Soldeer de voedingskabel voor de batterij op de + en - aansluiting van de print.
3. Soldeer een condensator van 1000 µF parallel over de batterijvoeding.
4. Soldeer kleine condensatoren over beide motoren om storingen en spanningspieken te beperken.
5. Soldeer draden aan de motoren en leid deze via het voorziene poortje naar de printplaat.
6. Maak aan de onderzijde van de print de nodige verbindingen tussen de ESP32, motor driver en buck converter.

### stap 4 montage van de printplaat aan het frame
Plaats het perforatieprintje (met de motoren) onder het 3D-geprinte frame.

Lijn de gaten uit.

Schroef het geheel aan elkaar met de bouten en moeren.

### stap 5 Montage van de Line Follower Sensor
laats de 8-channel Line Follow sensor in de voorziene opening aan de voorkant van het frame.

plaats de batterijhouder juist

Schroef deze vast met de bijbehorende bouten en moeren.

### stap 6 Plaatsen van de Hoofdcomponenten
Plaats de extender female pinnen op de reeds gesoldeerde female pinnen van het perforatieprintje.

Plaats de ESP-32 op de extender pinnen. Zorg dat de ESP correct is georiënteerd.

Plaats de Motor Driver (rood) en de Buck Converter (blauw) op de daarvoor bestemde plekken op de printplaat.

### stap 7 Aansluiten van de Sensoren
Neem Dupont draadjes en steek die in de overgebleven open female headers

Maak de verbinding tussen deze headers en de pinnen van de 8-channel Line Follow sensor volgens het schema.

### stap 8 Finaliseren en Klaar voor Software

Bevestig de wielen op de motorassen.

Sluit de batterij aan op de XT30-connector.

De robot is nu mechanisch en elektrisch geassembleerd.

### Stap 9 Voorbereiding en installatie van de code

1. Zorg dat Arduino IDE geïnstalleerd is en dat de ESP32 Board Support Package  is toegevoegd.
2. Ga naar de map `code/finaal/` en download alle bestanden uit deze map.
3. Plaats alle bestanden samen in één map op uw computer. De mapnaam moet overeenkomen met de naam van het `.ino`-bestand.
4. Open het `.ino`-bestand in Arduino IDE.


### Stap 10: Compileren en uploaden naar de ESP32

1. Verbind de ESP32 met de computer via USB.
2. Selecteer in Arduino IDE het juiste board, bijvoorbeeld `ESP32 Dev Module`.
3. Selecteer de juiste seriële poort.
4. Klik op Uploaden om de code naar de ESP32 te sturen.


### Stap 11: Veiligheidswaarschuwingen

- Sluit nooit tegelijk de batterij en de USB-kabel aan op de robot.
- Gebruik de USB-aansluiting enkel voor programmeren.
- Voed de motoren altijd via de externe batterij en de motor driver.

### Stap 12: Installatie van de GUI

Volg het stappenplan in `code/GUI/readme.md` om de bijbehorende gebruikersinterface op de computer te installeren.
