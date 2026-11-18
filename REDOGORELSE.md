# Redogörelse

Utkast för genomgång före inlämning.

## Bakgrund: Mindverk Monitor

Mindverk Monitor är ett exempel från arbetet med en större övervakningslösning. En del samlar in uppgifter om bland annat systemresurser, lagring, tjänster och nätverk. Resultatet skrivs till `status.json`. En annan del läser filen och visar en översikt i terminalen. Insamlingen skriver först till en tillfällig fil och ersätter sedan den gamla filen.

Skoluppgiften har ett mindre mål: att hålla en serverlista, kontrollera adresser och exportera rapporter. Samma uppdelning är användbar här. `kontroller.py` sköter ping, `lagring.py` sköter filer och `main.py` sköter meny och kommandon. I `lagring.py`, `spara_servrar()`, används också en tillfällig fil före bytet. Det gör att en befintlig datafil inte ersätts förrän den nya filen är färdigskriven.

## 1. Villkor, loop och funktion

I `main.py` finns funktionen `hitta_server()`:

```python
def hitta_server(servrar, namn):
    for server in servrar:
        if server["namn"] == namn:
            return server
    return None
```

`def` skapar funktionen. Parametern `servrar` tar emot listan som ska sökas igenom och `namn` tar emot namnet som söks.

`for` går igenom en server i taget. `if` jämför serverns namn med det sökta namnet. `==` är en jämförelse. Kolon och indrag visar vilka rader som hör till funktionen, loopen och villkoret.

När namnet stämmer lämnar `return server` tillbaka serverns dictionary och avslutar funktionen. Om loopen tar slut utan träff körs `return None`. Funktionen returnerar alltså ett resultat till den som anropar den; den skriver inte ut resultatet själv.

## 2. Lista och dictionaries

En dictionary håller ihop uppgifterna om en server. Nycklar som `namn` och `adress` gör det tydligt vilket värde som används. Listan samlar alla servrar och gör det enkelt att gå igenom dem, lägga till en server eller ta bort en.

I `main.py`, `starta_meny()`, skapas `ny_server` som en dictionary och läggs till med `servrar.append(ny_server)`. Alla sex fält har strängvärden. Även adressen och kontrolltiden är strängar. Före första kontrollen är tiden en tom sträng. Att fälten innehåller strängar kontrolleras i `lagring.py`, `validera_servrar()`.

## 3. JSON och CSV

JSON passar listan med dictionaries eftersom samma struktur kan sparas och läsas tillbaka. I `lagring.py` använder `spara_servrar()` funktionen `json.dump()`, och `las_servrar()` läser tillbaka uppgifterna med `json.load()`.

CSV passar en rapport där varje server blir en rad med samma kolumner. Filen går att öppna i ett kalkylprogram. `exportera_csv()` i `lagring.py` skriver rubrikerna och serverraderna. JSON är datafilen som programmet arbetar vidare med, medan CSV är en rapport över uppgifterna vid exporten.

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

Det första är att återanvända funktioner. `kontrollera_och_spara()` i `main.py` används av både menyn och kommandoraden. En ändring i kontrollflödet gäller då för båda körsätten.

Det andra är att kontrollera data innan de används eller sparas. `validera_servrar()` i `lagring.py` upptäcker till exempel saknade fält, fel miljö och dubbla namn. Då kan programmet visa ett fel i stället för att fortsätta med felaktiga uppgifter.

Det tredje är hur filen sparas. `spara_servrar()` i `lagring.py` skriver först till en tillfällig fil och byter sedan ut datafilen. Om skrivningen misslyckas före bytet finns en tidigare datafil kvar. Det minskar risken att en avbruten skrivning förstör inventeringen.

## 7. Källor och hjälpmedel

[Uppgiftsbeskrivningen](https://gist.github.com/jonasbjork/b402dfb3db4b2c63d3e0333fecce3212) användes för kraven på fält, meny, kommandon och dokumentation. Exempel är serverfälten i `lagring.py`, `validera_servrar()`, och argumenten i `main.py`, `main()`.

Pythons dokumentation användes för [JSON](https://docs.python.org/3/library/json.html), [CSV](https://docs.python.org/3/library/csv.html), [subprocess](https://docs.python.org/3/library/subprocess.html) och [argparse](https://docs.python.org/3/library/argparse.html). Det hör bland annat till `spara_servrar()` och `exportera_csv()` i `lagring.py`, `kontrollera_server()` i `kontroller.py` och `main()` i `main.py`.

AI har använts som stöd med kod, dokumentation, tester och felsökning, bland annat i `main.py`, `kora_tester()`.

Mindverk Monitor har använts som jämförelse för uppdelningen mellan insamling, lagring och visning, samt för filbytet i `lagring.py`, `spara_servrar()`.
