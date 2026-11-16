# Meny för serverinventering.

import sys
from pathlib import Path

from lagring import las_servrar, spara_servrar

datafil = Path(__file__).with_name("servrar.json")

try:
    servrar = las_servrar(datafil)
except (ValueError, OSError) as fel:
    sys.exit(f"Kunde inte läsa {datafil.name}: {fel}")

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
        try:
            spara_servrar(servrar, datafil)
        except OSError as fel:
            servrar.remove(ny_server)
            print("Kunde inte spara servern:", fel)
        else:
            print("Servern har lagts till och sparats:", namn)

    elif val == "3":
        print("Avslutar.")
        break

    else:
        print("Ogiltigt val. Välj 1, 2, 3 eller 4.")
