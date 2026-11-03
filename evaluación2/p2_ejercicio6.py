def es_triangular(matriz, n):
    """
    Verifica si una matriz de tamaño n x n es triangular.
    Retorna True si es triangular superior, triangular inferior o ambas (diagonal).
    """
    if n == 1:
        return True

    es_triangular_superior = True
    es_triangular_inferior = True

    for i in range(n):
        for j in range(n):
            val = matriz[i][j]
            # Elementos por debajo de la diagonal principal (i > j)
            if i > j and val != 0:
                es_triangular_superior = False
            # Elementos por encima de la diagonal principal (i < j)
            if i < j and val != 0:
                es_triangular_inferior = False

    return es_triangular_superior or es_triangular_inferior


while True:
    try:
        print("\n--- EVALUACIÓN DE MATRIZ TRIANGULAR ---")
        entrada_n = input("Ingrese el tamaño n de la matriz (0 < n <= 50, o 0 para salir): ").strip()
        
        if not entrada_n:
            continue

        n = int(entrada_n)

        # Condición de parada
        if n == 0:
            print("Fin del programa.")
            break

        if not (1 <= n <= 50):
            print("Error: El tamaño debe estar entre 1 y 50.")
            continue

        matriz = []
        print(f"\nIngrese los {n} elementos de cada fila separados por espacios:")
        
        i = 0
        while i < n:
            entrada_fila = input(f"  Fila {i + 1}: ").strip().split()
            
            # Validar que se ingresen exactamente 'n' elementos por fila
            if len(entrada_fila) != n:
                print(f"  --> Error: Debe ingresar exactamente {n} números. Intente de nuevo esta fila.")
                continue

            try:
                fila = [int(x) for x in entrada_fila]
                matriz.append(fila)
                i += 1
            except ValueError:
                print("  --> Error: Todos los elementos deben ser números enteros. Intente de nuevo esta fila.")

        # Mostrar matriz ingresada
        print("\nMatriz ingresada:")
        for fila in matriz:
            print(" ", fila)

        # Evaluar resultado
        resultado = "SI" if es_triangular(matriz, n) else "NO"
        print(f"\n¿Es triangular?: {resultado}")

    except ValueError:
        print("Error: Ingrese un tamaño válido (entero).")
    except EOFError:
        break