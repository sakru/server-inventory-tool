# Meny och självtester för serverinventering.

import argparse
import sys
from pathlib import Path

from lagring import las_servrar, spara_servrar


def hitta_server(servrar, namn):
    for server in servrar:
        if server["namn"] == namn:
            return server
    return None


def filtrera_servrar(servrar, miljo):
    resultat = []
    for server in servrar:
        if server["miljo"] == miljo:
            resultat.append(server)
    return resultat


def las_miljo():
    while True:
        miljo = input("Miljö (dev/test/prod): ").strip().lower()
        if miljo in ["dev", "test", "prod"]:
            return miljo
        print("Ogiltig miljö. Välj dev, test eller prod.")


def starta_meny(servrar, datafil):
    while True:
        print()
        print("Server Inventory Tool")
        print("1. Visa alla servrar")
        print("2. Hitta server efter namn")
        print("3. Avsluta")
        print("4. Lägg till server")
        print("5. Ta bort server")
        print("6. Visa servrar i en miljö")
        val = input("Ditt val: ").strip()

        if val == "1":
            for server in servrar:
                print(server["namn"], "-", server["adress"])

        elif val == "2":
            sokt_namn = input("Servernamn: ").strip()
            hittad_server = hitta_server(servrar, sokt_namn)

            if hittad_server is None:
                print("Servern finns inte.")
            else:
                print("Hittad server:", hittad_server["namn"])
                print("Adress:", hittad_server["adress"])

        elif val == "4":
            while True:
                namn = input("Namn på den nya servern: ").strip()
                if namn == "":
                    print("Namnet får inte vara tomt.")
                elif hitta_server(servrar, namn) is not None:
                    print("Namnet finns redan. Välj ett annat namn.")
                else:
                    break

            adress = input("Adress: ").strip()

            miljo = las_miljo()

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

        elif val == "5":
            namn = input("Servernamn att ta bort: ").strip()
            hittad_server = hitta_server(servrar, namn)

            if hittad_server is None:
                print("Servern finns inte.")
                continue

            if hittad_server["miljo"] == "prod":
                while True:
                    svar = input(f"Ta bort prod-servern {namn}? (ja/nej): ").strip().lower()
                    if svar in ["ja", "nej"]:
                        break
                    print("Svara ja eller nej.")

                if svar == "nej":
                    print("Borttagningen avbröts.")
                    continue

            position = servrar.index(hittad_server)
            servrar.remove(hittad_server)
            try:
                spara_servrar(servrar, datafil)
            except OSError as fel:
                servrar.insert(position, hittad_server)
                print("Kunde inte ta bort servern:", fel)
            else:
                print("Servern har tagits bort:", namn)

        elif val == "6":
            miljo = las_miljo()
            filtrerade = filtrera_servrar(servrar, miljo)
            if not filtrerade:
                print(f"Inga servrar i miljön {miljo}.")
            else:
                for server in filtrerade:
                    print(server["namn"], "-", server["adress"])

        elif val == "3":
            print("Avslutar.")
            break

        else:
            print("Ogiltigt val. Välj 1, 2, 3, 4, 5 eller 6.")


