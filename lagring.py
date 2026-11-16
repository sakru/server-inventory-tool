# Läser och sparar serverlistan i JSON.

import json


def las_servrar(datafil):
    if not datafil.exists():
        return []

    with datafil.open("r", encoding="utf-8") as fil:
        servrar = json.load(fil)

    if not isinstance(servrar, list):
        raise ValueError("Datafilen måste innehålla en lista med servrar.")

    return servrar


def spara_servrar(servrar, datafil):
    tillfallig_fil = datafil.with_suffix(".tmp")
    with tillfallig_fil.open("w", encoding="utf-8") as fil:
        json.dump(servrar, fil, ensure_ascii=False, indent=2)
        fil.write("\n")
    tillfallig_fil.replace(datafil)
