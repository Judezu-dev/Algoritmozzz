def pares_objetivo(lista, objetivo):
    vistos = set()
    pares_encontrados = set()

    for num in lista:
        complemento = objetivo - num

        # Si el complemento ya fue visto, se ha encontrado un par válido
        if complemento in vistos:
            # Mantener la relación a <= b
            a, b = (num, complemento) if num < complemento else (complemento, num)
            pares_encontrados.add((a, b))

        vistos.add(num)

    # Si no se encontró ningún par
    if not pares_encontrados:
        print("No se encontraron pares que sumen el objetivo.")
        return

    # Ordenar los pares en orden ascendente por 'a' y luego por 'b'
    pares_ordenados = sorted(pares_encontrados)

    # Imprimir cada par con el formato requerido "a, b"
    for a, b in pares_ordenados:
        print(f"{a}, {b}")


# --- FLUJO DE PRUEBA INTERACTIVO ---
while True:
    try:
        print("\n--- BÚSQUEDA DE PARES OBJETIVO ---")
        entrada_lista = input("Ingrese los enteros separados por espacios (o enter vacío para salir): ").strip()

        if not entrada_lista:
            print("Fin del programa.")
            break

        lista = [int(x) for x in entrada_lista.split()]
        objetivo = int(input("Ingrese la suma objetivo: ").strip())

        print(f"\nPares que suman {objetivo}:")
        pares_objetivo(lista, objetivo)

    except ValueError:
        print("Error: Ingrese únicamente números enteros válidos.")
    except EOFError:
        break