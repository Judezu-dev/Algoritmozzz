# Simulación Serial y Paralela de Interacción Electrostática 2D

Proyecto final — Cálculo Científico (2026-2), Universidad Industrial de Santander (UIS).

## Descripción del modelo
Simulación en el plano z = 0 de N cargas puntuales bajo ley de Coulomb regularizada:

    V(x, y) = sum( k * q_i / sqrt(r_i^2 + eps^2) ),   con eps = 0.18 m

Utiliza integración simpléctica Velocity-Verlet para la dinámica de partículas y cálculo de curvas equipotenciales y líneas de campo eléctrico en unidades del Sistema Internacional (SI).

La parte computacionalmente dominante (evaluación del potencial escalar V(x, y) sobre la malla de tamaño Ng x Ng) está implementada en versión serial (`potencial_serial`) y paralela (`potencial_paralelo` mediante `numba.prange`).

## Estructura del proyecto
- `simulador_electrico.py`: Aplicación principal interactiva (física, mediciones e interfaz Pygame).
- `serial.py`: Módulo de referencia con las rutinas secuenciales.
- `paralelo.py`: Módulo con el kernel paralelo y control de hilos.
- `medir.py`: Script de perfilado, verificación numérica, medición de tiempos (CSV) y generación de todas las figuras.
- `requirements.txt`: Dependencias de Python necesarias.

## Requisitos e instalación
Probado en Python 3.10+ sobre Linux. Se recomienda usar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt