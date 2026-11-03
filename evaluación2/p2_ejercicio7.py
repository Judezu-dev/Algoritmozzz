def entero_a_romano(numero):
    """Convierte un entero entre 1 y 3999 a su representación en números romanos."""
    valores = [
        (1000, "M"),
        (900, "CM"),
        (500, "D"),
        (400, "CD"),
        (100, "C"),
        (90, "XC"),
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    romano = []
    for valor, simbolo in valores:
        while numero >= valor:
            romano.append(simbolo)
            numero -= valor

    return "".join(romano)


while True:
    try:
        print("\n--- CONVERSOR A NÚMEROS ROMANOS ---")
        entrada = input("Ingrese un número entero positivo (1 a 3999, o 0 para salir): ").strip()

        if not entrada:
            continue

        numero = int(entrada)

        # Condición de parada
        if numero == 0:
            print("Programa finalizado.")
            break

        # Validación del rango permitido
        if not (1 <= numero <= 3999):
            print("Error: El número debe estar en el rango de 1 a 3999.")
            continue

        # Conversión e impresión del resultado
        resultado = entero_a_romano(numero)
        print(f"--> Representación romana: {resultado}")

    except ValueError:
        print("Error: Entrada inválida. Debe ingresar únicamente números enteros.")
    except EOFError:
        break