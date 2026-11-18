# Meny, kommandon och självtester.

import argparse
import os
import sys
from pathlib import Path

from kontroller import kontrollera_server
from lagring import FALT, exportera_csv, exportera_sammanfattning, las_servrar, spara_servrar


def hamta_datafil():
    filnamn = os.environ.get("INVENTORY_DATAFIL")
    if filnamn:
        return Path(filnamn).expanduser()
    return Path(__file__).with_name("servrar.json")


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


def visa_servrar(servrar):
    if not servrar:
        print("Inga servrar att visa.")
        return

    rader = [["Namn", "Adress", "Miljö", "Roll", "Status", "Senast kontrollerad"]]
    for server in servrar:
        rader.append([server[falt] or "-" for falt in FALT])

    bredder = []
    for kolumn in zip(*rader):
        bredder.append(max(len(text) for text in kolumn))

    for rad in rader:
        delar = []
        for text, bredd in zip(rad, bredder):
            delar.append(f"{text:<{bredd}}")
        print("  ".join(delar))


def las_text(fragetext, utan_blanksteg=False):
    while True:
        varde = input(fragetext).strip()
        if not varde:
            print("Fältet får inte vara tomt.")
        elif utan_blanksteg and any(tecken.isspace() for tecken in varde):
            print("Värdet får inte innehålla blanksteg.")
        else:
            return varde


def las_miljo():
    while True:
        miljo = input("Miljö (dev/test/prod): ").strip().lower()
        if miljo in ["dev", "test", "prod"]:
            return miljo
        print("Ogiltig miljö. Välj dev, test eller prod.")


def kontrollera_och_spara(servrar, server, datafil):
    tidigare_status = server["status"]
    tidigare_tid = server["senast_kontrollerad"]
    try:
        kontrollera_server(server)
        spara_servrar(servrar, datafil)
    except (OSError, ValueError) as fel:
        server["status"] = tidigare_status
        server["senast_kontrollerad"] = tidigare_tid
        print(f"Kunde inte kontrollera {server['namn']}: {fel}")
        return False

    namnbredd = max(len(post["namn"]) for post in servrar)
    print(f"{server['namn']:<{namnbredd}}  {server['status']:<7}  {server['senast_kontrollerad']}")
    return server["status"] == "up"


def kontrollera_alla(servrar, datafil):
    if not servrar:
        print("Inga servrar att kontrollera.")
        return True

    alla_uppe = True
    for server in servrar:
        if not kontrollera_och_spara(servrar, server, datafil):
            alla_uppe = False
    return alla_uppe


def exportera_rapport(servrar, datafil):
    try:
        rapportfil = exportera_csv(servrar, datafil.parent / "rapporter")
        textfil = exportera_sammanfattning(servrar, rapportfil.with_suffix(".txt"))
    except (OSError, ValueError) as fel:
        print("Kunde inte exportera rapporten:", fel)
        return False
    print("CSV-rapport:", rapportfil)
    print("TXT-sammanfattning:", textfil)
    return True


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
        print("7. Kontrollera en server")
        print("8. Kontrollera alla servrar")
        print("9. Exportera rapporter (CSV och TXT)")
        val = input("Ditt val: ").strip()

        if val == "1":
            visa_servrar(servrar)

        elif val == "2":
            sokt_namn = las_text("Servernamn: ", utan_blanksteg=True)
            hittad_server = hitta_server(servrar, sokt_namn)

            if hittad_server is None:
                print("Servern finns inte.")
            else:
                visa_servrar([hittad_server])

        elif val == "4":
            while True:
                namn = las_text("Namn på den nya servern: ", utan_blanksteg=True)
                if hitta_server(servrar, namn) is not None:
                    print("Namnet finns redan. Välj ett annat namn.")
                else:
                    break

            while True:
                adress = las_text("Adress: ", utan_blanksteg=True)
                if not adress.startswith("-"):
                    break
                print("Adressen får inte börja med '-'.")

            miljo = las_miljo()

            roll = las_text("Roll: ")
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
            except (OSError, ValueError) as fel:
                servrar.remove(ny_server)
                print("Kunde inte spara servern:", fel)
            else:
                print("Servern har lagts till och sparats:", namn)

        elif val == "5":
            namn = las_text("Servernamn att ta bort: ", utan_blanksteg=True)
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
            except (OSError, ValueError) as fel:
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
                visa_servrar(filtrerade)

        elif val == "7":
            namn = las_text("Servernamn att kontrollera: ", utan_blanksteg=True)
            server = hitta_server(servrar, namn)
            if server is None:
                print("Servern finns inte.")
            else:
                kontrollera_och_spara(servrar, server, datafil)

        elif val == "8":
            kontrollera_alla(servrar, datafil)

        elif val == "9":
            exportera_rapport(servrar, datafil)

        elif val == "3":
            print("Avslutar.")
            break

        else:
            print("Ogiltigt val. Välj ett nummer från 1 till 9.")


