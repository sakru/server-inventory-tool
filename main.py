# Den första servern lagras som en dictionary med sex fält.
forsta_server = {
    "namn": "web01",
    "adress": "example.com",
    "miljo": "prod",
    "roll": "webbserver",
    "status": "unknown",
    "senast_kontrollerad": ""
}

# Listan innehåller först bara den första servern.
servrar = [forsta_server]

# Skapa den andra servern och lägg till den i listan.
andra_server = {
    "namn": "db01",
    "adress": "127.0.0.1",
    "miljo": "prod",
    "roll": "databas",
    "status": "unknown",
    "senast_kontrollerad": ""
}
servrar.append(andra_server)

# Visa menyn tills användaren väljer att avsluta.
while True:
    print()
    print("Server Inventory Tool")
    print("1. Visa alla servrar")
    print("2. Hitta server efter namn")
    print("3. Avsluta")
    print("4. Lägg till server")
    val = input("Ditt val: ").strip()

    if val == "1":
        for server in servrar:
            print(server["namn"], "-", server["adress"])

    elif val == "2":
        sokt_namn = input("Servernamn: ").strip()
        # Nollställ sökresultatet inför varje ny sökning.
        hittad_server = None

        for server in servrar:
            if server["namn"] == sokt_namn:
                hittad_server = server
                break

        if hittad_server is None:
            print("Servern finns inte.")
        else:
            print("Hittad server:", hittad_server["namn"])
            print("Adress:", hittad_server["adress"])

    elif val == "4":
        # Fråga igen tills namnet är ledigt och inte tomt.
        while True:
            namn = input("Namn på den nya servern: ").strip()
            namn_finns = False

            for server in servrar:
                if server["namn"] == namn:
                    namn_finns = True
                    break

            if namn == "":
                print("Namnet får inte vara tomt.")
            elif namn_finns:
                print("Namnet finns redan. Välj ett annat namn.")
            else:
                break

        adress = input("Adress: ").strip()

        # Godkänn bara miljöerna dev, test och prod.
        while True:
            miljo = input("Miljö (dev/test/prod): ").strip().lower()
            if miljo in ["dev", "test", "prod"]:
                break
            print("Ogiltig miljö. Välj dev, test eller prod.")

        roll = input("Roll: ").strip()
        ny_server = {
            "namn": namn,
            "adress": adress,
            "miljo": miljo,
            "roll": roll,
            "status": "unknown",
            "senast_kontrollerad": ""
        }
        servrar.append(ny_server)
        print("Servern har lagts till:", namn)

    elif val == "3":
        print("Avslutar.")
        break

    else:
        print("Ogiltigt val. Välj 1, 2, 3 eller 4.")
