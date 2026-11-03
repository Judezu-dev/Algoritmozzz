def g(y):
    if y < 0:
        return 0.0
    elif y > 1:
        return 1.0
    return y


def evaluar_polinomio(coeficientes, x):
    resultado = 0.0
    for coef in coeficientes:
        resultado = resultado * x + coef
    return resultado


while True:
    try:
        print("\n--- NUEVO CASO DE PRUEBA ---")
        grado_in = input("Ingrese el grado del polinomio (0 a 19, o 20 para salir): ").strip()
        if not grado_in:
            continue

        grado = int(grado_in)

        # Condición de parada (grado 20)
        if grado == 20:
            print("Fin del programa.")
            break

        if not (0 <= grado <= 19):
            print("Grado fuera de rango. Debe estar entre 0 y 19.")
            continue

        # Lectura individual de los n + 1 coeficientes
        coeficientes = []
        print(f"Ingrese los {grado + 1} coeficientes en orden decreciente de grado:")
        for i in range(grado, -1, -1):
            coef = int(input(f"  Coeficiente de x^{i}: ").strip())
            coeficientes.append(coef)

        # Lectura individual del número de rectángulos
        num_rectangulos = int(input("Ingrese el número de rectángulos a usar: ").strip())

        # Suma de Riemann
        area_cain = 0.0
        ancho = 1.0 / num_rectangulos

        for i in range(num_rectangulos):
            x_i = i / num_rectangulos
            y_i = evaluar_polinomio(coeficientes, x_i)
            area_cain += ancho * g(y_i)

        area_abel = 1.0 - area_cain
        diferencia = abs(area_cain - area_abel)

        print("\n--> Resultado:", end=" ")
        if diferencia <= 0.001:
            print("JUSTO")
        elif area_cain > area_abel:
            print("CAIN")
        else:
            print("ABEL")

    except ValueError:
        print("Error: Entrada inválida. Asegúrese de ingresar números enteros.")
    except EOFError:
        break