import time
import os

def limpiar_pantalla():
    os.system("cls" if os.name == "nt" else "clear")


def resolver_operacion(proceso):
    op = proceso["operacion"]
    a = proceso["operando1"]
    b = proceso["operando2"]

    if op == "+":
        return a + b

    elif op == "-":
        return a - b

    elif op == "*":
        return a * b

    elif op == "/":
        return a / b

    elif op == "%":
        return a % b

    elif op == "**":
        return a ** b

def mostrar_estado(
    lotes_pendientes,
    lote_actual,
    proceso_actual,
    tiempo_transcurrido,
    tiempo_restante,
    terminados,
    contador_global
):

    limpiar_pantalla()

    print("=" * 70)
    print("              SIMULADOR DE PROCESAMIENTO POR LOTES")
    print("=" * 70)

    # LOTES PENDIENTES
    print(f"\nLOTES PENDIENTES: {lotes_pendientes}")

    print("\n" + "-" * 70)
    print("LOTE EN EJECUCIÓN")
    print("-" * 70)

    print(f"{'ID':<15}{'TME':<15}")

    for proceso in lote_actual:
        print(
            f"{proceso['id']:<15}"
            f"{str(proceso['tme']) + ' segundos':<15}"
        )

    print("\n" + "-" * 70)
    print("PROCESO EN EJECUCIÓN")
    print("-" * 70)

    print(f"ID:                 {proceso_actual['id']}")
    print(f"Programador:        {proceso_actual['programador']}")

    print(
        f"Operación:           "
        f"{proceso_actual['operando1']} "
        f"{proceso_actual['operacion']} "
        f"{proceso_actual['operando2']}"
    )

    print(f"TME:                {proceso_actual['tme']} segundos")
    print(f"Tiempo transcurrido: {tiempo_transcurrido} segundos")
    print(f"Tiempo restante:     {tiempo_restante} segundos")

    print("\n" + "-" * 70)
    print("PROCESOS TERMINADOS")
    print("-" * 70)

    if len(terminados) == 0:
        print("Ningún proceso terminado.")
    else:

        for elemento in terminados:

            # Si es una marca de cambio de lote
            if elemento["tipo"] == "marca":
                print(elemento["texto"])

            else:
                proceso = elemento["proceso"]

                print(
                    f"ID: {proceso['id']} | "
                    f"{proceso['operando1']} "
                    f"{proceso['operacion']} "
                    f"{proceso['operando2']} = "
                    f"{proceso['resultado']}"
                )

    print("\n" + "=" * 70)
    print(f"CONTADOR GLOBAL: {contador_global} segundos")
    print("=" * 70)

print("=" * 50)
print("SIMULADOR DE PROCESAMIENTO POR LOTES")
print("=" * 50)

while True:

    try:
        num_procesos = int(
            input("\n¿Cuántos procesos se van a ejecutar?: ")
        )

        if num_procesos > 0:
            break

        else:
            print("El número de procesos debe ser mayor a 0.")

    except ValueError:
        print("Debes ingresar un número entero.")

procesos = []
ids_usados = []

