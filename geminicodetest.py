import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from numba import njit
import time

# =============================================================================
# 1. PARÁMETROS FÍSICOS Y CONSTANTES (SISTEMA INTERNACIONAL - SI)
# =============================================================================
K = 8.9875e9        # Constante de Coulomb (N·m²/C²)
MIN_DIST = 0.6      # Distancia mínima entre cargas (metros) para evitar singularidades extremas
GRID_RES = 120      # Resolución de la malla para el cálculo de equipotenciales (120x120)

# =============================================================================
# 2. MOTOR FÍSICO OPTIMIZADO (NUMBA COMPILADO JIT)
# =============================================================================
# [OPTIMIZACIÓN]: @njit(fastmath=True) compila el bucle anidado a lenguaje máquina C
# y permite el uso de instrucciones vectoriales de la CPU (SIMD), acelerando el
# proceso iterativo de O(N*M) órdenes de magnitud frente a Python puro.

@njit(fastmath=True)
def calcular_potencial_numba(x_grid, y_grid, q_x, q_y, q_val, k):
    """Calcula el potencial eléctrico escalar V(x,y) en toda la malla."""
    nx, ny = len(x_grid), len(y_grid)
    V = np.zeros((ny, nx))
    n_charges = len(q_val)
    
    for i in range(ny):
        py = y_grid[i]
        for j in range(nx):
            px = x_grid[j]
            v_total = 0.0
            for c in range(n_charges):
                dx = px - q_x[c]
                dy = py - q_y[c]
                # Distancia Euclidiana
                r = np.sqrt(dx*dx + dy*dy)
                # [FÍSICA]: Distancia de softening. Evita que V tienda a infinito 
                # en el centro geométrico de una partícula puntual.
                if r < 1e-2: r = 1e-2
                # Superposición del potencial de Coulomb: V = sum(k*q/r)
                v_total += k * q_val[c] / r  
            V[i, j] = v_total
    return V

@njit(fastmath=True)
def campo_electrico_punto(px, py, q_x, q_y, q_val, k):
    """Calcula el vector del campo eléctrico E = (Ex, Ey) en un punto (px, py)."""
    ex, ey = 0.0, 0.0
    for c in range(len(q_val)):
        dx = px - q_x[c]
        dy = py - q_y[c]
        r2 = dx*dx + dy*dy + 1e-5
        r3 = r2 * np.sqrt(r2)
        # Vector campo eléctrico E = k * q * r_vector / |r|^3
        ex += k * q_val[c] * dx / r3
        ey += k * q_val[c] * dy / r3
    return ex, ey

@njit(fastmath=True)
def trazar_lineas_campo(q_x, q_y, q_val, num_lines=12, max_steps=140, ds=0.08, k=K):
    """Integra las trayectorias de las líneas de campo desde las cargas positivas."""
    lines_x, lines_y = [], []
    for c in range(len(q_val)):
        if q_val[c] > 0: # Las líneas nacen exclusivamente en cargas positivas
            d_angle = 2.0 * np.pi / num_lines
            for step in range(num_lines):
                angle = step * d_angle
                # Punto de origen (ligeramente desplazado del centro)
                curr_x = q_x[c] + 0.25 * np.cos(angle)
                curr_y = q_y[c] + 0.25 * np.sin(angle)
                lx, ly = [curr_x], [curr_y]
                
                # Integración de Euler siguiendo el vector de campo normalizado
                for _ in range(max_steps):
                    ex, ey = campo_electrico_punto(curr_x, curr_y, q_x, q_y, q_val, k)
                    emag = np.sqrt(ex*ex + ey*ey)
                    if emag < 1e-3: break
                    curr_x += (ex / emag) * ds
                    curr_y += (ey / emag) * ds
                    lx.append(curr_x)
                    ly.append(curr_y)
                    # Cortar si la línea se sale de la pantalla
                    if abs(curr_x) > 5.0 or abs(curr_y) > 5.0: break
                        
                lines_x.append(np.array(lx))
                lines_y.append(np.array(ly))
    return lines_x, lines_y

