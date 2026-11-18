# Reflektion

Utkast för genomgång före inlämning.

Server Inventory Tool ska hålla reda på servrar, kontrollera dem och spara resultaten. Det behöver gå att förstå vad som händer när något misslyckas. Här värderas fyra lösningar i programmet. Listan med dictionaries och sparandet efter varje ändring ingår i uppgiftens krav, men det finns ändå skäl att jämföra dem med andra sätt att bygga programmet.

Mindverk Monitor ger en koppling till arbetet med en större övervakningslösning. Där samlar en del in uppgifter, skriver en JSON-fil och låter en annan del visa resultatet i terminalen. Skolprojektet använder samma idé om att skilja kontroller, filer och visning åt. Det gör sambandet tydligt utan att behöva ta med hela Monitors funktionalitet.

## 1. En lista med dictionaries

I `main.py`, `starta_meny()`, läggs varje ny server i en dictionary och sedan i listan `servrar`. Namn, adress och övriga fält hör ihop i samma post. För den lilla inventeringen är det lätt att följa koden och lägga till eller ta bort en server. Strukturen passar också JSON-filen som läses i `lagring.py`, `las_servrar()`.

Ett alternativ är en dictionary där servernamnet är nyckeln. Då går det att slå upp en server direkt. Med listan måste `hitta_server()` i `main.py` gå igenom poster tills rätt namn hittas. Även kontrollen av dubbla namn behöver söka bland befintliga namn.

Listan är rimlig här eftersom datamängden är liten och samma poster används för utskrift, filtrering och export. Nackdelen märks när många uppslagningar behövs. Ett namnbyte skulle samtidigt behöva hanteras särskilt om namnet användes som dictionarynyckel.

Vid många sökningar kan en extra dictionary med namn som nyckel vara ett nästa steg. En databas blir mer relevant om flera användare ska ändra uppgifter samtidigt eller om historik behöver sparas. Bara antalet 1000 servrar gör inte i sig en databas nödvändig.

## 2. Spara efter varje ändring

I `main.py` sparar menyn efter tillägg och borttagning. `kontrollera_och_spara()` sparar efter en kontroll. Fördelen är att redan sparade ändringar finns kvar om körningen avbryts senare. Användaren behöver inte komma ihåg ett eget sparkommando.

Ett alternativ är att spara först vid avslut. Det skulle ge färre skrivningar, men ändringarna sedan starten kan gå förlorade om processen stoppas oväntat. För ett litet verktyg väger det tyngre att bevara arbetet än att minska antalet filskrivningar.

`spara_servrar()` i `lagring.py` skriver först en tillfällig fil och ersätter sedan datafilen. Mindverk Monitors insamling använder också ett sådant filbyte för sitt JSON-resultat. En läsare kan då få den gamla eller nya färdiga filen i stället för en halvskriven fil.

Det löser däremot inte samtidiga ändringar. Två körningar kan skriva över varandras uppgifter, och de använder samma namn för den tillfälliga filen. Dessutom skrivs hela inventeringen efter varje ping. I en större version kan resultat sparas i mindre omgångar. Det minskar skrivningarna men innebär att de senaste resultaten sedan förra sparandet kan förloras. Om flera processer ska skriva behövs också låsning eller en databas med transaktioner.

## 3. Fråga igen vid felaktig inmatning

Den ena valda fördjupningen är säkrare inmatning. I `main.py`, `las_text()`, avvisas tomma värden. När blanksteg inte är tillåtna kontrolleras även det. `las_miljo()` fortsätter fråga tills miljön är giltig. Rollen får däremot innehålla flera ord.

Ett annat sätt är att läsa alla fält och först kontrollera dem när de ska sparas. Då blir själva inmatningen kortare, men användaren får återkoppling senare. I en textmeny är det lättare att rätta ett fält direkt vid frågan.

