#  GUI Applicatie

Dit project is een Python-applicatie met een GUI gebouwd met PyQt6 en is gericht op het besturen van de linefollower en dataanalyse van gereden runs


## Installatie

Volg deze stappen om het project lokaal op uw computer in te stellen en uit te voeren.

### 1. Project Klonen

Open uw commandoregel en download de code van GitHub:

```bash
git clone https://github.com/nielsha987/linefollower
cd code/GUI
```
### 2. Virtuele Omgeving Instellen (niet verplicht maar aanbevolen)

#### Maak een virtuele omgeving om ervoor te zorgen dat u systeem niet vervuilt en om conflicten te vermijden 
Creëer de omgeving:
  ```bash
  python -m venv venv
  ```
Activeer de omgeving:
  ```bash
  .\venv\Scripts\Activate
  ```
### 3. Dependencies Installeren

#### Installeer alle benodigde pakketten die in het requirements.txt bestand zijn gespecificeerd:

 ```bash
pip install -r req.txt
 ```
  Dit installeert alle vereisten, inclusief de GUI-bibliotheek (PyQt6), plotting tools (matplotlib), en seriële communicatie (pyserial).
#### De Applicatie Uitvoeren

Zodra de virtuele omgeving actief is en de installatie is voltooid, start u de applicatie met dit commando:

 ```bash
python main.py
 ```
De grafische gebruikersinterface zou nu moeten verschijnen.

### NOTE : Belangrijke Map- en Bestandsstructuur
  De applicatie is ontworpen om bepaalde bestanden en mappen automatisch aan te maken in de map waar u python main.py uitvoert.
#### 1. CSV-bestanden
      Wanneer: Als u in de GUI op de knop "Maak CSV" drukt.
     
      Locatie: Er wordt een nieuwe submap gemaakt genaamd csv_files (als deze nog niet bestaat).
     
      Doel: Alle geëxporteerde gegevens worden in deze map opgeslagen.

#### 3. Lokale Database
      Actie: De database wordt automatisch gecreëerd bij de eerste keer opstarten of wanneer een database-actie vereist is.
      
      Locatie: Het databasebestand (robot_data.db) wordt direct in de hoofdmap van de applicatie aangemaakt (naast main.py).
