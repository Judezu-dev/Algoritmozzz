"""Script maestro de perfilado, verificación, benchmarks y regeneración de figuras.

Ejecuta sin modificar `simulador_electrico.py`:
1. Perfilado comparativo de las funciones físicas (justificación de paralelización).
2. Experimentos de tiempo, speedup y eficiencia variando hilos y tamaños de malla.
3. Verificación numérica serial vs. paralelo (tolerancia float64).
4. Generación de CSVs y figuras vectoriales SVG de alta calidad para informe y póster.
"""
import argparse
import csv
import math
import os
import subprocess
from pathlib import Path
from time import perf_counter

import contourpy
import numpy as np
from numba import config, set_num_threads

import simulador_electrico as sim


def detectar_nucleos_fisicos() -> int:
    """Detecta el número de núcleos físicos en Linux o usa respaldo seguro."""
    cpuinfo = Path('/proc/cpuinfo')
    if cpuinfo.exists():
        pares = set()
        for bloque in cpuinfo.read_text(encoding='utf-8', errors='ignore').split('\n\n'):
            campos = {}
            for linea in bloque.splitlines():
                if ':' in linea:
                    k, v = linea.split(':', 1)
                    campos[k.strip()] = v.strip()
            if 'physical id' in campos and 'core id' in campos:
                pares.add((campos['physical id'], campos['core id']))
        if pares:
            return len(pares)
    try:
        salida = subprocess.check_output(['lscpu', '-p=CORE,SOCKET'], text=True)
        pares = {
            linea.strip()
            for linea in salida.splitlines()
            if linea and not linea.startswith('#')
        }
        if pares:
            return len(pares)
    except Exception:
        pass
    return max(1, (os.cpu_count() or 2) // 2)


def secuencia_hilos(max_hilos: int) -> list[int]:
    """Construye 1, 2, 4, ... hasta max_hilos sin exceder el límite de Numba."""
    limite = min(max_hilos, config.NUMBA_NUM_THREADS)
    hilos = [1]
    while hilos[-1] * 2 <= limite:
        hilos.append(hilos[-1] * 2)
    if hilos[-1] != limite:
        hilos.append(limite)
    return sorted(set(hilos))


def perfilar_componentes(malla: int, repeticiones: int, carpeta: Path) -> list[dict]:
    """Mide el peso relativo de cada rutina física para justificar qué se paraleliza."""
    rng = np.random.default_rng(2026)
    pos = rng.uniform(-3.0, 3.0, (32, 2))
    vel = np.zeros_like(pos)
    q = rng.choice(np.array([-2e-9, 2e-9]), 32)
    eje = np.linspace(-5.0, 5.0, malla)
    v_out = np.empty((malla, malla))
    dt = 1e-4

    # Calentamiento JIT
    sim.potencial_serial(eje, pos, q, v_out)
    sim.avanzar(pos.copy(), vel.copy(), q, dt, 96)
    sim.lineas_campo(pos, q, 5.0)
    sim.energia(pos, vel, q)

    tareas = [
        ('potencial_serial (malla V)', lambda: sim.potencial_serial(eje, pos, q, v_out)),
        ('avanzar (Verlet 96 pasos)', lambda: sim.avanzar(pos.copy(), vel.copy(), q, dt, 96)),
        ('lineas_campo (32 curvas RK2)', lambda: sim.lineas_campo(pos, q, 5.0)),
        ('energia (Ec + U)', lambda: sim.energia(pos, vel, q)),
    ]

    resultados = []
    for nombre, fn in tareas:
        muestras = []
        for _ in range(repeticiones):
            t0 = perf_counter()
            fn()
            muestras.append((perf_counter() - t0) * 1000.0)
        med = float(np.median(muestras))
        iqr = float(np.percentile(muestras, 75) - np.percentile(muestras, 25))
        resultados.append({'componente': nombre, 'mediana_ms': med, 'iqr_ms': iqr})

    total_ms = sum(r['mediana_ms'] for r in resultados)
    for r in resultados:
        r['porcentaje'] = 100.0 * r['mediana_ms'] / max(total_ms, 1e-30)

    sim.guardar_csv(carpeta / 'perfilado.csv', resultados)
    return resultados


def verificar_consistencia(mallas: list[int], hilos: list[int], carpeta: Path) -> list[dict]:
    """Genera tabla explícita de verificación numérica serial vs. paralelo."""
    rng = np.random.default_rng(2026)
    pos = rng.uniform(-3.0, 3.0, (32, 2))
    q = rng.choice(np.array([-2e-9, 2e-9]), 32)
    filas = []

    for n in mallas:
        eje = np.linspace(-5.0, 5.0, n)
        ref = np.empty((n, n))
        par = np.empty((n, n))
        sim.potencial_serial(eje, pos, q, ref)
        denom = np.maximum(np.abs(ref), 1e-30)

        for p in hilos:
            set_num_threads(p)
            sim.potencial_paralelo(eje, pos, q, par)
            diff = np.abs(ref - par)
            err_abs = float(np.max(diff))
            err_rel = float(np.max(diff / denom))
            ok = bool(np.allclose(ref, par, rtol=1e-12, atol=1e-10))
            if not ok:
                raise AssertionError(f'Fallo de verificación en malla {n}, hilos {p}: err={err_abs}')
            filas.append({
                'malla': f'{n}x{n}',
                'hilos': p,
                'rtol': 1e-12,
                'atol_V': 1e-10,
                'error_abs_max_V': err_abs,
                'error_rel_max': err_rel,
                'allclose': ok,
            })

    sim.guardar_csv(carpeta / 'verificacion.csv', filas)
    return filas


def _leer_resumen(ruta_csv: Path) -> list[dict]:
    filas = []
    with ruta_csv.open('r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            filas.append({
                'malla': int(row['malla']),
                'cargas': int(row['cargas']),
                'hilos': int(row['hilos']),
                'serial_ms': float(row['serial_ms']),
                'paralelo_ms': float(row['paralelo_ms']),
                'iqr_serial': float(row['iqr_serial']),
                'iqr_paralelo': float(row['iqr_paralelo']),
                'speedup': float(row['speedup']),
                'eficiencia': float(row['eficiencia']),
                'error': float(row['error']),
                'f_amdahl': float(row['f_amdahl']) if row['f_amdahl'] != '' else None,
            })
    return filas


