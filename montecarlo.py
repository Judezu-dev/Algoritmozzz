import math
import random
import time


def montecarlo_valor_medio(f, a, b, n):
    """Calcula la integral aproximada de f(x) en [a, b] usando N muestras."""
    suma = 0.0
    for _ in range(n):
        x = random.uniform(a, b)
        suma += f(x)

    promedio = suma / n
    return (b - a) * promedio


def evaluar_diferentes_funciones():
    # Definición del diccionario de funciones a evaluar
    # Formato: "Nombre": (función, a, b, valor_exacto)
    funciones = {
        "f(x) = sin(x)  en [0, pi]": (math.sin, 0.0, math.pi, 2.0),
        "f(x) = x^2     en [0, 1]": (lambda x: x**2, 0.0, 1.0, 1 / 3),
        "f(x) = e^x     en [0, 2]": (
            math.exp,
            0.0,
            2.0,
            math.exp(2) - 1,
        ),
    }

    muestras_list = [1_000, 100_000, 10_000_000]

    for nombre, (f, a, b, valor_real) in funciones.items():
        print(f"\n==========================================")
        print(f"Evaluando: {nombre}")
        print(f"Valor real exacto: {valor_real:.8f}")
        print(f"==========================================")

        header = f"{'N Muestras':>12} | {'Aproximación':>15} | {'Error Absoluto':>15} | {'Tiempo (s)':>12}"
        print(header)
        print("-" * len(header))

        for n in muestras_list:
            inicio = time.perf_counter()
            resultado = montecarlo_valor_medio(f, a, b, n)
            fin = time.perf_counter()

            tiempo_empleado = fin - inicio
            error = abs(valor_real - resultado)

            print(
                f"{n:12,d} | {resultado:15.8f} | {error:15.8e} | {tiempo_empleado:12.6f}"
            )


if __name__ == "__main__":
    evaluar_diferentes_funciones()