import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter_ns
import sys

# Aumentar límite de recursión por seguridad
sys.setrecursionlimit(20000)

# =========================================================
# 1. IMPLEMENTACIÓN DE ALGORITMOS DE ORDENAMIENTO
# =========================================================

def bubble_sort(A):
    n = len(A)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if A[j] > A[j + 1]:
                A[j], A[j + 1] = A[j + 1], A[j]
                swapped = True
        if not swapped:
            break

def selection_sort(A):
    n = len(A)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if A[j] < A[min_idx]:
                min_idx = j
        A[i], A[min_idx] = A[min_idx], A[i]

def insertion_sort(A):
    n = len(A)
    for i in range(1, n):
        key = A[i]
        j = i - 1
        while j >= 0 and A[j] > key:
            A[j + 1] = A[j]
            j -= 1
        A[j + 1] = key

def merge_sort(A):
    if len(A) > 1:
        mid = len(A) // 2
        L = A[:mid]
        R = A[mid:]

        merge_sort(L)
        merge_sort(R)

        i = j = k = 0
        while i < len(L) and j < len(R):
            if L[i] <= R[j]:
                A[k] = L[i]
                i += 1
            else:
                A[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            A[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            A[k] = R[j]
            j += 1
            k += 1

def quick_sort(A):
    def _quick_sort(arr, low, high):
        if low < high:
            # Pivote en el punto medio para equilibrar particiones
            mid = (low + high) // 2
            arr[mid], arr[high] = arr[high], arr[mid]
            
            pivot = arr[high]
            i = low - 1
            for j in range(low, high):
                if arr[j] <= pivot:
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            p = i + 1
            
            _quick_sort(arr, low, p - 1)
            _quick_sort(arr, p + 1, high)

    _quick_sort(A, 0, len(A) - 1)

# =========================================================
# 2. MEDISIÓN Y VALIDACIÓN
# =========================================================

def medir_algoritmo(func, vector_base, repeticiones=3):
    v_esperado = np.sort(vector_base)
    tiempos = []

    for _ in range(repeticiones):
        v_copia = vector_base.tolist()  # Copia limpia en lista nativa
        
        t_inicio = perf_counter_ns()
        func(v_copia)
        t_final = perf_counter_ns()
        
        if not np.array_equal(v_copia, v_esperado):
            raise ValueError(f"Error: {func.__name__} no ordenó correctamente.")
            
        tiempos.append((t_final - t_inicio) / 1e6)  # Convertir ns a ms

    return np.median(tiempos)

# =========================================================
# 3. EXPERIMENTACIÓN
# =========================================================

t_inicio_global = perf_counter_ns()

# Rangos diferenciados
n_cuadraticos = np.arange(500, 10001, 500)
n_avanzados = np.arange(5000, 100001, 5000)

t_bubble = np.zeros(len(n_cuadraticos))
t_selection = np.zeros(len(n_cuadraticos))
t_insertion = np.zeros(len(n_cuadraticos))

t_merge = np.zeros(len(n_avanzados))
t_quick = np.zeros(len(n_avanzados))

print("Procesando algoritmos cuadráticos O(n²)...")
for i, n in enumerate(n_cuadraticos):
    base_vector = np.random.randint(0, 100, n, dtype=np.int32)
    reps = 5 if n <= 2000 else 3
    
    t_bubble[i] = medir_algoritmo(bubble_sort, base_vector, repeticiones=reps)
    t_selection[i] = medir_algoritmo(selection_sort, base_vector, repeticiones=reps)
    t_insertion[i] = medir_algoritmo(insertion_sort, base_vector, repeticiones=reps)

print("Procesando algoritmos avanzados O(n log n)...")
for i, n in enumerate(n_avanzados):
    base_vector = np.random.randint(0, 100, n, dtype=np.int32)
    
    t_merge[i] = medir_algoritmo(merge_sort, base_vector, repeticiones=3)
    t_quick[i] = medir_algoritmo(quick_sort, base_vector, repeticiones=3)

# G5: Tipos de entrada
n_g5 = np.arange(100, 1001, 100)
cases = ['aleatorio', 'ordenado', 'inverso']
algos_g5 = ['Insertion', 'Bubble', 'Quick']
times_g5 = {algo: {c: np.zeros(len(n_g5)) for c in cases} for algo in algos_g5}

print("Procesando experimento G5 (Tipos de entrada)...")
for i, n in enumerate(n_g5):
    data_dict = {
        'aleatorio': np.random.randint(0, 100, n, dtype=np.int32),
        'ordenado': np.arange(n, dtype=np.int32),
        'inverso': np.arange(n, 0, -1, dtype=np.int32)
    }
    for c_name, arr in data_dict.items():
        times_g5['Insertion'][c_name][i] = medir_algoritmo(insertion_sort, arr, repeticiones=3)
        times_g5['Bubble'][c_name][i] = medir_algoritmo(bubble_sort, arr, repeticiones=3)
        times_g5['Quick'][c_name][i] = medir_algoritmo(quick_sort, arr, repeticiones=3)

# G6: Rango de valores en QuickSort
n_g6 = np.arange(10000, 100001, 10000)
t_quick_dups = np.zeros(len(n_g6))
t_quick_unique = np.zeros(len(n_g6))

print("Procesando experimento G6 (Duplicados)...")
for i, n in enumerate(n_g6):
    arr_dups = np.random.randint(0, 100, n, dtype=np.int32)
    arr_unique = np.random.randint(0, 1_000_000, n, dtype=np.int32)
    
    t_quick_dups[i] = medir_algoritmo(quick_sort, arr_dups, repeticiones=3)
    t_quick_unique[i] = medir_algoritmo(quick_sort, arr_unique, repeticiones=3)

t_final_global = perf_counter_ns()
print(f"\nTiempo total de ejecución: {(t_final_global - t_inicio_global) / 1e9:.2f} segundos.\n")

# =========================================================
# 4. GENERACIÓN DE GRÁFICOS (G1 - G6)
# =========================================================

# G1
plt.figure(figsize=(8, 5))
plt.plot(n_cuadraticos, t_bubble, "g-o", label="Burbuja — O(n²)")
plt.plot(n_cuadraticos, t_selection, "r-s", label="Selección — O(n²)")
plt.plot(n_cuadraticos, t_insertion, "b-^", label="Inserción — O(n²)")
plt.title("G1: Tiempo vs n (Algoritmos Cuadráticos)")
plt.xlabel("Tamaño del arreglo (n)")
plt.ylabel("Tiempo (ms)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# G2
plt.figure(figsize=(8, 5))
plt.plot(n_avanzados, t_quick, "m-d", label="QuickSort — O(n log n)")
plt.plot(n_avanzados, t_merge, "c-P", label="MergeSort — O(n log n)")
plt.title("G2: Tiempo vs n (Algoritmos Avanzados)")
plt.xlabel("Tamaño del arreglo (n)")
plt.ylabel("Tiempo (ms)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# G3
plt.figure(figsize=(9, 6))
algos_g3 = [
    ("Burbuja", n_cuadraticos, t_bubble, "g"),
    ("Selección", n_cuadraticos, t_selection, "r"),
    ("Inserción", n_cuadraticos, t_insertion, "b"),
    ("MergeSort", n_avanzados, t_merge, "c"),
    ("QuickSort", n_avanzados, t_quick, "m")
]

for name, x_vals, t_vals, color in algos_g3:
    log_x = np.log(x_vals)
    log_t = np.log(t_vals)
    p = np.polyfit(log_x, log_t, 1)
    slope = p[0]
    
    plt.loglog(x_vals, t_vals, color + "o", label=f"{name} (datos)")
    plt.loglog(x_vals, np.exp(np.polyval(p, log_x)), color + "--", 
               label=f"Ajuste {name}: m = {slope:.2f}")

plt.title("G3: Escala Log-Log con Pendiente de Ajuste (Exponente m)")
plt.xlabel("n (Escala Log)")
plt.ylabel("Tiempo en ms (Escala Log)")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# G4
plt.figure(figsize=(8, 5))
plt.plot(n_cuadraticos, t_bubble / (n_cuadraticos ** 2), "g-o", label="Burbuja / n²")
plt.plot(n_cuadraticos, t_selection / (n_cuadraticos ** 2), "r-s", label="Selección / n²")
plt.plot(n_cuadraticos, t_insertion / (n_cuadraticos ** 2), "b-^", label="Inserción / n²")
plt.plot(n_avanzados, t_merge / (n_avanzados * np.log2(n_avanzados)), "c-P", label="MergeSort / (n log₂ n)")
plt.plot(n_avanzados, t_quick / (n_avanzados * np.log2(n_avanzados)), "m-d", label="QuickSort / (n log₂ n)")

plt.title("G4: Tiempo Normalizado t / f(n)")
plt.xlabel("Tamaño del arreglo (n)")
plt.ylabel("Cociente t / f(n)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()

# G5
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
colors_g5 = {'aleatorio': 'black', 'ordenado': 'green', 'inverso': 'red'}
styles_g5 = {'aleatorio': '-', 'ordenado': '--', 'inverso': ':'}
markers_g5 = {'aleatorio': 'o', 'ordenado': 's', 'inverso': '^'}

for idx, algo in enumerate(algos_g5):
    ax = axes[idx]
    for c_name in cases:
        ax.plot(
            n_g5, 
            times_g5[algo][c_name], 
            linestyle=styles_g5[c_name],
            marker=markers_g5[c_name],
            color=colors_g5[c_name], 
            label=c_name.capitalize()
        )
    ax.set_title(f"{algo} Sort")
    ax.set_xlabel("n")
    ax.set_ylabel("Tiempo (ms)")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()

plt.suptitle("G5: Comparación de Casos (Promedio, Mejor y Peor)", fontsize=14)
plt.tight_layout()
plt.show()

# G6
plt.figure(figsize=(8, 5))
plt.plot(n_g6, t_quick_dups, "r-o", label="Rango 0–99 (Muchos duplicados)")
plt.plot(n_g6, t_quick_unique, "b-s", label="Rango 0–1,000,000 (Valores casi únicos)")
plt.title("G6: Efecto de Elementos Duplicados en QuickSort")
plt.xlabel("Tamaño del arreglo (n)")
plt.ylabel("Tiempo (ms)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()