def graficar_desempeno(datos: list[dict], carpeta: Path) -> None:
    """Genera figuras SVG con etiquetas completas, marcadores, IQR, ideal y Amdahl."""
    paleta = ['#1565c0', '#c62828', '#2e7d32', '#6a1b9a']
    mallas = sorted({d['malla'] for d in datos})
    hilos_unicos = sorted({d['hilos'] for d in datos})
    xmax = max(hilos_unicos)
    xmin = min(hilos_unicos)

    configs = [
        ('fig_tiempo.svg', 'Tiempo de ejecución vs. Número de hilos', 'Tiempo mediana (ms)', 'paralelo_ms'),
        ('fig_speedup.svg', 'Speedup (Sp = T1 / Tp) vs. Número de hilos', 'Speedup (adimensional)', 'speedup'),
        ('fig_eficiencia.svg', 'Eficiencia paralela (Ep = Sp / p) vs. Número de hilos', 'Eficiencia (Ep)', 'eficiencia'),
    ]

    for archivo, titulo, ylabel, clave in configs:
        ymax = max(d[clave] for d in datos) * 1.18
        if clave == 'paralelo_ms':
            ymax = max(ymax, max(d['serial_ms'] for d in datos) * 1.18)
        elif clave == 'speedup':
            ymax = max(ymax, xmax * 1.10)
        elif clave == 'eficiencia':
            ymax = max(ymax, 1.15)

        x0, x1, y0, y1 = 95.0, 740.0, 390.0, 65.0

        def px(p: float) -> float:
            if xmax == xmin:
                return (x0 + x1) / 2.0
            return x0 + (x1 - x0) * (p - xmin) / (xmax - xmin)

        def py(val: float) -> float:
            return y0 - (y0 - y1) * (val / ymax)

        svg = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="820" height="475" font-family="DejaVu Sans, Arial, sans-serif">',
            '<rect width="100%" height="100%" fill="#ffffff"/>',
            f'<text x="410" y="32" text-anchor="middle" font-size="18" font-weight="bold" fill="#111">{titulo}</text>',
        ]

        # Rejilla horizontal y marcas eje Y
        for k in range(6):
            val = ymax * k / 5.0
            yy = py(val)
            svg.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="#e5e9f0" stroke-width="1"/>')
            svg.append(f'<text x="{x0 - 10}" y="{yy + 4:.1f}" text-anchor="end" font-size="12" fill="#333">{val:.3g}</text>')

        # Rejilla vertical y marcas eje X
        for p in hilos_unicos:
            xx = px(p)
            svg.append(f'<line x1="{xx:.1f}" y1="{y1}" x2="{xx:.1f}" y2="{y0}" stroke="#f0f3f8" stroke-width="1"/>')
            svg.append(f'<text x="{xx:.1f}" y="{y0 + 22}" text-anchor="middle" font-size="12" fill="#333">{p}</text>')

        # Ejes principales y títulos
        svg.append(f'<path d="M{x0} {y1} V{y0} H{x1}" fill="none" stroke="#222" stroke-width="1.5"/>')
        svg.append(f'<text x="{(x0 + x1)/2:.1f}" y="445" text-anchor="middle" font-size="14" font-weight="bold" fill="#222">Número de hilos (p)</text>')
        svg.append(f'<text x="24" y="{(y0 + y1)/2:.1f}" text-anchor="middle" font-size="14" font-weight="bold" fill="#222" transform="rotate(-90 24 {(y0 + y1)/2:.1f})">{ylabel}</text>')

        # Línea ideal global para speedup y eficiencia
        if clave == 'speedup':
            pts_ideal = ' '.join(f'{px(p):.1f},{py(p):.1f}' for p in hilos_unicos)
            svg.append(f'<polyline points="{pts_ideal}" fill="none" stroke="#555" stroke-width="1.8" stroke-dasharray="6,4"/>')
        elif clave == 'eficiencia':
            pts_ideal = ' '.join(f'{px(p):.1f},{py(1.0):.1f}' for p in hilos_unicos)
            svg.append(f'<polyline points="{pts_ideal}" fill="none" stroke="#555" stroke-width="1.8" stroke-dasharray="6,4"/>')

        # Series por tamaño de malla
        for idx, n in enumerate(mallas):
            color = paleta[idx % len(paleta)]
            serie = sorted([d for d in datos if d['malla'] == n], key=lambda r: r['hilos'])

            if clave == 'paralelo_ms':
                pts_ideal = ' '.join(f'{px(d["hilos"]):.1f},{py(d["serial_ms"]/d["hilos"]):.1f}' for d in serie)
                svg.append(f'<polyline points="{pts_ideal}" fill="none" stroke="{color}" stroke-width="1.3" stroke-dasharray="5,4" opacity="0.7"/>')

            if clave == 'speedup':
                fs = [d['f_amdahl'] for d in serie if d['f_amdahl'] is not None and 0.0 <= d['f_amdahl'] <= 1.0]
                if fs:
                    f_med = float(np.median(fs))
                    pts_amdahl = ' '.join(
                        f'{px(p):.1f},{py(1.0 / ((1.0 - f_med) + f_med / p)):.1f}'
                        for p in hilos_unicos
                    )
                    svg.append(f'<polyline points="{pts_amdahl}" fill="none" stroke="{color}" stroke-width="1.4" stroke-dasharray="2,3" opacity="0.85"/>')

            pts = []
            for d in serie:
                xx, yy = px(d['hilos']), py(d[clave])
                pts.append(f'{xx:.1f},{yy:.1f}')
                if clave == 'paralelo_ms':
                    y_hi = py(d['paralelo_ms'] + 0.5 * d['iqr_paralelo'])
                    y_lo = py(max(0.0, d['paralelo_ms'] - 0.5 * d['iqr_paralelo']))
                    svg.append(f'<line x1="{xx:.1f}" y1="{y_hi:.1f}" x2="{xx:.1f}" y2="{y_lo:.1f}" stroke="{color}" stroke-width="1.5"/>')

            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2.4"/>')
            for d in serie:
                xx, yy = px(d['hilos']), py(d[clave])
                svg.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4.2" fill="{color}" stroke="#fff" stroke-width="1"/>')

            ly = 62 + idx * 20
            svg.append(f'<line x1="560" y1="{ly - 4}" x2="585" y2="{ly - 4}" stroke="{color}" stroke-width="2.5"/>')
            svg.append(f'<text x="592" y="{ly}" font-size="12" fill="#222">Malla {n} × {n}</text>')

        nota = 'Línea continua: medido (mediana) | Discontinua: ideal'
        if clave == 'speedup':
            nota += ' | Punteada: ajuste Amdahl'
        elif clave == 'paralelo_ms':
            nota += ' | Barras: IQR'
        svg.append(f'<text x="{x0}" y="466" font-size="11" fill="#555">{nota}</text>')
        svg.append('</svg>')
        (carpeta / archivo).write_text('\n'.join(svg), encoding='utf-8')


def graficar_perfilado(perfil: list[dict], carpeta: Path) -> None:
    """Genera gráfico horizontal SVG del perfilado por función física."""
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="820" height="300" font-family="DejaVu Sans, Arial, sans-serif">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="410" y="30" text-anchor="middle" font-size="17" font-weight="bold" fill="#111">Perfilado de costo computacional por componente físico (serial)</text>',
    ]
    x0, x1 = 270.0, 720.0
    colores = ['#c62828', '#1565c0', '#2e7d32', '#6a1b9a']

    for i, item in enumerate(perfil):
        y = 65 + i * 50
        ancho = (x1 - x0) * (item['porcentaje'] / 100.0)
        color = colores[i % len(colores)]
        svg.append(f'<text x="{x0 - 12}" y="{y + 18}" text-anchor="end" font-size="13" fill="#222">{item["componente"]}</text>')
        svg.append(f'<rect x="{x0}" y="{y}" width="{max(2.0, ancho):.1f}" height="26" rx="4" fill="{color}"/>')
        svg.append(
            f'<text x="{x0 + ancho + 8:.1f}" y="{y + 18}" font-size="12" font-weight="bold" fill="#222">'
            f'{item["mediana_ms"]:.3f} ms ({item["porcentaje"]:.1f}%)</text>'
        )

    svg.append(f'<line x1="{x0}" y1="55" x2="{x0}" y2="265" stroke="#222" stroke-width="1.5"/>')
    svg.append('<text x="410" y="288" text-anchor="middle" font-size="12" fill="#444">Justificación de paralelización: el cálculo del potencial en la malla concentra la mayor fracción del tiempo.</text>')
    svg.append('</svg>')
    (carpeta / 'fig_perfilado.svg').write_text('\n'.join(svg), encoding='utf-8')


