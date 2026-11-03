import math
import numpy as np
import matplotlib.pyplot as plt


def fijar_semilla():
    """Permite fijar opcionalmente la semilla del generador aleatorio."""
    respuesta = input("¿Desea fijar una semilla para reproducibilidad? (s/n): ").strip().lower()
    if respuesta == 's':
        try:
            semilla = int(input("Ingrese el número de semilla (entero): ").strip())
            np.random.seed(semilla)
            print(f"Semilla fijada en {semilla}.\n")
        except ValueError:
            print("Entrada inválida. Se continuará sin fijar semilla.\n")


def procesar_vector(x, y, contador_vector):
    u = np.array([x, y], dtype=float)

    # 1. Generar dos ángulos aleatorios en [0, 2π) y sus vectores unitarios v1, v2
    theta1, theta2 = np.random.uniform(0, 2 * np.pi, size=2)
    
    v1_hat = np.array([np.cos(theta1), np.sin(theta1)])
    v2_hat = np.array([np.cos(theta2), np.sin(theta2)])

    # 2. Calcular las proyecciones: p_i = (u · v_i_hat) * v_i_hat
    p1 = np.dot(u, v1_hat) * v1_hat
    p2 = np.dot(u, v2_hat) * v2_hat

    # Convertir ángulos a grados
    theta1_deg = np.degrees(theta1)
    theta2_deg = np.degrees(theta2)

    # 3. Imprimir tabla de datos redondeada a 3 decimales
    print("\n" + "=" * 65)
    print(f"RESULTADOS PARA EL VECTOR #{contador_vector}: u = ({u[0]:.3f}, {u[1]:.3f})")
    print("=" * 65)
    print(f"{'Propiedad / Componente':<25} | {'Valor 1':<15} | {'Valor 2':<15}")
    print("-" * 65)
    print(f"{'Ángulo (grados)':<25} | {theta1_deg:<15.3f} | {theta2_deg:<15.3f}")
    print(f"{'Vector unitario v_i':<25} | ({v1_hat[0]:.3f}, {v1_hat[1]:.3f}) | ({v2_hat[0]:.3f}, {v2_hat[1]:.3f})")
    print(f"{'Proyección p_i':<25} | ({p1[0]:.3f}, {p1[1]:.3f}) | ({p2[0]:.3f}, {p2[1]:.3f})")
    print("=" * 65 + "\n")

    # 4. Graficar el vector original y sus proyecciones
    graficar_vectores(u, p1, p2, theta1_deg, theta2_deg, contador_vector)


def graficar_vectores(u, p1, p2, theta1_deg, theta2_deg, contador_vector):
    fig, ax = plt.subplots(figsize=(7, 7))

    # Vector u original (negro, continuo)
    ax.quiver(
        0,
        0,
        u[0],
        u[1],
        angles='xy',
        scale_units='xy',
        scale=1,
        color='black',
        label=f'u = ({u[0]:.2f}, {u[1]:.2f})',
        zorder=3,
    )

    # Proyección p1 (azul)
    ax.quiver(
        0,
        0,
        p1[0],
        p1[1],
        angles='xy',
        scale_units='xy',
        scale=1,
        color='blue',
        label=f'p1 (θ1={theta1_deg:.1f}°)',
        zorder=2,
    )

    # Proyección p2 (roja)
    ax.quiver(
        0,
        0,
        p2[0],
        p2[1],
        angles='xy',
        scale_units='xy',
        scale=1,
        color='red',
        label=f'p2 (θ2={theta2_deg:.1f}°)',
        zorder=2,
    )

    # Líneas auxiliares ortogonales desde u hacia p1 y p2 (líneas punteadas normales)
    ax.plot([u[0], p1[0]], [u[1], p1[1]], color='blue', linestyle=':', alpha=0.6)
    ax.plot([u[0], p2[0]], [u[1], p2[1]], color='red', linestyle=':', alpha=0.6)

    # Ajuste de límites de ejes
    todos_x = [0, u[0], p1[0], p2[0]]
    todos_y = [0, u[1], p1[1], p2[1]]
    max_lim = max(max(np.abs(todos_x)), max(np.abs(todos_y)), 1.0) * 1.3

    ax.set_xlim(-max_lim, max_lim)
    ax.set_ylim(-max_lim, max_lim)

    ax.set_aspect('equal')
    ax.axhline(0, color='gray', linewidth=0.8)
    ax.axvline(0, color='gray', linewidth=0.8)
    ax.grid(True, linestyle=':', alpha=0.7)

    ax.set_title(
        f'Proyección Ortogonal del Vector #{contador_vector}',
        fontsize=12,
        pad=10,
    )
    ax.set_xlabel('Componente X')
    ax.set_ylabel('Componente Y')
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.show()


# --- FLUJO PRINCIPAL ---
fijar_semilla()

contador = 1
while True:
    try:
        print(f"--- Vector #{contador} ---")
        x_in = float(input("Ingrese la componente x (o 0 para salir): ").strip())
        y_in = float(input("Ingrese la componente y (o 0 para salir): ").strip())

        # Condición de parada: Vector nulo (0, 0)
        if x_in == 0 and y_in == 0:
            print("\nVector nulo (0, 0) detectado. Fin del programa.")
            break

        procesar_vector(x_in, y_in, contador)
        contador += 1

    except ValueError:
        print("Entrada no válida. Asegúrese de ingresar números reales.\n")