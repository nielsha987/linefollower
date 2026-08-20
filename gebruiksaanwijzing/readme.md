# Gebruiksaanwijzing

### opladen / vervangen batterijen
De robot gebruikt een LiPo HV 2S batterij met een volledige spanning van 8.7 V. Dit type batterij vereist uiterste voorzichtigheid.
GEVAAR! LiPo-batterijen zijn zeer brandgevaarlijk bij onjuist gebruik of beschadiging.

Gebruik enkel de juiste, door de fabrikant gespecificeerde LiPo-lader.
Laad de batterij altijd op met de individuele cel-balansdraad aangesloten om overladen en celonbalans te voorkomen.
Zorg dat de batterij fysiek is losgekoppeld van de robot tijdens het opladen.
De robot en de USB poort van uw computer kan niet tegelijk de USB en de batterij aan doe dit nooit!

### draadloze communicatie
#### verbinding maken
De robot communiceert via Bluetooth met de GUI, waardoor er geen handmatige commando's nodig zijn. Verbinding Maken / Verbreken Actie Procedure Verbinden

Zorg dat de robot is ingeschakeld (batterij aangesloten).
Open de app en ga naar de Connectie Tab.
Druk op de knop Verbinden. De app zal de status 'Verbonden' weergeven.
Verbreken De verbinding wordt verbroken door:

In de app op Verbreken te drukken.
De applicatie te sluiten.
De batterij fysiek uit de robot te halen.

De Vier Applicatie Tabs

1.Connectie Tab
Toont de huidige verbindingsstatus en bevat de knoppen Verbinden en Verbreken. 
2. Sensoren Tab
Deze tab geeft de live data van de lijnsensoren weer via een visualisatie in de vorm van een balkgrafiek.
3. settings tab
Deze tab is bedoeld voor het configureren van de robotparameters.
  Start: Start de automatische lijnvolgroutine (PID-controle).
  Stop: Stopt de robot onmiddellijk en schakelt de PID-lus uit.
  Parameters: 
  de Basis Snelheid (0-255), 
  
  de PID-parameters (Kp, Ki, Kd) 
  
  het minimaal contrast tussen zwart en wit wanneer de robot uitvalt en
  
  de loogdaarlaatfilter op de position.
  
  Testmodus (ZQSD): Dit biedt de mogelijkheid om de motoren manueel te testen en besturen met de ZQSD-toetsen (of vergelijkbare controls).

  Belangrijk: Manuele besturing is alleen mogelijk wanneer u in deze tab bent. Dit is handig om de robot na lijnverlies snel en handmatig terug op de lijn te plaatsen.
5. plot tab
Deze tab dient voor het analyseren van de prestaties na een run.


### kalibratie
Kalibratie is het proces waarbij de sensorwaarden softwarematig worden genormaliseerd. Dit zorgt ervoor dat de robot de maximale contrastinformatie tussen de witte ondergrond en de zwarte lijn benut, en maakt de sensoren onderling gelijk. Stappenplan

Installeer de App: Ga naar de Connectie Tab en verbind met de robot.

Kalibratie WIT (Minimale Waarden):

    Plaatsing: Plaats de robot op de witte achtergrond van het parcours dat u gaat gebruiken.

    Controle: Ga naar de Sensoren Tab en controleer of alle sensorbalken een lage waarde (bijna allemaal 'wit') aangeven.

    Uitvoeren: Druk op de knop Kalibreer WIT.

Kalibratie ZWART (Maximale Waarden):

    Plaatsing: Plaats de robot met de sensoren direct op de zwarte lijn van het parcours.

    Controle: Ga naar de Sensoren Tab en controleer of alle sensorbalken een hoge waarde (bijna allemaal 'zwart') aangeven.

    Uitvoeren: Druk op de knop Kalibreer ZWART.
Let op: Het is cruciaal dat u deze stappen uitvoert op de exacte materialen (wit/zwart) die u tijdens de run zult gebruiken.
Aanbevolen Parameters

De robot rijdt stabiel met de volgende parameters:

Kp 7

Ki 0

Kd 0

Speed 140 De basissnelheid van de robot.