def graficar_fenomeno(carpeta: Path) -> None:
    """Genera una ilustración SVG limpia del dipolo eléctrico (V, equipotenciales y E)."""
    n = 160
    ext = 4.0
    eje = np.linspace(-ext, ext, n)
    pos = np.array([[-1.4, 0.0], [1.4, 0.0]])
    q = np.array([2e-9, -2e-9])
    v = np.empty((n, n))
    sim.potencial_serial(eje, pos, q, v)

    x0, y0, size = 80.0, 55.0, 440.0
    celda = size / n
    normal = np.clip(np.arcsinh(v / 3.0) / np.arcsinh(60.0 / 3.0), -1.0, 1.0)

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="560" font-family="DejaVu Sans, Arial, sans-serif">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="300" y="30" text-anchor="middle" font-size="17" font-weight="bold" fill="#111">Potencial eléctrico V(x, y), equipotenciales y líneas de campo E (z = 0)</text>',
        f'<g transform="translate({x0},{y0})">',
    ]

    # Mapa de calor discretizado en celdas SVG
    for i in range(n):
        yy = (n - 1 - i) * celda
        for j in range(n):
            val = normal[i, j]
            w = abs(val)
            if val >= 0:
                r = int((1 - w) * 248 + w * 195)
                g = int((1 - w) * 248 + w * 65)
                b = int((1 - w) * 248 + w * 60)
            else:
                r = int((1 - w) * 248 + w * 45)
                g = int((1 - w) * 248 + w * 110)
                b = int((1 - w) * 248 + w * 180)
            svg.append(f'<rect x="{j * celda:.2f}" y="{yy:.2f}" width="{celda + 0.3:.2f}" height="{celda + 0.3:.2f}" fill="rgb({r},{g},{b})"/>')

    # Curvas equipotenciales
    gen = contourpy.contour_generator(x=eje, y=eje, z=v)
    for nivel in [-30, -15, -5, 0, 5, 15, 30]:
        dash = ' stroke-dasharray="4,3"' if nivel == 0 else ''
        for curva in gen.lines(nivel):
            if len(curva) > 1:
                pts = ' '.join(
                    f'{(px_w + ext) * size / (2 * ext):.1f},{(ext - py_w) * size / (2 * ext):.1f}'
                    for px_w, py_w in curva
                )
                svg.append(f'<polyline points="{pts}" fill="none" stroke="#2c3e50" stroke-width="1.2"{dash}/>')

    # Líneas de campo eléctrico
    for idx, curva in enumerate(sim.lineas_campo(pos, q, ext)):
        curva = curva[np.isfinite(curva[:, 0])]
        if len(curva) < 3:
            continue
        pts = ' '.join(
            f'{(px_w + ext) * size / (2 * ext):.1f},{(ext - py_w) * size / (2 * ext):.1f}'
            for px_w, py_w in curva
        )
        svg.append(f'<polyline points="{pts}" fill="none" stroke="#00796b" stroke-width="1.6"/>')

    # Cargas puntuales
    for idx, (cx_w, cy_w) in enumerate(pos):
        cx = (cx_w + ext) * size / (2 * ext)
        cy = (ext - cy_w) * size / (2 * ext)
        color = '#b71c1c' if q[idx] > 0 else '#0d47a1'
        signo = '+' if q[idx] > 0 else '−'
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="{color}" stroke="#fff" stroke-width="1.5"/>')
        svg.append(f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" font-size="13" font-weight="bold" fill="#fff">{signo}</text>')

    svg.append(f'<rect x="0" y="0" width="{size}" height="{size}" fill="none" stroke="#222" stroke-width="1.5"/>')
    svg.append('</g>')

    # Ejes espaciales en metros
    for val in [-4, -2, 0, 2, 4]:
        xx = x0 + (val + ext) * size / (2 * ext)
        yy = y0 + (ext - val) * size / (2 * ext)
        svg.append(f'<text x="{xx:.1f}" y="{y0 + size + 20}" text-anchor="middle" font-size="12" fill="#222">{val}</text>')
        svg.append(f'<text x="{x0 - 10}" y="{yy + 4:.1f}" text-anchor="end" font-size="12" fill="#222">{val}</text>')

    svg.append(f'<text x="{x0 + size/2:.1f}" y="538" text-anchor="middle" font-size="13" font-weight="bold" fill="#222">Posición x (m)</text>')
    svg.append(f'<text x="24" y="{y0 + size/2:.1f}" text-anchor="middle" font-size="13" font-weight="bold" fill="#222" transform="rotate(-90 24 {y0 + size/2:.1f})">Posición y (m)</text>')
    svg.append('<text x="535" y="100" font-size="12" fill="#b71c1c" font-weight="bold">+2 nC (x = -1.4 m)</text>')
    svg.append('<text x="535" y="122" font-size="12" fill="#0d47a1" font-weight="bold">−2 nC (x = +1.4 m)</text>')
    svg.append('<text x="535" y="155" font-size="11" fill="#00796b">Verde: líneas de campo E</text>')
    svg.append('<text x="535" y="175" font-size="11" fill="#2c3e50">Gris: equipotenciales</text>')
    svg.append('<text x="535" y="195" font-size="11" fill="#444">Fondo: V ∈ [−60, +60] V</text>')
    svg.append('</svg>')
    (carpeta / 'fig_fenomeno.svg').write_text('\n'.join(svg), encoding='utf-8')


def main() -> None:
    nucleos_fisicos = detectar_nucleos_fisicos()
    hilos_default = secuencia_hilos(nucleos_fisicos)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mallas', nargs='+', type=int, default=[150, 350, 600])
    parser.add_argument('--hilos', nargs='+', type=int, default=hilos_default)
    parser.add_argument('--repeticiones', type=int, default=7)
    parser.add_argument('--salida', default='resultados')
    args = parser.parse_args()

    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)

    print(f'Núcleos físicos detectados: {nucleos_fisicos} | Hilos a evaluar: {args.hilos}', flush=True)
    print('1/4 Ejecutando perfilado de componentes...', flush=True)
    perfil = perfilar_componentes(max(args.mallas), args.repeticiones, carpeta)

    print('2/4 Verificando equivalencia numérica serial vs. paralelo...', flush=True)
    verificar_consistencia(args.mallas, args.hilos, carpeta)

    print('3/4 Ejecutando experimentos de desempeño (CSV + hardware)...', flush=True)
    sim.experimentos(args)

    print('4/4 Generando figuras vectoriales para informe y póster...', flush=True)
    datos = _leer_resumen(carpeta / 'resumen.csv')
    graficar_desempeno(datos, carpeta)
    graficar_perfilado(perfil, carpeta)
    graficar_fenomeno(carpeta)
    print(f'Listo. Todos los resultados y figuras se guardaron en: {carpeta.resolve()}', flush=True)


if __name__ == '__main__':
    main()