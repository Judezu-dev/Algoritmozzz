"""Módulo paralelo (OpenMP/TBB vía Numba prange) del simulador electrostático 2D.

Reexporta el kernel paralelo y el control de hilos de `simulador_electrico.py`.
"""
from time import perf_counter
import numpy as np
from numba import set_num_threads, get_num_threads

from simulador_electrico import (
    K,
    EPS,
    MASA,
    potencial_paralelo,
    potencial_serial,
)

__all__ = [
    'K',
    'EPS',
    'MASA',
    'potencial_paralelo',
    'set_num_threads',
    'get_num_threads',
]


if __name__ == '__main__':
    eje = np.linspace(-5.0, 5.0, 200)
    pos = np.array([[-1.4, 0.0], [1.4, 0.0]])
    q = np.array([2e-9, -2e-9])
    ref = np.empty((len(eje), len(eje)))
    par = np.empty_like(ref)

    potencial_serial(eje, pos, q, ref)
    potencial_paralelo(eje, pos, q, par)  # Calentamiento JIT

    t0 = perf_counter()
    potencial_paralelo(eje, pos, q, par)
    dt_ms = (perf_counter() - t0) * 1000.0
    coincide = np.allclose(ref, par, rtol=1e-12, atol=1e-10)
    err_max = float(np.max(np.abs(ref - par)))
    print(
        f'Verificación paralelo OK ({get_num_threads()} hilos) | '
        f'200x200: {dt_ms:.3f} ms | allclose={coincide} | err_max={err_max:.2e} V'
    )