import time
from numba import njit

# 1. Versión en Python nativo
def calcular_pi_python(numero_terminos):
    suma = 0.0
    i = 0
    while i <= numero_terminos:
        suma = suma + ((-1)**i) / (2*i + 1)
        i = i + 1
    return suma * 4

# 2. Versión optimizada con Numba
@njit
def calcular_pi_numba(numero_terminos):
    suma = 0.0
    i = 0
    while i <= numero_terminos:
        suma = suma + ((-1)**i) / (2*i + 1)
        i = i + 1
    return suma * 4

# --- Entrada de datos ---
numero_terminos = int(input("Ingrese el número de términos de la serie: "))

# --- Calentamiento de Numba (Compilación JIT) ---
_ = calcular_pi_numba(10)

# --- Medición: Python Nativo ---
inicio_py = time.perf_counter()
res_py = calcular_pi_python(numero_terminos)
fin_py = time.perf_counter()
tiempo_py = fin_py - inicio_py

# --- Medición: Numba ---
inicio_nb = time.perf_counter()
res_nb = calcular_pi_numba(numero_terminos)
fin_nb = time.perf_counter()
tiempo_nb = fin_nb - inicio_nb

# --- Cálculo de Aceleración (Speedup) ---
speedup = tiempo_py / tiempo_nb if tiempo_nb > 0 else 0

# --- Resultados ---
print("\n" + "="*45)
print(f"Resultado Pi (Python): {res_py}")
print(f"Resultado Pi (Numba):  {res_nb}")
print("="*45)
print(f"Tiempo Python nativo: {tiempo_py:.6f} segundos")
print(f"Tiempo con Numba:     {tiempo_nb:.6f} segundos")
print(f"Aceleración (Speedup): {speedup:.2f}x más rápido")
print("="*45)