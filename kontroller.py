# Kontrollerar servrar med ping.

import subprocess
from datetime import datetime


def kontrollera_server(server):
    adress = server["adress"].strip()
    if not adress or adress.startswith("-") or any(tecken.isspace() for tecken in adress):
        raise ValueError("Ange en adress utan blanksteg eller inledande '-'.")

    kommando = ["ping", "-c", "1", adress]
    try:
        resultat = subprocess.run(
            kommando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
            check=False
        )
    except subprocess.TimeoutExpired:
        status = "down"
    else:
        if resultat.returncode == 0:
            status = "up"
        else:
            status = "down"

    server["status"] = status
    server["senast_kontrollerad"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return status
