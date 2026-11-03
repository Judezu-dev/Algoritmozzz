import numpy as np
import matplotlib.pyplot as plt
import time

# =============================================================================
# 1. FUNCIONES DEL SISTEMA DE LORENZ Y MÉTODO DE RUNGE-KUTTA (Entregable 1)
# =============================================================================

def lorenz_individual(t, estado, sigma, rho, beta):
    """Ecuaciones de Lorenz para un solo punto (array 1D de tamaño 3)."""
    x, y, z = estado
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return np.array([dxdt, dydt, dzdt])

def lorenz_vectorizado(t, estado, sigma, rho, beta):
    """
    Ecuaciones de Lorenz vectorizadas para N trayectorias simultáneas.
    'estado' es un array 2D de forma (N, 3).
    """
    x = estado[:, 0]
    y = estado[:, 1]
    z = estado[:, 2]
    
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    
    return np.column_stack((dxdt, dydt, dzdt))

def rk4_step(f, t, estado, h, *args):
    """Implementa un paso del método de Runge-Kutta de orden 4."""
    k1 = f(t, estado, *args)
    k2 = f(t + h/2, estado + (h/2)*k1, *args)
    k3 = f(t + h/2, estado + (h/2)*k2, *args)
    k4 = f(t + h, estado + h*k3, *args)
    return estado + (h/6) * (k1 + 2*k2 + 2*k3 + k4)


# =============================================================================
# 2. FUNCIONES DE INTEGRACIÓN (Bucle vs Vectorización para Punto Extra)
# =============================================================================

def integrar_bucle(puntos_iniciales, t_vals, h, params):
    """Integra iterando trayectoria por trayectoria (bucle for anidado)."""
    n_puntos = len(puntos_iniciales)
    n_pasos = len(t_vals)
    trayectorias = np.zeros((n_puntos, n_pasos, 3))
    
    for i in range(n_puntos):
        estado_actual = np.copy(puntos_iniciales[i])
        trayectorias[i, 0] = estado_actual
        for j in range(1, n_pasos):
            estado_actual = rk4_step(lorenz_individual, t_vals[j-1], estado_actual, h, *params)
            trayectorias[i, j] = estado_actual
            
    return trayectorias

def integrar_vectorizado(puntos_iniciales, t_vals, h, params):
    """Integra todas las trayectorias simultáneamente usando operaciones vectorizadas."""
    n_puntos = len(puntos_iniciales)
    n_pasos = len(t_vals)
    
    # trayectorias_v guardará los datos temporalmente con forma (n_pasos, n_puntos, 3)
    trayectorias_v = np.zeros((n_pasos, n_puntos, 3))
    
    estado_actual = np.copy(puntos_iniciales)
    trayectorias_v[0] = estado_actual
    
    for j in range(1, n_pasos):
        estado_actual = rk4_step(lorenz_vectorizado, t_vals[j-1], estado_actual, h, *params)
        trayectorias_v[j] = estado_actual
        
    # Transponemos para retornar con la misma forma (n_puntos, n_pasos, 3) que la versión original
    return trayectorias_v.transpose(1, 0, 2)


def graficar_trayectorias(trayectorias, titulo, parametros):
    """Genera la gráfica 3D de las trayectorias calculadas."""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Graficar cada una de las 10 trayectorias
    for i in range(trayectorias.shape[0]):
        ax.plot(trayectorias[i, :, 0], trayectorias[i, :, 1], trayectorias[i, :, 2], lw=0.5, alpha=0.8)
        
    ax.set_title(f"{titulo}\n(σ={parametros[0]}, ρ={parametros[1]}, β={parametros[2]:.2f})", pad=15)
    ax.set_xlabel("Eje X")
    ax.set_ylabel("Eje Y")
    ax.set_zlabel("Eje Z")
    plt.tight_layout()
    plt.show()


# =============================================================================
# 3. CONFIGURACIÓN DEL EXPERIMENTO
# =============================================================================

# Definición del dominio temporal
t_inicio = 0
t_fin = 100
h = 0.01
t_vals = np.arange(t_inicio, t_fin + h, h)

# Generación de los 10 puntos iniciales cercanos entre sí (distancia del orden de 1e-3)
puntos_iniciales = np.zeros((10, 3))
punto_base = np.array([5.0, 5.0, 5.0])
puntos_iniciales[0] = punto_base

for i in range(1, 10):
    # Se añade una perturbación minúscula determinista en cada eje a partir del punto base
    perturbacion = np.array([i * 1e-3, (10 - i) * 1e-3, (i % 2) * 1e-3])
    puntos_iniciales[i] = punto_base + perturbacion

# Definición de los distintos sets de parámetros (Base + 3 Variaciones)
parametros_base = (10.0, 28.0, 8.0/3.0)
variacion_1 = (10.0, 14.0, 8.0/3.0)
variacion_2 = (14.0, 28.0, 8.0/3.0)
variacion_3 = (10.0, 28.0, 4.0)

escenarios = [
    ("Escenario Base (Caos Clásico)", parametros_base),
    ("Variación 1 (Puntos Fijos Estables)", variacion_1),
    ("Variación 2 (Cambio en σ - Geometría alterada)", variacion_2),
    ("Variación 3 (Cambio en β - Mayor disipación)", variacion_3)
]


# =============================================================================
# 4. EJECUCIÓN, COMPARATIVA DE TIEMPOS (Entregable 5) Y GRAFICACIÓN
# =============================================================================

print("Integrando trayectorias base mediante bucle for...")
inicio_bucle = time.time()
trayectorias_base_bucle = integrar_bucle(puntos_iniciales, t_vals, h, parametros_base)
fin_bucle = time.time()
tiempo_bucle = fin_bucle - inicio_bucle

print("Integrando trayectorias base vectorizadas con NumPy...")
inicio_vect = time.time()
trayectorias_base_vect = integrar_vectorizado(puntos_iniciales, t_vals, h, parametros_base)
fin_vect = time.time()
tiempo_vect = fin_vect - inicio_vect

print("\n--- COMPARATIVA DE TIEMPOS DE CÓMPUTO (Punto Extra) ---")
print(f"Tiempo con bucles anidados: {tiempo_bucle:.4f} segundos")
print(f"Tiempo con vectorización (NumPy): {tiempo_vect:.4f} segundos")
print(f"Aceleración obtenida: {tiempo_bucle / tiempo_vect:.2f}x veces más rápido.\n")


print("Generando gráficas para el entregable 2 y 3. Cierre cada ventana para ver la siguiente...")
# Graficamos el escenario base (Entregable 2)
graficar_trayectorias(trayectorias_base_vect, escenarios[0][0], escenarios[0][1])

# Simulamos y graficamos las 3 variaciones (Entregable 3)
for titulo, params in escenarios[1:]:
    trayectorias_var = integrar_vectorizado(puntos_iniciales, t_vals, h, params)
    graficar_trayectorias(trayectorias_var, titulo, params)

print("Simulación finalizada.")