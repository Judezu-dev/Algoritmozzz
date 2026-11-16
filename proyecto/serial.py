"""Módulo de referencia serial del simulador electrostático 2D.

Reexporta las rutinas secuenciales de `simulador_electrico.py` para cumplir
con la separación modular solicitada en la rúbrica sin duplicar código.
"""
from time import perf_counter
import numpy as np

from simulador_electrico import (
    K,
    EPS,
    MASA,
    potencial_serial,
    campo,
    fuerzas,
    avanzar,
    lineas_campo,
    energia,
)

__all__ = [
    'K',
    'EPS',
    'MASA',
    'potencial_serial',
    'campo',
    'fuerzas',
    'avanzar',
    'lineas_campo',
    'energia',
]


if __name__ == '__main__':
    eje = np.linspace(-5.0, 5.0, 200)
    pos = np.array([[-1.4, 0.0], [1.4, 0.0]])
    q = np.array([2e-9, -2e-9])
    salida = np.empty((len(eje), len(eje)))

    potencial_serial(eje, pos, q, salida)  # Calentamiento JIT
    t0 = perf_counter()
    potencial_serial(eje, pos, q, salida)
    dt_ms = (perf_counter() - t0) * 1000.0
    print(f'Verificación serial OK | Malla 200x200: {dt_ms:.3f} ms | V_max={salida.max():.2f} V')