def kora_tester():
    import csv
    import subprocess
    from contextlib import redirect_stdout
    from datetime import datetime
    from io import StringIO
    from tempfile import TemporaryDirectory
    from unittest.mock import patch

    def kontrollera(villkor, meddelande):
        if not villkor:
            raise AssertionError(meddelande)

    def provkor(argument, svar=()):
        with patch.dict(os.environ, {"INVENTORY_DATAFIL": str(datafil)}):
            with patch("builtins.input", side_effect=svar), redirect_stdout(StringIO()) as utskrift:
                kod = main(argument)
        return kod, utskrift.getvalue()

    try:
        with TemporaryDirectory() as katalog:
            datafil = Path(katalog) / "inventering.tmp"
            servrar = []
            for namn, adress, miljo, status in [
                ("dev01", "127.0.0.1", "dev", "up"),
                ("test01", "192.0.2.10", "test", "down"),
                ("prod01", "localhost", "prod", "unknown")
            ]:
                servrar.append({
                    "namn": namn, "adress": adress, "miljo": miljo,
                    "roll": "webb, övervakning", "status": status, "senast_kontrollerad": ""
                })

            kontrollera(hitta_server(servrar, "prod01") == servrar[2], "Fel server vid sökning.")
            kontrollera(hitta_server(servrar, "saknas") is None, "Okänt namn ska ge None.")
            kontrollera(filtrera_servrar(servrar, "dev") == [servrar[0]], "Fel miljöfilter.")
            kontrollera(las_servrar(datafil) == [], "Saknad fil ska ge en tom lista.")
            datafil.write_text("[123]", encoding="utf-8")
            try:
                las_servrar(datafil)
            except ValueError:
                pass
            else:
                raise AssertionError("Felaktiga serverdata godkändes.")
            spara_servrar(servrar, datafil)
            kontrollera(las_servrar(datafil) == servrar, "JSON sparades eller lästes fel.")
            kod, utskrift = provkor(["--lista", "--miljo", "prod"])
            kontrollera(kod == 0 and "prod01" in utskrift and "dev01" not in utskrift, "Fel CLI-filter.")
            with patch.dict(os.environ, {"INVENTORY_DATAFIL": ""}):
                kontrollera(hamta_datafil() == Path(__file__).with_name("servrar.json"), "Fel standardfil.")
            print("Sökning, JSON och miljöfilter: OK")

            fore = datafil.read_bytes()
            kontrollera(provkor(["--export"])[0] == 0, "Exporten misslyckades.")
            rapportfil = next((Path(katalog) / "rapporter").glob("*.csv"))
            datetime.strptime(rapportfil.stem, "inventering_%Y-%m-%d_%H%M%S_%f")
            with rapportfil.open(encoding="utf-8", newline="") as fil:
                kontrollera(list(csv.DictReader(fil)) == servrar, "Fel innehåll i CSV.")
            rader = rapportfil.with_suffix(".txt").read_text(encoding="utf-8").splitlines()
            kontrollera([rad.split() for rad in rader[1:]] == [
                ["Totalt", "1", "1", "1"], ["dev", "1", "0", "0"],
                ["test", "0", "1", "0"], ["prod", "0", "0", "1"]
            ], "Fel antal i TXT-sammanfattningen.")
            kontrollera(datafil.read_bytes() == fore, "Exporten ändrade JSON.")
            print("CSV och TXT: OK")

            svar = ["99", "4", "", "fel namn", "prod01", "ny01", "", "-c", "localhost",
                    "staging", " DEV ", "", "webbserver", "6", "dev", "3"]
            kod, utskrift = provkor([], svar)
            ny_server = hitta_server(las_servrar(datafil), "ny01")
            kontrollera(kod == 0 and ny_server is not None and ny_server["miljo"] == "dev"
                        and ny_server["status"] == "unknown", "Tillägget sparades inte korrekt.")
            kontrollera("Ogiltigt val." in utskrift and "ny01" in utskrift
                        and "prod01" not in utskrift and "Senast kontrollerad" in utskrift,
                        "Fel meddelande eller tabell i menyn.")
            fore = datafil.read_bytes()
            provkor([], ["5", "prod01", "fel", "nej", "3"])
            kontrollera(datafil.read_bytes() == fore, "Prod-servern togs bort utan bekräftelse.")
            provkor([], ["5", "prod01", "ja", "5", "ny01", "3"])
            servrar = las_servrar(datafil)
            kontrollera([server["namn"] for server in servrar] == ["dev01", "test01"], "Fel borttagning.")
            print("Meny, tillägg och borttagning: OK")

            with patch("kontroller.subprocess.run", side_effect=[
                subprocess.CompletedProcess([], 1), subprocess.CompletedProcess([], 0)
            ]) as ping:
                kod, utskrift = provkor(["--kontrollera-alla"])
            servrar = las_servrar(datafil)
            kontrollera(kod == 1 and ping.call_count == 2
                        and [server["status"] for server in servrar] == ["down", "up"], "Fel pingresultat.")
            rader = utskrift.splitlines()
            kontrollera(rader[0].index("down") == rader[1].index("up"), "Ojämna pingkolumner.")
            for anrop, server in zip(ping.call_args_list, servrar):
                kontrollera(anrop.args[0] == ["ping", "-c", "1", server["adress"]], "Fel pingkommando.")
                datetime.strptime(server["senast_kontrollerad"], "%Y-%m-%d %H:%M")
            with patch("kontroller.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
                kontrollera(provkor(["--kontrollera", "dev01"])[0] == 0, "Lyckad kontroll ska ge 0.")
                kontrollera(provkor(["--kontrollera", "saknas"])[0] == 1, "Okänt namn ska ge 1.")
            with patch("kontroller.subprocess.run", side_effect=subprocess.TimeoutExpired([], 3)):
                kontrollera(provkor(["--kontrollera", "dev01"])[0] == 1, "Timeout ska ge 1.")
            print("Ping, kontrolltid och exitkoder: OK")

            servrar[0]["status"] = "down"
            servrar[0]["senast_kontrollerad"] = "2000-01-01 00:00"
            spara_servrar(servrar, datafil)
            fore = datafil.read_bytes()
            with patch("kontroller.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
                with patch("lagring.json.dump", side_effect=OSError("skrivfel")), redirect_stdout(StringIO()):
                    lyckad = kontrollera_och_spara(servrar, servrar[0], datafil)
            kontrollera(not lyckad and servrar == las_servrar(datafil)
                        and datafil.read_bytes() == fore, "Skrivfelet ändrade inventeringen.")
            with patch("kontroller.subprocess.run", side_effect=FileNotFoundError("ping saknas")):
                with redirect_stdout(StringIO()):
                    lyckad = kontrollera_och_spara(servrar, servrar[0], datafil)
            kontrollera(not lyckad and datafil.read_bytes() == fore, "Saknat ping ändrade filen.")
            print("Skydd vid fel: OK")
    except Exception as fel:
        print("Test misslyckades:", fel, file=sys.stderr)
        return 1

    print("Alla tester godkända.")
    return 0

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Serverinventering med textmeny och kommandon.",
        epilog="Utan argument startar textmenyn."
    )
    kommandon = parser.add_mutually_exclusive_group()
    kommandon.add_argument("--lista", action="store_true", help="Visa alla servrar.")
    kommandon.add_argument("--kontrollera", metavar="NAMN", help="Kontrollera en server och spara status.")
    kommandon.add_argument("--kontrollera-alla", action="store_true", help="Kontrollera alla servrar.")
    kommandon.add_argument("--export", dest="exportera", action="store_true", help="Skapa CSV och TXT-sammanfattning.")
    kommandon.add_argument("--test", action="store_true", help="Kör självtester med tillfälliga data.")
    parser.add_argument("--miljo", choices=["dev", "test", "prod"], help="Filtrera listan efter miljö, med --lista.")
    args = parser.parse_args(argv)

    if args.miljo and not args.lista:
        parser.error("--miljo används tillsammans med --lista.")

    if args.test:
        return kora_tester()

    try:
        datafil = hamta_datafil()
        servrar = las_servrar(datafil)
    except (ValueError, OSError, RuntimeError) as fel:
        print(f"Kunde inte läsa datafilen: {fel}", file=sys.stderr)
        return 1

    try:
        if args.lista:
            if args.miljo:
                servrar = filtrera_servrar(servrar, args.miljo)
            visa_servrar(servrar)
        elif args.kontrollera is not None:
            server = hitta_server(servrar, args.kontrollera)
            if server is None:
                print("Servern finns inte.")
                return 1
            return 0 if kontrollera_och_spara(servrar, server, datafil) else 1
        elif args.kontrollera_alla:
            return 0 if kontrollera_alla(servrar, datafil) else 1
        elif args.exportera:
            return 0 if exportera_rapport(servrar, datafil) else 1
        else:
            starta_meny(servrar, datafil)
    except EOFError:
        print("\nInmatningen avslutades.")
    except KeyboardInterrupt:
        print("\nAvbrutet.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