# =============================================================================
# 3. VERIFICACIÓN DE RENDIMIENTO (CÓDIGO SECUENCIAL LENTO PARA COMPARAR)
# =============================================================================
def calcular_potencial_python_puro(x_grid, y_grid, q_x, q_y, q_val, k):
    nx, ny = len(x_grid), len(y_grid)
    V = np.zeros((ny, nx))
    for i in range(ny):
        py = y_grid[i]
        for j in range(nx):
            px = x_grid[j]
            v_total = 0.0
            for c in range(len(q_val)):
                r = max(((px - q_x[c])**2 + (py - q_y[c])**2)**0.5, 1e-2)
                v_total += k * q_val[c] / r
            V[i, j] = v_total
    return V

# =============================================================================
# 4. CONFIGURACIÓN DEL ENTORNO GRÁFICO (UI/UX)
# =============================================================================
# Estado Inicial
x = np.array([-1.5, 1.5], dtype=np.float64)
y = np.array([0.0, 0.0], dtype=np.float64)
q = np.array([2.0e-9, -2.0e-9], dtype=np.float64) # Dipolo clásico inicial

x_grid = np.linspace(-5, 5, GRID_RES)
y_grid = np.linspace(-5, 5, GRID_RES)

# Calentamiento JIT (Evita latencia en el primer renderizado)
_ = calcular_potencial_numba(x_grid[:5], y_grid[:5], x, y, q, K)

