# Reflektion

Server Inventory Tool håller reda på servrar, kontrollerar deras adresser och sparar resultaten. Två av lösningarna, listan med dictionaries och sparandet efter varje ändring, är bestämda i uppgiften. De går ändå att jämföra med andra lösningar. De två fördjupningarna är säkrare inmatning och en TXT-sammanfattning.

MindverkSR är min egen server och testmiljö. Där använder jag Mindverk Monitor, som samlar in uppgifter och sparar dem i JSON. En annan del visar resultatet i terminalen. Den uppdelningen går att känna igen i skolprojektets tre moduler. Server Inventory Tool har färre uppgifter, så det går lättare att följa vad varje funktion gör.

## 1. En lista med dictionaries

I `main.py`, `starta_meny()`, skapas en dictionary för varje ny server. Den läggs sedan i listan `servrar`. Namn, adress och övriga fält hör ihop i samma post. Det är en enkel struktur att gå igenom, lägga till i och ta bort från. `las_servrar()` i `lagring.py` läser in samma struktur från JSON.

Med servernamnet som nyckel i en dictionary skulle en server kunna slås upp direkt. Nu behöver `hitta_server()` i `main.py` söka genom listan tills namnet hittas. Även kontrollen av dubbla namn behöver söka bland befintliga namn.

För en liten serverlista fungerar det bra. Samma poster kan användas vid utskrift, filtrering och export. Många sökningar skulle däremot ta mer arbete än med en dictionary. Med namn som nycklar tillkommer en annan sak att hålla reda på: vid ett namnbyte måste även nyckeln bytas.

Vid många sökningar kan en extra dictionary med namn som nyckel vara ett nästa steg. En databas blir mer relevant om flera användare ska ändra uppgifter samtidigt eller om historik behöver sparas. Bara antalet 1000 servrar gör inte i sig en databas nödvändig.

## 2. Spara efter varje ändring

I `main.py` sparar menyn efter tillägg och borttagning. `kontrollera_och_spara()` sparar efter en kontroll. Fördelen är att redan sparade ändringar finns kvar om körningen avbryts senare. Användaren behöver inte komma ihåg ett eget sparkommando.

Att spara först vid avslut skulle ge färre skrivningar. Då kan däremot alla ändringar sedan starten försvinna om processen stoppas oväntat. Med den här datamängden är det viktigare att de senaste resultaten finns kvar än att minska antalet skrivningar.

`spara_servrar()` i `lagring.py` skriver först en tillfällig fil och ersätter sedan datafilen. Mindverk Monitors insamling använder också ett sådant filbyte för sitt JSON-resultat. En läsare kan då få den gamla eller nya färdiga filen i stället för en halvskriven fil.

Det löser däremot inte samtidiga ändringar. Två körningar kan skriva över varandras uppgifter, och de använder samma namn för den tillfälliga filen. Dessutom skrivs hela inventeringen efter varje ping. I en större version kan resultat sparas i mindre omgångar. Det minskar skrivningarna men innebär att de senaste resultaten sedan förra sparandet kan förloras. Om flera processer ska skriva behövs också låsning eller en databas med transaktioner.

## 3. Fråga igen vid felaktig inmatning

För säkrare inmatning används `las_text()` i `main.py`. Den frågar igen om ett värde är tomt eller innehåller blanksteg där de är förbjudna. `las_miljo()` gör samma sak när miljön är felaktig. Rollen får innehålla flera ord, eftersom det kan behövas för att beskriva serverns uppgift.

Alla fält skulle kunna läsas in först och kontrolleras när de ska sparas. Det skulle göra inmatningsdelen kortare, men felet upptäcks senare. I menyn går det lättare att rätta ett fält när frågan fortfarande visas.

Funktionerna återanvänds, men data måste även kontrolleras när JSON läses. Annars kan manuella ändringar i filen gå förbi menyreglerna. Därför finns `validera_servrar()` i `lagring.py` också. Nackdelen är att regler, exempelvis tillåtna miljöer, behöver hållas samstämmiga på flera ställen.

Kontrollen av inmatningen garanterar inte att en adress finns eller går att nå. `kontrollera_server()` i `kontroller.py` provar sedan om den svarar på ping. Vid import av många servrar skulle upprepade frågor vara opraktiska. Då passar en lista med fel per post bättre. För fler fält kan gemensamma regler minska risken att meny och filkontroll börjar skilja sig åt.

## 4. CSV tillsammans med en TXT-sammanfattning

CSV hör till grundkraven. Fördjupningen är TXT-filen som skrivs av `exportera_sammanfattning()` i `lagring.py`. `exportera_rapport()` i `main.py` skapar båda filerna med samma grundnamn. CSV har en rad per server. TXT visar hur många som är `up`, `down` och `unknown`, totalt och i varje miljö.

Det skulle gå att räkna direkt i CSV-filen med ett kalkylprogram, eller att bara visa totalsummorna i terminalen. En TXT-fil går att spara och läsa tillsammans med rapporten senare. `unknown` har en egen kolumn, eftersom noll `down` inte betyder att alla servrar har kontrollerats.

Sammanfattningen visar inte vilka servrar som har problem, så CSV behövs för detaljerna. Två filer innebär också två skrivningar. Om TXT-skrivningen misslyckas kan CSV redan finnas kvar. Exporten räknar sparade statusvärden och startar ingen ny kontroll, så rapporten kan innehålla gamla resultat.

För många nattkörningar behövs ett sätt att hantera gamla rapporter. Om bara andra program ska läsa resultaten kan CSV räcka som rapportformat. TXT passar främst den som snabbt vill läsa läget.

## 1000 servrar och en nattlig pipeline

`kontrollera_alla()` i `main.py` kör en server i taget. I `kontroller.py`, `kontrollera_server()`, är tidsgränsen tre sekunder. Om alla 1000 kontroller når den gränsen går ungefär 50 minuter bara åt till väntan på ping. Processstarter, validering och filskrivning tillkommer. Dessutom görs 1000 fulla sparningar av inventeringen.

För att korta väntetiden kan flera kontroller köras samtidigt, med en gräns för hur många som får pågå. Gränsen behöver provas i nätverket. Resultaten kan lämnas till en gemensam del som uppdaterar listan och sparar filen. Då konkurrerar inte kontrollerna om samma fil. Även här finns en koppling till Monitor, där insamlingen skriver filen och visningen läser den.

CLI-läget i `main.py`, `main()`, passar redan för en automatisk körning. Ett nattjobb skulle först köra `--kontrollera-alla`, spara dess exitkod och sedan köra `--export` som en separat åtgärd. Exporten behöver köras även när kontrollen ger `1`, annars kan rapporten utebli just när en server inte svarar. Exportens exitkod behöver också kontrolleras.

Jobbet behöver fasta sökvägar, exempelvis en absolut `INVENTORY_DATAFIL`, tillgång till ping och rättigheter att skriva data och rapporter. Två nattjobb bör inte ändra samma inventering samtidigt. Rapporter kan sparas som resultat från körningen och rensas efter en bestämd tid, medan de fortsätter vara uteslutna från Git.

Nu betyder exitkod `1` både otillgängliga servrar och tekniska fel. Om ping saknas behålls tidigare status och kontrolltid. En gammal `up` kan därför fortfarande finnas i rapporten. En större lösning behöver en tydlig fellogg och kontroll av när uppgifterna senast uppdaterades. Självtesterna i `main.py`, `kora_tester()`, kontrollerar logiken med simulerade svar. Prestanda och beteende i den riktiga nätmiljön behöver undersökas separat innan en sådan driftversion används.
