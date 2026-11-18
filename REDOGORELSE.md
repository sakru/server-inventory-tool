# Redogörelse

## Bakgrund: min server och testmiljö

MindverkSR är min egen server och testmiljö. Där använder jag Mindverk Monitor för att följa systemresurser, lagring, tjänster och nätverk. Monitor samlar in uppgifterna och skriver dem till `status.json`. En separat del läser filen och visar en översikt i terminalen. Vid sparandet skrivs först en tillfällig fil, som sedan ersätter den gamla.

I skoluppgiften behövs en serverlista, ping och rapporter. Delarna hålls isär även här: `kontroller.py` sköter ping, `lagring.py` sköter filer och `main.py` sköter meny och kommandon. `spara_servrar()` i `lagring.py` skriver också en tillfällig fil. Den befintliga datafilen ersätts först när den nya är färdigskriven.

## 1. Villkor, loop och funktion

I `main.py` finns funktionen `hitta_server()`:

```python
def hitta_server(servrar, namn):
    for server in servrar:
        if server["namn"] == namn:
            return server
    return None
```

`def` definierar funktionen. Den får två parametrar: listan `servrar` och namnet `namn` som ska sökas.

`for` går igenom en server i taget. `if` jämför serverns namn med det sökta namnet. `==` är en jämförelse. Kolon och indrag visar vilka rader som hör till funktionen, loopen och villkoret.

När namnet stämmer returneras hela serverns dictionary och funktionen avslutas. Om ingen server hittas körs `return None` efter loopen. Den kod som anropar funktionen kan sedan använda resultatet, till exempel för att visa eller ta bort servern.

## 2. Lista och dictionaries

Varje server är en dictionary med namngivna fält. Med `server["adress"]` går det till exempel att hämta adressen utan att hålla reda på ett positionsnummer. Alla servrar ligger i en lista, så de kan gås igenom i en loop eller läggas till och tas bort.

I `main.py`, `starta_meny()`, skapas `ny_server` som en dictionary och läggs till med `servrar.append(ny_server)`. Alla sex fält har strängvärden. Även adressen och kontrolltiden är strängar. Före första kontrollen är tiden en tom sträng. Att fälten innehåller strängar kontrolleras i `lagring.py`, `validera_servrar()`.

## 3. JSON och CSV

JSON kan spara listan och dess dictionaries i samma struktur som används i programmet. I `lagring.py` skriver `spara_servrar()` uppgifterna med `json.dump()`. `las_servrar()` läser tillbaka dem med `json.load()`.

I CSV blir varje server en rad med samma kolumner, vilket passar en rapport som ska öppnas i ett kalkylprogram. `exportera_csv()` i `lagring.py` skriver rubrikerna och raderna. Programmet läser sin inventering från JSON. CSV är en separat rapport över läget vid exporten.

## 4. Uppdelning av programmet

- I `main.py` läser `main()` argument och väljer vad som ska köras. `starta_meny()` tar hand om användarens menyval. Här finns också sökning, tabellutskrift och självtesterna i `kora_tester()`.
- I `lagring.py` finns `las_servrar()`, `spara_servrar()` och `validera_servrar()`. Filen sköter också rapporterna genom `exportera_csv()` och `exportera_sammanfattning()`.
- I `kontroller.py` kör `kontrollera_server()` ping och uppdaterar status och kontrolltid.

Menyn och kommandoraden använder samma funktioner. Till exempel anropar båda `kontrollera_och_spara()` i `main.py`. Pingkontrollen behöver därför inte skrivas på två ställen.

## 5. Standardbiblioteket

- `json` och `csv` används i `lagring.py` för datafilen och CSV-rapporten, i bland annat `las_servrar()` och `exportera_csv()`.
- `pathlib.Path` används för sökvägar och filer, till exempel i `hamta_datafil()` i `main.py` och `spara_servrar()` i `lagring.py`.
- `datetime` ger kontrolltiden i `kontroller.py`, `kontrollera_server()`, och datumet i rapportnamnet i `lagring.py`, `exportera_csv()`.
- `subprocess` startar systemkommandot ping i `kontroller.py`, `kontrollera_server()`.
- `os` läser miljövariabeln i `main.py`, `hamta_datafil()`. `argparse` läser kommandona i `main()`. `sys.exit(main())` lämnar programmets exitkod till terminalen.
- I `main.py`, `kora_tester()`, används `tempfile` för tillfälliga filer och `unittest.mock` för simulerade svar. `io` och `contextlib` används för att fånga utskrifter och kontrollera vad programmet visar.

## 6. Tre exempel på god praxis

Menyn och kommandoraden anropar båda `kontrollera_och_spara()` i `main.py`. Därför räcker det att ändra på ett ställe om sättet att kontrollera och spara ska ändras.

`validera_servrar()` i `lagring.py` kontrollerar uppgifterna före användning och sparande. Saknade fält, fel miljö eller dubbla namn ger ett felmeddelande. Det behövs också när någon har ändrat JSON-filen för hand.

`spara_servrar()` i `lagring.py` skriver till en tillfällig fil innan datafilen byts ut. Om skrivningen misslyckas före bytet finns den tidigare filen kvar. Det minskar risken att förlora sparade uppgifter när en skrivning avbryts.

## 7. Källor och hjälpmedel

[Uppgiftsbeskrivningen](https://gist.github.com/jonasbjork/b402dfb3db4b2c63d3e0333fecce3212) användes för kraven på fält, meny, kommandon och dokumentation. Exempel är serverfälten i `lagring.py`, `validera_servrar()`, och argumenten i `main.py`, `main()`.

Pythons dokumentation användes för [JSON](https://docs.python.org/3/library/json.html), [CSV](https://docs.python.org/3/library/csv.html), [subprocess](https://docs.python.org/3/library/subprocess.html) och [argparse](https://docs.python.org/3/library/argparse.html). Det hör bland annat till `spara_servrar()` och `exportera_csv()` i `lagring.py`, `kontrollera_server()` i `kontroller.py` och `main()` i `main.py`.

AI har varit ett stöd i arbetet, bland annat vid planering av programmets struktur och för att hitta fel. Ett exempel är felkontrollerna i `main.py`, `kora_tester()`.

Mindverk Monitor har använts som jämförelse för uppdelningen mellan insamling, lagring och visning, samt för filbytet i `lagring.py`, `spara_servrar()`.