for i in range(num_procesos):

    print("\n" + "=" * 50)
    print(f"PROCESO {i + 1}")
    print("=" * 50)

    while True:

        try:
            id_proceso = int(
                input("ID del proceso: ")
            )

            if id_proceso in ids_usados:
                print(
                    "Ese ID ya existe. "
                    "Ingresa un identificador diferente."
                )

            else:
                ids_usados.append(id_proceso)
                break

        except ValueError:
            print("El ID debe ser un número entero.")

    while True:

        programador = input(
            "Nombre del programador: "
        ).strip()

        if programador != "":
            break

        else:
            print(
                "El nombre del programador "
                "no puede estar vacío."
            )

    while True:

        operacion = input(
            "Operación (+, -, *, /, %, **): "
        )

        if operacion in [
            "+",
            "-",
            "*",
            "/",
            "%",
            "**"
        ]:
            break

        else:
            print("Operación no válida.")

    while True:

        try:
            operando1 = int(
                input("Primer operando: ")
            )

            break

        except ValueError:
            print(
                "El operando debe ser "
                "un número entero."
            )

    while True:

        try:
            operando2 = int(
                input("Segundo operando: ")
            )

            if (
                operacion == "/"
                or operacion == "%"
            ) and operando2 == 0:

                print(
                    "El segundo operando "
                    "no puede ser 0."
                )

            else:
                break

        except ValueError:
            print(
                "El operando debe ser "
                "un número entero."
            )

    while True:

        try:
            tme = int(
                input(
                    "Tiempo Máximo Estimado "
                    "(segundos): "
                )
            )

            if tme > 0:
                break

            else:
                print(
                    "El TME debe ser mayor a 0."
                )

        except ValueError:
            print(
                "El TME debe ser "
                "un número entero."
            )

    proceso = {
        "id": id_proceso,
        "programador": programador,
        "operacion": operacion,
        "operando1": operando1,
        "operando2": operando2,
        "tme": tme,
        "resultado": None
    }

    procesos.append(proceso)

lotes = []

for i in range(0, len(procesos), 4):

    lote = procesos[i:i + 4]

    lotes.append(lote)

limpiar_pantalla()

print("=" * 50)
print("LOTES CREADOS")
print("=" * 50)

for numero_lote, lote in enumerate(
    lotes,
    start=1
):

    print(f"\nLOTE {numero_lote}")

    for proceso in lote:

        print(
            f"ID: {proceso['id']} | "
            f"TME: {proceso['tme']} segundos"
        )

print(
    f"\nTotal de lotes: {len(lotes)}"
)

input(
    "\nPresiona ENTER para iniciar "
    "la simulación..."
)

contador_global = 0

terminados = []

for indice_lote, lote in enumerate(lotes):

    lotes_pendientes = (
        len(lotes)
        - indice_lote
        - 1
    )

    if indice_lote > 0:

        terminados.append({
            "tipo": "marca",
            "texto":
            f"\n----- INICIO DEL LOTE "
            f"{indice_lote + 1} -----"
        })

    for proceso in lote:

        tiempo_transcurrido = 0

        tiempo_restante = proceso["tme"]

        while tiempo_transcurrido < proceso["tme"]:

            mostrar_estado(
                lotes_pendientes,
                lote,
                proceso,
                tiempo_transcurrido,
                tiempo_restante,
                terminados,
                contador_global
            )

            time.sleep(1)

            # Actualizar tiempos
            tiempo_transcurrido += 1

            tiempo_restante -= 1

            contador_global += 1

        proceso["resultado"] = (
            resolver_operacion(proceso)
        )

        terminados.append({
            "tipo": "proceso",
            "proceso": proceso
        })

    terminados.append({
        "tipo": "marca",
        "texto":
        f"----- FIN DEL LOTE "
        f"{indice_lote + 1} -----"
    })

limpiar_pantalla()

print("=" * 70)
print("             TODOS LOS PROCESOS HAN TERMINADO")
print("=" * 70)

print("\nPROCESOS TERMINADOS:\n")

for elemento in terminados:

    if elemento["tipo"] == "marca":

        print(elemento["texto"])

    else:

        proceso = elemento["proceso"]

        print(
            f"ID: {proceso['id']} | "
            f"Programador: {proceso['programador']} | "
            f"{proceso['operando1']} "
            f"{proceso['operacion']} "
            f"{proceso['operando2']} = "
            f"{proceso['resultado']}"
        )

print("\n" + "=" * 70)

print(
    f"CONTADOR GLOBAL FINAL: "
    f"{contador_global} segundos"
)

print("=" * 70)


# PAUSAR EL PROGRAMA
input(
    "\nSimulación terminada. "
    "Presiona ENTER para finalizar..."
)