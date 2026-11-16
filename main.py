# Meny, kommandon och självtester.

import argparse
import os
import sys
from pathlib import Path

from kontroller import kontrollera_server
from lagring import FALT, exportera_csv, las_servrar, spara_servrar


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

    print(server["namn"], "-", server["status"], "-", server["senast_kontrollerad"])
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
    except (OSError, ValueError) as fel:
        print("Kunde inte exportera rapporten:", fel)
        return False
    print("CSV-rapport:", rapportfil)
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
        print("9. Exportera CSV")
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
    from contextlib import redirect_stderr, redirect_stdout
    from datetime import datetime
    from io import StringIO
    from tempfile import TemporaryDirectory
    from unittest.mock import patch

    def kontrollera(villkor, meddelande):
        if not villkor:
            raise AssertionError(meddelande)

    def provkor(svar):
        with patch("builtins.input", side_effect=svar):
            with redirect_stdout(StringIO()) as utskrift:
                starta_meny(servrar, datafil)
        return utskrift.getvalue()

    def provkor_kommando(argument):
        with patch.dict(os.environ, {"INVENTORY_DATAFIL": str(datafil)}):
            with redirect_stdout(StringIO()) as utskrift, redirect_stderr(StringIO()):
                try:
                    kod = main(argument)
                except SystemExit as avslut:
                    kod = avslut.code
        return kod, utskrift.getvalue()

    try:
        with TemporaryDirectory() as katalog:
            datafil = Path(katalog) / "inventering.tmp"
            servrar = [
                {
                    "namn": namn, "adress": adress, "miljo": miljo,
                    "roll": "webb, övervakning", "status": "unknown", "senast_kontrollerad": ""
                }
                for namn, adress, miljo in [
                    ("dev01", "127.0.0.1", "dev"),
                    ("test01", "192.0.2.10", "test"),
                    ("prod01", "localhost", "prod")
                ]
            ]

            kontrollera(hitta_server(servrar, "prod01") == servrar[2], "Sökningen gav fel server.")
            kontrollera(hitta_server(servrar, "saknas") is None, "Okänt namn ska ge None.")
            for server in servrar:
                kontrollera(
                    filtrera_servrar(servrar, server["miljo"]) == [server],
                    "Miljöfiltret gav fel resultat."
                )
            tabellservrar = [
                dict(servrar[0], roll="utveckling och övervakning", senast_kontrollerad="2026-11-16 10:00"),
                dict(servrar[1], status="down")
            ]
            with redirect_stdout(StringIO()) as utskrift:
                visa_servrar(tabellservrar)
                visa_servrar([])
            rader = utskrift.getvalue().splitlines()
            kontrollera(
                rader[0].index("Status") == rader[1].index("unknown") == rader[2].index("down")
                and all(varde in rader[1] for varde in tabellservrar[0].values())
                and rader[-1] == "Inga servrar att visa.",
                "Tabellen saknar data eller har ojämna kolumner."
            )
            kontrollera(provkor(["1", "2", "dev01", "3"]).count("Senast kontrollerad") == 2,
                        "Listan och sökningen ska visa tabellen.")
            print("Sökning, miljöfilter och tabell: OK")

            kontrollera(las_servrar(datafil) == [], "Saknad fil ska ge en tom lista.")
            spara_servrar(servrar, datafil)
            kontrollera(las_servrar(datafil) == servrar, "JSON sparades eller lästes fel.")
            for innehall in ["{trasig JSON", "[123]"]:
                datafil.write_text(innehall, encoding="utf-8")
                try:
                    las_servrar(datafil)
                except ValueError:
                    pass
                else:
                    raise AssertionError("Felaktiga data godkändes.")
                kontrollera(datafil.read_text() == innehall, "Läsningen ändrade filen.")
            spara_servrar(servrar, datafil)
            tidigare_data = datafil.read_bytes()
            provkor(["9", "3"])
            rapporter = list((Path(katalog) / "rapporter").glob("inventering_*.csv"))
            kontrollera(len(rapporter) == 1, "CSV-rapporten skapades inte.")
            datetime.strptime(rapporter[0].stem, "inventering_%Y-%m-%d_%H%M%S_%f")
            with rapporter[0].open(encoding="utf-8", newline="") as fil:
                lasare = csv.DictReader(fil)
                kontrollera(lasare.fieldnames == list(servrar[0]) and list(lasare) == servrar, "Fel innehåll i CSV.")
            kontrollera(datafil.read_bytes() == tidigare_data, "Exporten ändrade JSON.")
            with patch.dict(os.environ):
                os.environ.pop("INVENTORY_DATAFIL", None)
                kontrollera(hamta_datafil() == Path(__file__).with_name("servrar.json"), "Fel standardfil.")
                os.environ["INVENTORY_DATAFIL"] = str(datafil)
                kontrollera(hamta_datafil() == datafil, "Miljövariabeln valde inte rätt fil.")
            kod, utskrift = provkor_kommando(["--lista", "--miljo", "prod"])
            kontrollera(kod == 0 and "prod01" in utskrift and "dev01" not in utskrift
                        and "test01" not in utskrift, "Kommandot filtrerade fel miljö.")
            for argument, kod in [
                (["--lista"], 0), (["--export"], 0), (["--help"], 0),
                (["--miljo", "prod"], 2), (["--lista", "--export"], 2)
            ]:
                kontrollera(provkor_kommando(argument)[0] == kod, f"Fel exitkod för {argument}.")
            kontrollera(len(list((Path(katalog) / "rapporter").glob("*.csv"))) == 2,
                        "Export via kommandoraden skapade ingen rapport.")
            kontrollera(datafil.read_bytes() == tidigare_data, "Kommandona ändrade JSON.")
            print("JSON, CSV och inställningar: OK")

            svar = [
                "99", "4", "", "fel namn", "prod01", "ny01",
                "", "-c", "localhost", "staging", " DEV ", "", "webbserver",
                "6", "dev", "3"
            ]
            utskrift = provkor(svar)
            kontrollera(len(servrar) == 4, "Servern lades inte till.")
            kontrollera(
                hitta_server(servrar, "ny01")["miljo"] == "dev"
                and "ny01" in utskrift and "localhost" in utskrift and "prod01" not in utskrift
                and "Senast kontrollerad" in utskrift,
                "Tillägg eller filtrering i menyn fungerar inte."
            )
            fore = las_servrar(datafil)
            utskrift = provkor(["5", "prod01", "fel", "nej", "3"])
            kontrollera(
                servrar == fore and las_servrar(datafil) == fore and "Svara ja eller nej." in utskrift,
                "Prod-servern måste bevaras vid felaktigt svar och nej."
            )
            provkor(["5", "prod01", "ja", "5", "ny01", "3"])
            kontrollera(
                hitta_server(servrar, "prod01") is None and hitta_server(servrar, "ny01") is None
                and las_servrar(datafil) == servrar,
                "Borttagningen sparades inte korrekt."
            )
            print("Meny, tillägg och borttagning: OK")

            resultat = [
                subprocess.CompletedProcess([], 1),
                subprocess.CompletedProcess([], 0)
            ]
            with patch("kontroller.subprocess.run", side_effect=resultat) as ping:
                kontrollera(provkor_kommando(["--kontrollera-alla"])[0] == 1,
                            "En nerevarande server ska ge exitkod 1.")
            servrar = las_servrar(datafil)
            kontrollera(
                [server["status"] for server in servrar] == ["down", "up"],
                "Kontrollen av alla servrar gav fel status."
            )
            kontrollera(ping.call_count == len(servrar), "Alla servrar kontrollerades inte.")
            for anrop, server in zip(ping.call_args_list, servrar):
                kontrollera(anrop.args[0] == ["ping", "-c", "1", server["adress"]], "Fel pingkommando.")
                datetime.strptime(server["senast_kontrollerad"], "%Y-%m-%d %H:%M")
            with patch("kontroller.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
                for argument in [["--kontrollera", "dev01"], ["--kontrollera-alla"]]:
                    kontrollera(provkor_kommando(argument)[0] == 0, "Lyckad kontroll ska ge exitkod 0.")
            with patch("kontroller.subprocess.run") as ping:
                for namn in ["saknas", ""]:
                    kontrollera(provkor_kommando(["--kontrollera", namn])[0] == 1,
                                "Okänt namn ska ge exitkod 1.")
                kontrollera(not ping.called, "Okänt namn ska inte starta ping.")
            with patch("kontroller.subprocess.run", side_effect=subprocess.TimeoutExpired([], 3)):
                kontrollera(provkor_kommando(["--kontrollera", "dev01"])[0] == 1,
                            "Timeout ska ge exitkod 1.")
            servrar = las_servrar(datafil)
            kontrollera(servrar[0]["status"] == "down", "Timeout ska ge down.")
            print("Ping, kontrolltid och exitkoder: OK")

            servrar[0]["senast_kontrollerad"] = "2000-01-01 00:00"
            spara_servrar(servrar, datafil)
            fore = las_servrar(datafil)
            tidigare_data = datafil.read_bytes()
            with patch("kontroller.subprocess.run", side_effect=FileNotFoundError("ping saknas")):
                provkor(["7", "dev01", "3"])
            kontrollera(servrar == fore, "Saknat ping ändrade servern.")
            with patch("lagring.json.dump", side_effect=OSError("skrivfel")):
                try:
                    spara_servrar(servrar, datafil)
                except OSError:
                    pass
                else:
                    raise AssertionError("Skrivfelet rapporterades inte.")
            kontrollera(datafil.read_bytes() == tidigare_data, "Skrivfelet skadade datafilen.")
            datafil.with_name(datafil.name + ".tmp").unlink()
            datafil.with_name(datafil.name + ".tmp").mkdir()
            provkor(["5", "test01", "3"])
            with patch("kontroller.subprocess.run", return_value=subprocess.CompletedProcess([], 0)):
                provkor(["7", "dev01", "3"])
            kontrollera(
                servrar == fore and datafil.read_bytes() == tidigare_data,
                "Listan och filen ska bevaras vid fel."
            )
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
    kommandon.add_argument("--export", dest="exportera", action="store_true", help="Skapa en CSV-rapport.")
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