Funktionerna återanvänds, men data måste även kontrolleras när JSON läses. Annars kan manuella ändringar i filen gå förbi menyreglerna. Därför finns `validera_servrar()` i `lagring.py` också. Nackdelen är att regler, exempelvis tillåtna miljöer, behöver hållas samstämmiga på flera ställen.

Kontrollen av inmatningen garanterar inte att en adress finns eller går att nå. `kontrollera_server()` i `kontroller.py` provar sedan om den svarar på ping. Vid import av många servrar skulle upprepade frågor vara opraktiska. Då passar en lista med fel per post bättre. För fler fält kan gemensamma regler minska risken att meny och filkontroll börjar skilja sig åt.

## 4. CSV tillsammans med en TXT-sammanfattning

CSV-exporten är ett G-krav. Den andra valda fördjupningen är TXT-sammanfattningen i `lagring.py`, `exportera_sammanfattning()`. `exportera_rapport()` i `main.py` skapar båda filerna med samma grundnamn. CSV behåller serverraderna, medan TXT visar antalet `up`, `down` och `unknown` totalt och per miljö.

Ett alternativ är att bara skapa CSV och låta läsaren räkna själv i ett kalkylprogram. En annan möjlighet är att bara skriva sammanfattningen i terminalen. TXT gör det lätt att spara och läsa en kort översikt från en viss körning. Att visa `unknown` separat gör också skillnad: noll `down` betyder inte att alla servrar har kontrollerats.

Sammanfattningen visar inte vilka servrar som har problem, så CSV behövs för detaljerna. Två filer innebär också två skrivningar. Om TXT-skrivningen misslyckas kan CSV redan finnas kvar. Exporten räknar sparade statusvärden och startar ingen ny kontroll, så rapporten kan innehålla gamla resultat.

För många nattkörningar behövs ett sätt att hantera gamla rapporter. Om bara andra program ska läsa resultaten kan CSV räcka som rapportformat. TXT passar främst den som snabbt vill läsa läget.

## 1000 servrar och en nattlig pipeline

`kontrollera_alla()` i `main.py` kör en server i taget. I `kontroller.py`, `kontrollera_server()`, är tidsgränsen tre sekunder. Om alla 1000 kontroller når den gränsen går ungefär 50 minuter bara åt till väntan på ping. Processstarter, validering och filskrivning tillkommer. Dessutom görs 1000 fulla sparningar av inventeringen.

En större version kan köra ett begränsat antal kontroller samtidigt. Gränsen behöver provas mot nätverkets och datorns kapacitet. Varje kontroll kan lämna sitt resultat till en gemensam del som uppdaterar listan och sparar. Det undviker att varje kontroll försöker skriva samma fil. Mindverk Monitors uppdelning mellan insamling och läsning är ett användbart mönster även här.

CLI-läget i `main.py`, `main()`, passar redan för en automatisk körning. Ett nattjobb skulle först köra `--kontrollera-alla`, spara dess exitkod och sedan köra `--export` som en separat åtgärd. Exporten behöver köras även när kontrollen ger `1`, annars kan rapporten utebli just när en server inte svarar. Exportens exitkod behöver också kontrolleras.

Jobbet behöver fasta sökvägar, exempelvis en absolut `INVENTORY_DATAFIL`, tillgång till ping och rättigheter att skriva data och rapporter. Två nattjobb bör inte ändra samma inventering samtidigt. Rapporter kan sparas som resultat från körningen och rensas efter en bestämd tid, medan de fortsätter vara uteslutna från Git.

Nu betyder exitkod `1` både otillgängliga servrar och tekniska fel. Om ping saknas behålls tidigare status och kontrolltid. En gammal `up` kan därför fortfarande finnas i rapporten. En större lösning behöver en tydlig fellogg och kontroll av när uppgifterna senast uppdaterades. Självtesterna i `main.py`, `kora_tester()`, kontrollerar logiken med simulerade svar. Prestanda och beteende i den riktiga nätmiljön behöver undersökas separat innan en sådan driftversion används.