def kora_tester():
    from contextlib import redirect_stdout
    from io import StringIO
    from tempfile import TemporaryDirectory
    from unittest.mock import patch

    def kontrollera(villkor, meddelande):
        if not villkor:
            raise AssertionError(meddelande)

    def testdata():
        return [
            {
                "namn": "prod01",
                "adress": "localhost",
                "miljo": "prod",
                "roll": "webbserver",
                "status": "unknown",
                "senast_kontrollerad": ""
            },
            {
                "namn": "dev01",
                "adress": "127.0.0.1",
                "miljo": "dev",
                "roll": "utveckling för Åke",
                "status": "unknown",
                "senast_kontrollerad": ""
            }
        ]

    def provkor_meny(servrar, datafil, svar):
        with patch("builtins.input", side_effect=svar):
            with redirect_stdout(StringIO()) as utskrift:
                starta_meny(servrar, datafil)
        return utskrift.getvalue()

    try:
        with TemporaryDirectory() as katalog:
            datafil = Path(katalog) / "servrar.json"
            servrar = testdata()

            kontrollera(
                hitta_server(servrar, "prod01") == servrar[0],
                "Sökningen hittade inte rätt server."
            )
            kontrollera(
                hitta_server(servrar, "saknas") is None,
                "Ett okänt namn ska ge None."
            )
            print("Sökning: OK")

            kontrollera(las_servrar(datafil) == [], "En saknad fil ska ge en tom lista.")
            spara_servrar(servrar, datafil)
            kontrollera(las_servrar(datafil) == servrar, "JSON sparades eller lästes fel.")
            kontrollera(
                "Åke" in datafil.read_text(encoding="utf-8"),
                "Svenska bokstäver ska vara läsbara i JSON."
            )
            datafil.write_text("{trasig JSON", encoding="utf-8")
            try:
                las_servrar(datafil)
            except ValueError:
                pass
            else:
                raise AssertionError("Trasig JSON ska ge ett fel.")
            kontrollera(
                datafil.read_text(encoding="utf-8") == "{trasig JSON",
                "Den trasiga filen ändrades vid läsning."
            )
            print("JSON: OK")

            servrar = testdata()
            testserver = servrar[1].copy()
            testserver["namn"] = "test01"
            testserver["miljo"] = "test"
            servrar.append(testserver)
            spara_servrar(servrar, datafil)
            tidigare_data = datafil.read_bytes()
            for miljo, namn in [("dev", "dev01"), ("test", "test01"), ("prod", "prod01")]:
                filtrerade = filtrera_servrar(servrar, miljo)
                kontrollera(
                    filtrerade == [hitta_server(servrar, namn)],
                    "Fel server vid filtrering av " + miljo
                )
                utskrift = provkor_meny(servrar, datafil, ["6", miljo, "3"])
                for server in servrar:
                    rad = server["namn"] + " - " + server["adress"]
                    kontrollera(
                        (rad in utskrift) == (server["miljo"] == miljo),
                        "Fel server visas i miljön " + miljo
                    )
            utskrift = provkor_meny(servrar, datafil, ["6", "", "staging", " PROD ", "3"])
            kontrollera(utskrift.count("Ogiltig miljö.") == 2, "Felaktig miljö ska frågas om.")
            kontrollera("prod01 - localhost" in utskrift, "PROD normaliserades inte.")
            kontrollera(las_servrar(datafil) == servrar, "Filtreringen ändrade listan.")
            kontrollera(datafil.read_bytes() == tidigare_data, "Filtreringen ändrade JSON.")

            servrar = testdata()
            spara_servrar(servrar, datafil)
            tidigare_data = datafil.read_bytes()
            kontrollera(filtrera_servrar(servrar, "test") == [], "Tomt filter ska ge en tom lista.")
            utskrift = provkor_meny(servrar, datafil, ["6", "test", "3"])
            kontrollera("Inga servrar i miljön test." in utskrift, "Meddelande saknas för tom miljö.")
            kontrollera(servrar == testdata(), "Ett tomt filter ändrade listan.")
            kontrollera(datafil.read_bytes() == tidigare_data, "Ett tomt filter ändrade JSON.")
            print("Filtrering dev/test/prod: OK")

            fall = [
                ("Okänt namn", ["5", "saknas", "3"], ["prod01", "dev01"]),
                ("Avbruten prod", ["5", "prod01", "nej", "3"], ["prod01", "dev01"]),
                ("Bekräftad prod", ["5", "prod01", "fel", " JA ", "3"], ["dev01"]),
                ("Borttagning dev", ["5", "dev01", "3"], ["prod01"]),
            ]
            for beskrivning, svar, forvantade_namn in fall:
                servrar = testdata()
                spara_servrar(servrar, datafil)
                provkor_meny(servrar, datafil, svar)
                kvarvarande_namn = [server["namn"] for server in servrar]
                kontrollera(kvarvarande_namn == forvantade_namn, beskrivning)
                kontrollera(las_servrar(datafil) == servrar, beskrivning + ": fel i JSON")
                print(beskrivning + ": OK")

            servrar = testdata()
            spara_servrar(servrar, datafil)
            tidigare_data = datafil.read_bytes()
            datafil.with_suffix(".tmp").mkdir()
            utskrift = provkor_meny(servrar, datafil, ["5", "prod01", "ja", "3"])
            kontrollera(servrar == testdata(), "Listan återställdes inte efter skrivfelet.")
            kontrollera(datafil.read_bytes() == tidigare_data, "Den gamla filen ändrades.")
            kontrollera(
                "Kunde inte ta bort servern:" in utskrift,
                "Skrivfelet ska visas för användaren."
            )
            kontrollera(
                "Servern har tagits bort:" not in utskrift,
                "Misslyckad borttagning får inte visas som lyckad."
            )
            print("Återställning vid skrivfel: OK")
    except Exception as fel:
        print("Test misslyckades:", fel, file=sys.stderr)
        return 1

    print("Alla tester godkända.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Serverinventering med textmeny.")
    parser.add_argument("--test", action="store_true", help="Kör självtester med tillfälliga data.")
    args = parser.parse_args(argv)

    if args.test:
        return kora_tester()

    datafil = Path(__file__).with_name("servrar.json")
    try:
        servrar = las_servrar(datafil)
    except (ValueError, OSError) as fel:
        print(f"Kunde inte läsa {datafil.name}: {fel}", file=sys.stderr)
        return 1

    starta_meny(servrar, datafil)
    return 0


if __name__ == "__main__":
    sys.exit(main())
