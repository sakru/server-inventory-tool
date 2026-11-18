# Server Inventory Tool

Server Inventory Tool håller reda på servrar och om de svarar på ping. Uppgifterna sparas i JSON. Programmet kan användas från en meny eller genom att ange ett kommando direkt i terminalen.

## Komma igång

Du behöver Python 3 och kommandot `ping`. Koden använder Pythons standardbibliotek, så det behövs inga paket från `pip`.

Ping körs med flaggan `-c`, som fungerar på Linux och macOS. På Windows används WSL eller kursens Linuxmiljö.

Hämta projektet med Git:

```bash
git clone https://github.com/sakru/server-inventory-tool.git
cd server-inventory-tool
```

Kontrollera att Python och ping fungerar i miljön där programmet ska köras:

```bash
python3 --version
ping -c 1 127.0.0.1
```

Om `ping` saknas behöver det installeras med systemets pakethanterare. Du behöver också kunna skriva till katalogen där datafilen ligger.

## Användning

Starta menyn med:

```bash
python3 main.py
```

I menyn kan du visa och söka efter servrar, lägga till och ta bort dem, filtrera efter miljö, köra ping och exportera rapporter. Val 3 avslutar programmet.

När en server läggs till frågar programmet efter namn, adress, miljö och roll. Namnet måste vara unikt och miljön ska vara `dev`, `test` eller `prod`. För att ta bort en server i `prod` behöver du bekräfta med `ja`. Svaret `nej` avbryter.

För att visa, kontrollera eller exportera servrar kan du köra följande kommandon:

| Kommando | Vad det gör |
|---|---|
| `python3 main.py --lista` | Visar alla servrar |
| `python3 main.py --lista --miljo prod` | Visar bara produktionsservrar |
| `python3 main.py --kontrollera db01` | Kontrollerar `db01` och sparar resultatet |
| `python3 main.py --kontrollera-alla` | Kontrollerar alla servrar |
| `python3 main.py --export` | Skapar CSV och TXT |
| `python3 main.py --help` | Visar hjälp med kommandona |

Välj ett kommando per körning. `--miljo` hör ihop med `--lista` och accepterar `dev`, `test` eller `prod`. Sökning och kontroll använder serverns exakta namn.

Exitkoden är `0` när kommandot lyckas. En kontroll som ger `down`, ett okänt namn med `--kontrollera` eller ett filfel ger `1`. Det gäller även om ping inte kan startas. Felaktiga argument ger `2`. Ctrl+C under menyn eller en åtgärd ger `130`.

I Bash kan resultatet kontrolleras så här:

```bash
python3 main.py --kontrollera db01
echo $?
```

## Datafilen

Normalt används `servrar.json` bredvid `main.py`. Filen innehåller från början `web01`, `db01`, `test01` och `dev01`.

Varje server har fälten `namn`, `adress`, `miljo`, `roll`, `status` och `senast_kontrollerad`. Värdena är strängar. Status är `up`, `down` eller `unknown`. En ny server får `unknown` och en tom kontrolltid. Efter en kontroll skrivs tiden som exempelvis `2026-11-17 14:30`.

För att använda en annan fil anger du miljövariabeln `INVENTORY_DATAFIL`:

```bash
INVENTORY_DATAFIL=egna_servrar.json python3 main.py
```

Det gäller bara den körningen. Ange samma variabel nästa gång om du vill fortsätta med den filen:

```bash
INVENTORY_DATAFIL=egna_servrar.json python3 main.py --lista
```

En relativ sökväg räknas från mappen där kommandot körs. Absoluta sökvägar och `~/` fungerar också. Om variabeln är tom eller inte satt används standardfilen.

Om filen inte finns börjar programmet med en tom lista och skapar filen när något ändras. Mappen där filen ska ligga måste redan finnas. En trasig JSON-fil eller ogiltiga serverdata ger ett felmeddelande och filen lämnas orörd.

Programmet sparar direkt när en server läggs till, tas bort eller kontrolleras. Om det inte går att skriva till filen återställs ändringen i minnet.

## Kontroller och rapporter

En kontroll kör `ping -c 1 ADRESS` och väntar högst tre sekunder. Ett lyckat ping ger `up`. Ett misslyckat ping eller timeout ger `down`. Vid kontroll av alla servrar fortsätter programmet även om någon inte svarar.

En server kan vara igång trots att ping blockeras av nätverket. Om själva kommandot `ping` saknas behålls tidigare status och kontrolltid, och ett felmeddelande visas.

Exporten använder de sparade statusvärdena. Kör därför en kontroll före exporten om du vill ha nya resultat.

Rapporterna hamnar i `rapporter/` bredvid den valda JSON-filen. Mappen skapas vid behov. CSV och TXT får samma namn med datum och tid, till exempel:

```text
rapporter/inventering_2026-11-17_143000_123456.csv
rapporter/inventering_2026-11-17_143000_123456.txt
```

CSV har en rubrikrad och alla sex serverfält. TXT räknar antalet `up`, `down` och `unknown`, både totalt och för varje miljö. Även miljöer utan servrar visas med nollor.

Om TXT inte kan skrivas efter att CSV har skapats kan CSV-filen bli kvar. Exporten ändrar inte serverlistan.

Rapporterna stannar lokalt. `rapporter/` finns i `.gitignore`, tillsammans med `__pycache__/` och tillfälliga `*.tmp`-filer.

## Fördjupningar

Fördjupningarna i projektet är säkrare inmatning och en TXT-sammanfattning till rapporten.

Vid tomma fält, blanksteg i namn, fel miljö eller fel menyval frågar programmet igen. Namn och adress får inte innehålla blanksteg, och adressen får inte börja med `-`. Data som läses från JSON kontrolleras också.

TXT-filen visar hur många servrar som har varje status, totalt och i varje miljö.

## Tester

Kör självtesterna med:

```bash
python3 main.py --test
```

Testerna kontrollerar sökning, tabeller, lagring, rapporter, meny, pingresultat och exitkoder. De använder tillfälliga filer och simulerade svar från ping. Den vanliga datafilen påverkas inte.

När allt fungerar skrivs `Alla tester godkända.` och exitkoden blir `0`. Ett testfel ger `1`. Testerna kontrollerar programlogiken; den riktiga pingmiljön kan kontrolleras med kommandot under Komma igång.

## Filer

- `main.py` innehåller menyn, kommandoraden, sökning, tabeller och självtester.
- `lagring.py` läser och sparar JSON, kontrollerar data och skriver CSV och TXT.
- `kontroller.py` kör ping och uppdaterar status och kontrolltid.
- `servrar.json` innehåller inventeringen.
- `.gitignore` anger vilka filer och mappar Git ska ignorera.
- `README.md` innehåller instruktionerna för programmet.
- `REDOGORELSE.md` förklarar koden och arbetet.
- `REFLEKTION.md` tar upp lösningarnas fördelar, nackdelar och användning i en större miljö.

Menyn ligger kvar i `main.py` för att hålla projektet till tre Pythonmoduler. Menyn och kommandoraden använder samma funktioner för kontroller och lagring.
