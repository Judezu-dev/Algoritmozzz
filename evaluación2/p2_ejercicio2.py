import math


def limpiar_cadena(texto):
    """Elimina caracteres duplicados manteniendo únicamente su primera aparición."""
    vistos = set()
    resultado = []
    for c in texto:
        if c not in vistos:
            vistos.add(c)
            resultado.append(c)
    return "".join(resultado)


def generar_ordenamientos(caracteres, n, ruta_actual, usados, resultados):
    """Genera todas las variaciones de tamaño n en orden lexicográfico usando backtracking."""
    if len(ruta_actual) == n:
        resultados.append("".join(ruta_actual))
        return

    for i in range(len(caracteres)):
        if not usados[i]:
            usados[i] = True
            ruta_actual.append(caracteres[i])

            generar_ordenamientos(caracteres, n, ruta_actual, usados, resultados)

            # Backtracking
            ruta_actual.pop()
            usados[i] = False


def main():
    try:
        cadena_entrada = input().strip()
        n = int(input().strip())

        # 1. Limpieza de caracteres repetidos (conserva la primera aparición)
        cadena_limpia = limpiar_cadena(cadena_entrada)

        # 2. Ordenamiento lexicográfico del conjunto de M caracteres distintos
        caracteres_unicos = sorted(list(cadena_limpia))
        m = len(caracteres_unicos)

        # Validación del rango de N
        if not (1 <= n <= m):
            print(f"Error: N debe estar entre 1 y M ({m}).")
            return

        # 3. Generación de ordenamientos
        resultados = []
        usados = [False] * m
        generar_ordenamientos(caracteres_unicos, n, [], usados, resultados)

        # 4. Imprimir cada ordenamiento
        for ordenamiento in resultados:
            print(ordenamiento)

        # 5. Verificación de la cantidad de líneas generadas mediante la fórmula
        lineas_generadas = len(resultados)
        esperado_formula = math.perm(m, n)  # M! / (M - N)!

        print(f"\nLíneas generadas: {lineas_generadas}")
        print(f"Valor esperado por fórmula: {esperado_formula}")
        print(f"Coincide: {lineas_generadas == esperado_formula}")

    except (EOFError, ValueError):
        pass


main()