# Estética y Colores de Interfaz
bg_color = "#f4f4f8"  # Gris muy suave para el fondo del programa
plt.rcParams['figure.facecolor'] = bg_color
fig, ax = plt.subplots(figsize=(12, 8))
fig.canvas.manager.set_window_title('Simulador Electromagnético Avanzado')
plt.subplots_adjust(left=0.06, bottom=0.15, right=0.72, top=0.92)

ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
ax.set_facecolor("#ffffff")
ax.set_title("Dinámica de Campos Electrostáticos en Tiempo Real", fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel("Eje Espacial X (m)", fontsize=11, fontweight='semibold')
ax.set_ylabel("Eje Espacial Y (m)", fontsize=11, fontweight='semibold')
ax.grid(True, linestyle=':', alpha=0.6) # Cuadrícula guía suave

# Panel lateral para métricas e información técnica
text_panel = fig.text(0.74, 0.88, "", fontsize=9.5, family='monospace', verticalalignment='top',
                      bbox=dict(boxstyle='round,pad=0.8', facecolor='#eef2f5', alpha=0.9, edgecolor='#b0b0cc'))

# Objetos gráficos para el renderizado
scatter_points = None
contour_set = None
lines_plots = []
charge_labels = []

# Variables de interacción y estado
dragged_idx = None
selected_idx = 0     # Por defecto empezamos con la primera seleccionada
current_input_nc = 2.0 # Valor predeterminado en el cuadro de texto

# =============================================================================
# 5. MOTOR DE RENDERIZADO VISUAL
# =============================================================================
def renderizar_escena(medir_comparativa=False):
    global scatter_points, contour_set, lines_plots, charge_labels
    
    # 1. Limpieza de memoria en el lienzo
    if scatter_points: scatter_points.remove()
    if contour_set: contour_set.remove()
    for lbl in charge_labels: lbl.remove()
    for line in lines_plots: line.remove()
    
    charge_labels.clear()
    lines_plots.clear()
    contour_set = None
    
    if len(q) > 0:
        # Colores (Rojo: Positivas, Azul: Negativas)
        colores = ['#e63946' if val > 0 else '#457b9d' for val in q]
        # Bordes: Destaca en amarillo brillante si está seleccionada
        bordes = ['#ffe066' if i == selected_idx else '#1d3557' for i in range(len(q))]
        grosores = [2.5 if i == selected_idx else 1.0 for i in range(len(q))]
        
        scatter_points = ax.scatter(x, y, c=colores, s=200, edgecolors=bordes, linewidths=grosores, zorder=10)
        
        # Etiquetas numéricas junto a las cargas
        for i in range(len(q)):
            val_nc = q[i] * 1e9
            bg = '#ffe066' if i == selected_idx else '#ffffff'
            txt = ax.text(x[i] + 0.2, y[i] + 0.2, f"{val_nc:+.1f} nC", fontsize=9, 
                          fontweight='bold', zorder=11,
                          bbox=dict(boxstyle='round,pad=0.2', facecolor=bg, alpha=0.85, edgecolor='gray'))
            charge_labels.append(txt)
            
        # 2. Cálculos físicos y perfilado de rendimiento
        t0 = time.perf_counter()
        V = calcular_potencial_numba(x_grid, y_grid, x, y, q, K)
        t_numba = (time.perf_counter() - t0) * 1000.0
        
        t_python = 0.0
        speedup = 1.0
        if medir_comparativa:
            t0 = time.perf_counter()
            _ = calcular_potencial_python_puro(x_grid, y_grid, x, y, q, K)
            t_python = (time.perf_counter() - t0) * 1000.0
            speedup = t_python / t_numba if t_numba > 0 else 1.0

        # 3. Actualización de panel lateral (HUD)
        info_txt = (
            f"=== PANEL TÉCNICO ===\n\n"
            f" [UNIDADES SI]\n"
            f" Espacio   : Metros (m)\n"
            f" Carga (q) : 10⁻⁹ C (nC)\n"
            f" Potencial : Voltios (V)\n"
            f" Campo E   : N/C\n\n"
            f" [PARÁMETROS]\n"
            f" Grilla    : {GRID_RES}x{GRID_RES}\n"
            f" N-Cuerpos : {len(q)}\n\n"
            f" [RENDIMIENTO COMPUTACIONAL]\n"
            f" Ejecución C/SIMD (Numba):\n"
            f"   >> {t_numba:.2f} ms\n"
        )
        if medir_comparativa:
            info_txt += (
                f" Ejecución Python Puro:\n"
                f"   >> {t_python:.2f} ms\n"
                f" -----------------------\n"
                f" Aceleración: {speedup:.1f}x veces\n"
                f" más eficiente."
            )
        else:
            info_txt += "\n (Suelte clic para comparar\n rendimiento.)"
            
        text_panel.set_text(info_txt)

        # 4. Renderizado Científico (Contornos y Streamlines)
        V_clipped = np.clip(V, -35, 35) # Filtro para saturación de color
        if np.max(V_clipped) != np.min(V_clipped):
            contour_set = ax.contour(x_grid, y_grid, V_clipped, levels=36, cmap='RdBu_r', alpha=0.75, linewidths=1.2, zorder=2)
            ax.clabel(contour_set, inline=True, fontsize=7.5, fmt='%1.0f V', levels=contour_set.levels[::4])
        
        lines_x, lines_y = trazar_lineas_campo(x, y, q)
        for lx, ly in zip(lines_x, lines_y):
            lp, = ax.plot(lx, ly, color='#2b2b2b', linestyle='solid', linewidth=0.8, alpha=0.5, zorder=4)
            lines_plots.append(lp)
    else:
        text_panel.set_text("=== PANEL TÉCNICO ===\n\nLienzo vacío.\nAgregue cargas para iniciar.")
        scatter_points = None
        
    fig.canvas.draw_idle()

# =============================================================================
# 6. INTERACCIÓN Y CONTROLES UI
# =============================================================================
def encontrar_carga_cercana(px, py, umbral=0.3):
    if len(x) == 0: return None
    dist_sq = (x - px)**2 + (y - py)**2
    idx_min = np.argmin(dist_sq)
    return idx_min if dist_sq[idx_min] < umbral else None

def agregar_carga_action(event):
    global x, y, q, selected_idx
    # Busca una posición que no colisione al nacer
    px, py = 0, 0
    for _ in range(50):
        px, py = np.random.uniform(-4, 4), np.random.uniform(-4, 4)
        if len(x) == 0 or np.min((x - px)**2 + (y - py)**2) > MIN_DIST**2: break
            
    x = np.append(x, px)
    y = np.append(y, py)
    q = np.append(q, current_input_nc * 1e-9)
    selected_idx = len(q) - 1 # Selecciona la recién creada
    renderizar_escena(medir_comparativa=True)

def eliminar_carga_action(event):
    global x, y, q, selected_idx
    if len(q) > 0:
        idx_borrar = selected_idx if selected_idx is not None else -1
        x = np.delete(x, idx_borrar)
        y = np.delete(y, idx_borrar)
        q = np.delete(q, idx_borrar)
        selected_idx = len(q) - 1 if len(q) > 0 else None
        renderizar_escena(medir_comparativa=True)

def text_submit_action(texto):
    global q, current_input_nc
    try:
        current_input_nc = float(texto)
        if selected_idx is not None and selected_idx < len(q):
            # Si hay una carga seleccionada, aplica el cambio a esa misma
            q[selected_idx] = current_input_nc * 1e-9
            renderizar_escena(medir_comparativa=True)
    except ValueError:
        pass # Ignora entradas no numéricas

# Diseño y creación de los controles inferiores
btn_color, btn_hover = '#ffffff', '#e0e0eb'
ax_txt = plt.axes([0.15, 0.04, 0.15, 0.05])
ax_add = plt.axes([0.32, 0.04, 0.15, 0.05])
ax_del = plt.axes([0.49, 0.04, 0.15, 0.05])

txt_box = TextBox(ax_txt, 'Valor (nC): ', initial=str(current_input_nc))
txt_box.label.set_fontsize(10)
txt_box.label.set_fontweight('bold')

btn_add = Button(ax_add, 'Agregar Carga', color=btn_color, hovercolor='#cce6ff')
btn_add.label.set_fontweight('bold')

btn_del = Button(ax_del, 'Eliminar Carga', color=btn_color, hovercolor='#ffcccc')
btn_del.label.set_fontweight('bold')

txt_box.on_submit(text_submit_action)
btn_add.on_clicked(agregar_carga_action)
btn_del.on_clicked(eliminar_carga_action)

# =============================================================================
# 7. EVENTOS DE RATÓN (ARRASTRE Y COLISIONES)
# =============================================================================
def on_press(event):
    global dragged_idx, selected_idx, current_input_nc
    if event.inaxes != ax: return
    
    idx_clic = encontrar_carga_cercana(event.xdata, event.ydata)
    
    if event.button == 1: # Clic izquierdo selecciona y arrastra
        if idx_clic is not None:
            dragged_idx = idx_clic
            selected_idx = idx_clic
            # Actualiza la caja de texto para reflejar el valor de la seleccionada
            current_input_nc = q[selected_idx] * 1e9
            txt_box.set_val(f"{current_input_nc:.2f}")
            renderizar_escena(medir_comparativa=False)
        else:
            selected_idx = None # Deselecciona si se cliquea en el vacío
            renderizar_escena(medir_comparativa=False)

def on_motion(event):
    global x, y
    if dragged_idx is None or event.inaxes != ax: return
    
    new_x, new_y = event.xdata, event.ydata
    # [FÍSICA]: Algoritmo de resolución de colisiones elásticas simple (3 pasadas)
    for _ in range(3):
        for i in range(len(x)):
            if i != dragged_idx:
                dx = new_x - x[i]
                dy = new_y - y[i]
                dist = np.sqrt(dx**2 + dy**2)
                if dist < MIN_DIST:
                    # Empuja la partícula de forma radial para mantener MIN_DIST
                    angle = np.arctan2(dy, dx)
                    new_x = x[i] + MIN_DIST * np.cos(angle)
                    new_y = y[i] + MIN_DIST * np.sin(angle)
                    
    x[dragged_idx] = new_x
    y[dragged_idx] = new_y
    # Solo renderizamos Numba durante el arrastre para máxima fluidez (FPS)
    renderizar_escena(medir_comparativa=False)

def on_release(event):
    global dragged_idx
    if dragged_idx is not None:
        dragged_idx = None
        # Al soltar, medimos el Python Puro para actualizar el panel de rendimiento
        renderizar_escena(medir_comparativa=True)

fig.canvas.mpl_connect('button_press_event', on_press)
fig.canvas.mpl_connect('motion_notify_event', on_motion)
fig.canvas.mpl_connect('button_release_event', on_release)

# Primera renderización
renderizar_escena(medir_comparativa=True)
plt.show()