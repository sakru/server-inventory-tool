# Läser och sparar serverlistan i JSON.

import json


def validera_servrar(servrar):
    if not isinstance(servrar, list):
        raise ValueError("Datafilen måste innehålla en lista med servrar.")

    namn = []
    for server in servrar:
        if not isinstance(server, dict):
            raise ValueError("Varje server måste vara en dictionary.")
        for falt in ["namn", "adress", "miljo", "roll", "status", "senast_kontrollerad"]:
            if not isinstance(server.get(falt), str):
                raise ValueError(f"Fältet '{falt}' saknas eller är inte en sträng.")
        for falt in ["namn", "adress", "roll"]:
            if not server[falt].strip():
                raise ValueError(f"Fältet '{falt}' får inte vara tomt.")
        if any(tecken.isspace() for tecken in server["namn"]):
            raise ValueError("Servernamn får inte innehålla blanksteg.")
        if any(tecken.isspace() for tecken in server["adress"]) or server["adress"].startswith("-"):
            raise ValueError("Adressen får inte innehålla blanksteg eller börja med '-'.")
        if server["miljo"] not in ["dev", "test", "prod"]:
            raise ValueError("Miljön måste vara dev, test eller prod.")
        if server["status"] not in ["up", "down", "unknown"]:
            raise ValueError("Status måste vara up, down eller unknown.")
        if server["namn"] in namn:
            raise ValueError(f"Servernamnet '{server['namn']}' finns flera gånger.")
        namn.append(server["namn"])


def las_servrar(datafil):
    if not datafil.exists():
        return []

    with datafil.open("r", encoding="utf-8") as fil:
        servrar = json.load(fil)

    validera_servrar(servrar)
    return servrar


def spara_servrar(servrar, datafil):
    validera_servrar(servrar)
    tillfallig_fil = datafil.with_name(datafil.name + ".tmp")
    with tillfallig_fil.open("w", encoding="utf-8") as fil:
        json.dump(servrar, fil, ensure_ascii=False, indent=2)
        fil.write("\n")
    tillfallig_fil.replace(datafil)
