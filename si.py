import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from numba import jit

# ==============================================================================
# 1. NÚCLEO DE CÁLCULO FÍSICO (Numba JIT)
# ==============================================================================
K_COULOMB = 8.9875517923e9  # Constante electrostática (N m^2 / C^2)

@jit(nopython=True)
def calcular_campo_potencial(X, Y, cargas):
    """
    Calcula el campo eléctrico (Ex, Ey) y el potencial V en una malla 2D.
    cargas: Array de dimensiones Nx3 -> [magnitud (C), pos_x (m), pos_y (m)]
    """
    filas, cols = X.shape
    Ex = np.zeros((filas, cols))
    Ey = np.zeros((filas, cols))
    V = np.zeros((filas, cols))
    
    for i in range(filas):
        for j in range(cols):
            x = X[i, j]
            y = Y[i, j]
            
            for c in range(len(cargas)):
                q = cargas[c, 0]
                cx = cargas[c, 1]
                cy = cargas[c, 2]
                
                dx = x - cx
                dy = y - cy
                r2 = dx**2 + dy**2
                r = np.sqrt(r2)
                
                # Prevenir división por cero / singularidad sobre la carga
                if r > 0.01:
                    V[i, j] += K_COULOMB * q / r
                    
                    E_mag = K_COULOMB * q / (r2 * r)
                    Ex[i, j] += E_mag * dx
                    Ey[i, j] += E_mag * dy
                    
    return Ex, Ey, V

# ==============================================================================
# 2. CONFIGURACIÓN DEL SISTEMA Y MALLA ESPACIAL
# ==============================================================================
# Configuración inicial de cargas puntual: [q (Coulombs), x (m), y (m)]
cargas = np.array([
    [1e-6, -1.0, 0.0],  # Carga positiva (+1 µC)
    [-1e-6, 1.0, 0.0]   # Carga negativa (-1 µC)
])

# Malla métrica 2D (-3m a 3m)
x = np.linspace(-3, 3, 100)
y = np.linspace(-3, 3, 100)
X, Y = np.meshgrid(x, y)

# Cálculo inicial del mapa escalar y vectorial
Ex, Ey, V = calcular_campo_potencial(X, Y, cargas)

# ==============================================================================
# 3. INTERFAZ GRÁFICA INTERACTIVA (Matplotlib)
# ==============================================================================
fig, ax = plt.subplots(figsize=(9, 7))
plt.subplots_adjust(bottom=0.18)
ax.set_title("Simulador Electrostático 2D — Mallas Equipotenciales y Líneas de Campo")
ax.set_xlabel("Eje X (m)")
ax.set_ylabel("Eje Y (m)")
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.5)

# Renderizado de superficies equipotenciales
contornos = ax.contour(X, Y, V, levels=25, cmap='coolwarm', alpha=0.7)
plt.colorbar(contornos, ax=ax, label="Potencial Eléctrico V (Volts)")

# Renderizado de líneas de campo eléctrico
ax.streamplot(X, Y, Ex, Ey, color='black', linewidth=1, density=1.4, arrowstyle='->', arrowsize=1.5)

# Dibujo de cargas puntuales
for q, cx, cy in cargas:
    color = 'red' if q > 0 else 'blue'
    ax.plot(cx, cy, marker='o', color=color, markersize=10, markeredgecolor='black', zorder=5)

# Cuadro flotante para mediciones
anotacion = ax.annotate("", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="gray", lw=1.5),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
anotacion.set_visible(False)

# Evento: Medición al hacer clic sobre la gráfica
def al_hacer_clic(event):
    if event.inaxes == ax:
        cx, cy = event.xdata, event.ydata
        
        # Evaluación puntual directa
        X_pt = np.array([[cx]])
        Y_pt = np.array([[cy]])
        ex_pt, ey_pt, v_pt = calcular_campo_potencial(X_pt, Y_pt, cargas)
        
        magnitud_E = np.sqrt(ex_pt[0, 0]**2 + ey_pt[0, 0]**2)
        
        texto = f"Pos: ({cx:.2f}, {cy:.2f}) m\nPotencial V: {v_pt[0, 0]:.2e} V\nCampo |E|: {magnitud_E:.2e} V/m"
        anotacion.xy = (cx, cy)
        anotacion.set_text(texto)
        anotacion.set_visible(True)
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('button_press_event', al_hacer_clic)

# Botón GUI: Limpiar medición
ax_boton = plt.axes([0.38, 0.04, 0.24, 0.06])
boton = Button(ax_boton, 'Ocultar Medición')

def ocultar_medicion(event):
    anotacion.set_visible(False)
    fig.canvas.draw_idle()

boton.on_clicked(ocultar_medicion)

# ==============================================================================
# 4. EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    plt.show()