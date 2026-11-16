
"""
Controles: espacio pausa; clic selecciona; arrastrar en pausa recoloca.
Agregar + o - y luego clic coloca una carga de ±2 nC. Quitar borra la seleccionada.
La gráfica usa una escala de color fija ±60 V; el cálculo no se recorta.
La escala espacial se amplía automáticamente si una carga se aleja.
El código se organiza en física, mediciones, ventana y main.
"""
import argparse
import csv
import json
import math
import os
import platform
from pathlib import Path
from time import perf_counter

import numpy as np
from numba import njit, prange, set_num_threads, get_num_threads, config

K = 8.9875517923e9
EPS = 0.18
MASA = 1e-8


# 1. FÍSICA. Las dos versiones de potencial hacen exactamente el mismo trabajo.
@njit(cache=True)
def potencial_serial(eje, pos, q, salida):
    for i in range(len(eje)):
        for j in range(len(eje)):
            valor = 0.
            for c in range(len(q)):
                dx = eje[j] - pos[c, 0]
                dy = eje[i] - pos[c, 1]
                valor += K*q[c]/math.sqrt(dx*dx+dy*dy+EPS*EPS)
            salida[i, j] = valor


@njit(cache=True, parallel=True)
def potencial_paralelo(eje, pos, q, salida):
    for i in prange(len(eje)):
        for j in range(len(eje)):
            valor = 0.
            for c in range(len(q)):
                dx = eje[j] - pos[c, 0]
                dy = eje[i] - pos[c, 1]
                valor += K*q[c]/math.sqrt(dx*dx+dy*dy+EPS*EPS)
            salida[i, j] = valor


@njit(cache=True)
def campo(punto, pos, q, excluir=-1):
    ex, ey, v = 0., 0., 0.
    for j in range(len(q)):
        if j == excluir:
            continue
        dx = punto[0]-pos[j, 0]
        dy = punto[1]-pos[j, 1]
        r2 = dx*dx+dy*dy+EPS*EPS
        factor = K*q[j]/math.sqrt(r2)
        v += factor
        ex += factor*dx/r2
        ey += factor*dy/r2
    return ex, ey, v


@njit(cache=True)
def fuerzas(pos, q):
    f = np.zeros_like(pos)
    for i in range(len(q)):
        for j in range(i+1, len(q)):
            d = pos[i]-pos[j]
            r2 = d[0]*d[0] + d[1]*d[1] + EPS*EPS
            par = K*q[i]*q[j]*d/(r2*math.sqrt(r2))
            f[i] += par
            f[j] -= par
    return f


@njit(cache=True)
def avanzar(pos, vel, q, dt, pasos):
    f = fuerzas(pos, q)
    for _ in range(pasos):
        vel += .5*dt*f/MASA
        pos += dt*vel
        f = fuerzas(pos, q)
        vel += .5*dt*f/MASA


@njit(cache=True)
def lineas_campo(pos, q, extension):
    # Máximo 32 curvas y 180 pasos: el coste visual queda acotado.
    numero = min(len(q), 4)
    curvas = np.full((numero*8, 180, 2), np.nan)
    paso = extension/65
    for carga in range(numero):
        sentido = 1. if q[carga] > 0 else -1.
        for semilla in range(8):
            angulo = semilla*math.pi/4
            punto = pos[carga] + .12*np.array([math.cos(angulo), math.sin(angulo)])
            for k in range(180):
                if np.max(np.abs(punto)) > extension:
                    break
                cerca = False
                for j in range(len(q)):
                    if j != carga and np.sum((punto-pos[j])**2) < .10**2:
                        cerca = True
                if cerca:
                    break
                curvas[carga*8+semilla, k] = punto
                ex, ey, _ = campo(punto, pos, q)
                norma = math.hypot(ex, ey)
                if norma < 1e-12:
                    break
                medio = punto + sentido*.5*paso*np.array([ex, ey])/norma
                ex, ey, _ = campo(medio, pos, q)
                norma = math.hypot(ex, ey)
                if norma < 1e-12:
                    break
                punto += sentido*paso*np.array([ex, ey])/norma
    return curvas


def energia(pos, vel, q):
    ec = .5*MASA*np.sum(vel*vel)
    u = 0.
    for i in range(len(q)):
        u += .5*q[i]*campo(pos[i], pos, q, i)[2]
    return ec, u


# 2. MEDICIONES. Las salidas se reservan y los kernels se calientan antes del reloj.
def comparar(eje, pos, q, repeticiones=7):
    a = np.empty((len(eje), len(eje)))
    b = np.empty_like(a)
    potencial_serial(eje, pos, q, a)
    potencial_paralelo(eje, pos, q, b)
    tiempos = [[], []]
    funciones = [potencial_serial, potencial_paralelo]
    for r in range(repeticiones):
        orden = [0, 1] if r % 2 == 0 else [1, 0]
        for i in orden:
            inicio = perf_counter()
            funciones[i](eje, pos, q, a if i == 0 else b)
            tiempos[i].append((perf_counter()-inicio)*1000)
    if not np.allclose(a, b, rtol=1e-12, atol=1e-10):
        raise ValueError('Serial y paralelo no coinciden.')
    t1, tp = [float(np.median(t)) for t in tiempos]
    dispersion = [float(np.percentile(t, 75)-np.percentile(t, 25)) for t in tiempos]
    p = get_num_threads()
    sp = t1/tp
    datos = dict(malla=len(eje), cargas=len(q), hilos=p, serial_ms=t1,
                 paralelo_ms=tp, iqr_serial=dispersion[0], iqr_paralelo=dispersion[1],
                 speedup=sp, eficiencia=sp/p, error=float(np.max(abs(a-b))),
                 f_amdahl=(1-1/sp)/(1-1/p) if p > 1 else '')
    return datos, tiempos


def guardar_csv(ruta, filas):
    with ruta.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)


def graficas(datos, carpeta):
    # SVG se abre en el navegador: no requiere otra biblioteca de gráficos.
    for clave, titulo in [('paralelo_ms', 'Tiempo (ms)'), ('speedup', 'Speedup'),
                          ('eficiencia', 'Eficiencia')]:
        xmax = max(d['hilos'] for d in datos)
        ymax = max(d[clave] for d in datos)*1.15
        if clave == 'paralelo_ms':
            ymax = max(ymax, max(d['serial_ms'] for d in datos)*1.15)
        if clave == 'speedup':
            ymax = max(ymax, xmax*1.15)
        if clave == 'eficiencia':
            ymax = max(ymax, 1.15)
        def punto(p, y):
            return f'{80+550*(p-1)/max(1,xmax-1):.1f},{350-280*y/ymax:.1f}'
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="440">',
               '<rect width="100%" height="100%" fill="white"/>',
               f'<text x="80" y="25" font-size="20">{titulo}</text>',
               '<path d="M80 60 V350 H650" fill="none" stroke="black"/>',
               '<text x="320" y="410">Número de hilos</text>']
        for y in np.linspace(0, ymax, 5):
            altura = 350-280*y/ymax
            svg.append(f'<text x="10" y="{altura:.1f}">{y:.3g}</text>')
        for p in sorted(set(d['hilos'] for d in datos)):
            x = punto(p, 0).split(',')[0]
            svg.append(f'<text x="{x}" y="375">{p}</text>')
        for i, n in enumerate(sorted(set(d['malla'] for d in datos))):
            serie = sorted([d for d in datos if d['malla'] == n], key=lambda d:d['hilos'])
            color = ['#197c92', '#c55440', '#8156a1'][i % 3]
            puntos = ' '.join(punto(d['hilos'], d[clave]) for d in serie)
            svg.append(f'<polyline points="{puntos}" stroke="{color}" fill="none" stroke-width="2"/>')
            svg.append(f'<text x="450" y="{25+i*18}" fill="{color}">Malla {n} x {n}</text>')
            ideal = []
            for d in serie:
                y = d['serial_ms']/d['hilos'] if clave == 'paralelo_ms' else d['hilos']
                if clave == 'eficiencia':
                    y = 1
                ideal.append(punto(d['hilos'], y))
            svg.append(f'<polyline points="{" ".join(ideal)}" stroke="{color}" fill="none" stroke-dasharray="5,5"/>')
        svg.append('<text x="80" y="435">Continua: medido. Discontinua: ideal.</text></svg>')
        (carpeta/(clave+'.svg')).write_text('\n'.join(svg), encoding='utf-8')


def experimentos(args):
    carpeta = Path(args.salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026)
    pos = rng.uniform(-3, 3, (32, 2))
    q = rng.choice(np.array([-2e-9, 2e-9]), 32)
    datos, muestras = [], []
    for n in args.mallas:
        eje = np.linspace(-5, 5, n)
        for p in args.hilos:
            set_num_threads(p)
            fila, tiempos = comparar(eje, pos, q, args.repeticiones)
            datos.append(fila)
            for tipo, valores in zip(['serial', 'paralelo'], tiempos):
                for r, t in enumerate(valores):
                    muestras.append(dict(malla=n, hilos=p, tipo=tipo, repeticion=r+1, ms=t))
            print(f'Malla {n}, {p} hilos: speedup {fila["speedup"]:.2f}', flush=True)
    guardar_csv(carpeta/'resumen.csv', datos)
    guardar_csv(carpeta/'muestras.csv', muestras)
    graficas(datos, carpeta)
    import numba
    import importlib.metadata
    hardware = dict(sistema=platform.platform(), cpu=platform.processor(),
                    python=platform.python_version(), numpy=np.__version__, numba=numba.__version__,
                    nucleos_logicos=os.cpu_count(), nucleos_fisicos='Consultar en el equipo',
                    repeticiones=args.repeticiones, semilla=2026, cargas=32,
                    nota='JIT y dibujo excluidos. CPU física y fracción serial requieren interpretación.')
    # Linux publica modelo y pares (socket, núcleo); en otros sistemas se declara desconocido.
    cpuinfo = Path('/proc/cpuinfo')
    if cpuinfo.exists():
        nucleos = set()
        for bloque in cpuinfo.read_text().split('\n\n'):
            campos = dict(linea.split(':', 1) for linea in bloque.splitlines() if ':' in linea)
            campos = {k.strip():v.strip() for k, v in campos.items()}
            if 'physical id' in campos and 'core id' in campos:
                nucleos.add((campos['physical id'], campos['core id']))
            if 'model name' in campos:
                hardware['cpu'] = campos['model name']
        if nucleos:
            hardware['nucleos_fisicos'] = len(nucleos)
    (carpeta/'hardware.json').write_text(json.dumps(hardware, indent=2), encoding='utf-8')
    dependencias = ['numpy', 'numba', 'pygame-ce', 'contourpy']
    versiones = [nombre+'=='+importlib.metadata.version(nombre) for nombre in dependencias]
    (carpeta/'requirements.txt').write_text('\n'.join(versiones)+'\n', encoding='utf-8')
    comando = f'python3 simulador_electrico.py --medir --mallas {" ".join(map(str,args.mallas))}'
    comando += f' --hilos {" ".join(map(str,args.hilos))} --repeticiones {args.repeticiones}'
    readme = '# Reproducción\n\n'+str(__doc__)+'\n\nComando utilizado:\n\n'+comando
    readme += '\n\nHardware y Python: hardware.json. Versiones: requirements.txt.\n'
    readme += 'Usar hilos 1, 2, 4, ... hasta los núcleos físicos del equipo para el estudio completo.\n'
    (carpeta/'README.md').write_text(readme, encoding='utf-8')


# 3. VENTANA. Una sola clase conserva el estado y atiende los botones.
class Simulador:
    def __init__(self, malla=100):
        os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
        import pygame
        self.pg = pygame
        pygame.display.init()
        pygame.font.init()
        self.ventana = pygame.display.set_mode((980, 660))
        pygame.display.set_caption('Simulador de cargas puntuales')
        self.fuente = pygame.font.SysFont('dejavusans,arial', 15)
        self.titulo = pygame.font.SysFont('dejavusans,arial', 24)
        # Cabecera preparada una sola vez: contorno degradado azul-rojo.
        nombre = 'Simulador de cargas puntuales'
        fuente_titulo = pygame.font.SysFont('dejavusans,arial', 29, bold=True)
        letras = fuente_titulo.render(nombre, True, (240, 246, 255))
        mascara = fuente_titulo.render(nombre, True, (255, 255, 255))
        borde = pygame.Surface(mascara.get_size(), pygame.SRCALPHA)
        for x in range(borde.get_width()):
            t = x/max(1, borde.get_width()-1)
            color = (int(55+190*t), int(151-70*t), int(255-145*t), 255)
            pygame.draw.line(borde, color, (x, 0), (x, borde.get_height()))
        borde.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.cabecera = pygame.Surface((letras.get_width()+6, letras.get_height()+6), pygame.SRCALPHA)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            self.cabecera.blit(borde, (3+dx, 3+dy))
        self.cabecera.blit(letras, (3, 3))
        self.hover = [0.]*6
        self.plano = pygame.Rect(35, 90, 520, 520)
        self.malla = malla
        self.mapa = pygame.Surface(self.plano.size)
        self.botones = [pygame.Rect(575+(i % 3)*133, 540+(i//3)*34, 127, 28) for i in range(6)]
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        self.agregar = 0
        self.arrastrando = False
        self.resultado = None
        self.motor = potencial_serial
        self.reiniciar()
        # Calentamiento de la física sobre copias: no mueve las cargas reales.
        avanzar(self.pos.copy(), self.vel.copy(), self.q, self.dt, 1)
        lineas_campo(self.pos, self.q, self.extension)
        self.medir()
        self.ultimo_mapa = self.ultimo_panel = 0.
        self.panel = []
        self.intervalo_mapa = .05
        self.reloj.tick()

    def reiniciar(self):
        self.pos = np.array([[-1.4, 0.], [1.4, 0.]])
        self.q = np.array([2e-9, -2e-9])
        self.vel = np.zeros_like(self.pos)
        self.t = 0.
        self.extension = 5.
        self.seleccion = 0
        self.agregar = 0
        self.arrastrando = False
        self.edicion()

    def edicion(self):
        # Cota conservadora para que la fuerza cercana no vuelva inestable el paso.
        cargas = abs(self.q)
        cota = 2*K*np.max(cargas*(cargas.sum()-cargas), initial=0)/(MASA*EPS**3)
        self.dt = min(.002, .05/math.sqrt(max(cota, 1e-30)))
        rapidez = np.linalg.norm(self.vel, axis=1).max(initial=0)
        self.dt = min(self.dt, .05*EPS/max(rapidez, 1e-15))
        ec, u = energia(self.pos, self.vel, self.q)
        self.energia0 = ec+u
        self.escala_energia = max(ec+abs(u), 1e-30)
        self.acumulado = 0.
        self.sucio = True
        self.resultado = None

    def medir(self):
        eje = np.linspace(-self.extension, self.extension, self.malla)
        self.resultado, _ = comparar(eje, self.pos, self.q)
        self.motor = potencial_paralelo if self.resultado['speedup'] > 1.3 else potencial_serial

    def pixel(self, pos):
        escala = 519/(2*self.extension)
        return (35+(pos[0]+self.extension)*escala, 90+(self.extension-pos[1])*escala)

    def mundo(self, punto):
        escala = 2*self.extension/519
        return np.array([(punto[0]-35)*escala-self.extension,
                         self.extension-(punto[1]-90)*escala])

    def actualizar_mapa(self):
        import contourpy
        inicio = perf_counter()
        eje = np.linspace(-self.extension, self.extension, self.malla)
        v = np.empty((self.malla, self.malla))
        self.motor(eje, self.pos, self.q, v)
        # Color divergente: azul negativo, blanco cero y rojo positivo.
        normal = np.clip(np.arcsinh(v/3)/np.arcsinh(60/3), -1, 1)
        color = np.array([190, 65, 60])
        azul = np.array([45, 110, 175])
        extremos = np.where(normal[:, :, None] > 0, color, azul)
        peso = abs(normal[:, :, None])
        rgb = ((1-peso)*248+peso*extremos).astype(np.uint8)
        imagen = self.pg.surfarray.make_surface(rgb[::-1].transpose(1, 0, 2))
        self.pg.transform.smoothscale(imagen, self.plano.size, self.mapa)
        curvas = contourpy.contour_generator(x=eje, y=eje, z=v)
        etiquetas = []
        zonas_cargas = []
        for posicion in self.pos:
            x, y = self.pixel(posicion)
            zonas_cargas.append(self.pg.Rect(x-35-16, y-90-16, 32, 32))
        for nivel in [-60, -30, -15, -3, 0, 3, 15, 30, 60]:
            for curva in curvas.lines(nivel):
                if len(curva) > 1:
                    puntos = (curva+self.extension)*519/(2*self.extension)
                    puntos[:, 1] = 519-puntos[:, 1]
                    self.pg.draw.aalines(self.mapa, (80, 100, 120), False, puntos)
                    # Una etiqueta por curva; se evitan bordes, cargas y otros textos.
                    color = (42, 89, 137) if nivel < 0 else (154, 64, 57)
                    if nivel == 0:
                        color = (75, 90, 105)
                    nombre = f'{nivel:+g} V' if nivel else '0 V'
                    letras = self.fuente.render(nombre, True, (25, 39, 53))
                    borde = self.fuente.render(nombre, True, (255, 255, 255))
                    texto = self.pg.Surface((letras.get_width()+2, letras.get_height()+2), self.pg.SRCALPHA)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        texto.blit(borde, (1+dx, 1+dy))
                    texto.blit(letras, (1, 1))
                    for indice in np.linspace(0, len(puntos)-1, min(24, len(puntos)), dtype=int):
                        rect = texto.get_rect(center=puntos[indice]).inflate(8, 4)
                        ocupado = any(rect.inflate(10, 8).colliderect(r) for r, _ in etiquetas)
                        ocupado |= any(rect.colliderect(r) for r in zonas_cargas)
                        if self.mapa.get_rect().inflate(-12, -12).contains(rect) and not ocupado:
                            if len(etiquetas) < 24:
                                etiquetas.append((rect, texto))
                            break
        for indice, curva in enumerate(lineas_campo(self.pos, self.q, self.extension)):
            curva = curva[np.isfinite(curva[:, 0])]
            if len(curva) < 3:
                continue
            puntos = (curva+self.extension)*519/(2*self.extension)
            puntos[:, 1] = 519-puntos[:, 1]
            tinta = (32, 142, 135)
            self.pg.draw.aalines(self.mapa, tinta, False, puntos)
            k = min(25, len(puntos)//2)
            direccion = puntos[k+1]-puntos[k-1]
            direccion *= np.sign(self.q[indice//8])
            direccion /= max(np.linalg.norm(direccion), 1e-12)
            punta = puntos[k]
            normal = np.array([-direccion[1], direccion[0]])
            self.pg.draw.polygon(self.mapa, tinta,
                                 [punta, punta-7*direccion+3*normal, punta-7*direccion-3*normal])
        for rect, texto in etiquetas:
            self.mapa.blit(texto, texto.get_rect(center=rect.center))
        self.mapa_ms = (perf_counter()-inicio)*1000
        self.intervalo_mapa = min(.15, max(.05, self.mapa_ms/200))
        self.sucio = False

    def texto(self, texto, x, y, color=(210, 221, 235), grande=False):
        fuente = self.titulo if grande else self.fuente
        self.ventana.blit(fuente.render(texto, True, color), (x, y))

    def actualizar_panel(self):
        ec, u = energia(self.pos, self.vel, self.q)
        self.panel = [f't = {self.t:.2f} s | N = {len(self.q)}',
                      f'Malla {self.malla} x {self.malla} | hilos {get_num_threads()}',
                      f'dt = {self.dt:.2e} s | eps = {EPS} m',
                      f'Masa por carga = {MASA:.0e} kg']
        if self.seleccion is not None:
            i = self.seleccion
            ex, ey, v = campo(self.pos[i], self.pos, self.q, i)
            e = math.hypot(ex, ey)
            self.panel += [f'Carga {i+1}: {self.q[i]*1e9:+g} nC',
                           f'|v| = {np.linalg.norm(self.vel[i]):.3e} m/s',
                           f'|E externo| = {e:.3e} N/C',
                           f'|F| = {abs(self.q[i])*e:.3e} N', f'V externo = {v:.3e} V']
        self.panel += [f'Ec = {ec:.3e} J | U = {u:.3e} J',
                       f'Deriva H = {(ec+u-self.energia0)/self.escala_energia:+.2e}',
                       f'FPS {self.reloj.get_fps():.0f} | mapa {self.mapa_ms:.2f} ms']
        r = self.resultado
        if r:
            self.panel += [f'Serial: {r["serial_ms"]:.3f} ms', f'Paralelo: {r["paralelo_ms"]:.3f} ms',
                           f'IQR: {r["iqr_serial"]:.3f} / {r["iqr_paralelo"]:.3f} ms',
                           f'Sp: {r["speedup"]:.2f} | Ep: {100*r["eficiencia"]:.1f}%',
                           f'Error max.: {r["error"]:.1e} V | OK',
                           '7 muestras; sin JIT ni dibujo.', 'Instantánea de la última comparación.']
        else:
            self.panel += ['Pulsa Comparar para medir esta escena.']

    def dibujar(self):
        self.ventana.fill((13, 21, 34))
        self.pg.draw.rect(self.ventana, (18, 30, 47), (0, 0, 980, 78))
        self.ventana.blit(self.cabecera, (26, 8))
        self.texto('Campo eléctrico  ·  Potencial  ·  Movimiento', 31, 49, (136, 163, 191))
        estado = 'Colocar carga' if self.agregar else ('En movimiento' if self.corriendo else 'Pausado')
        acento = (247, 191, 96) if not self.corriendo else (83, 211, 180)
        self.pg.draw.circle(self.ventana, acento, (783, 27), 4)
        self.texto(estado, 797, 17, acento)
        self.texto('F = qE     a = F/m', 780, 48, (105, 134, 165))
        # Dos cargas decorativas oscilan en la cabecera; sólo se dibujan círculos.
        for i, signo in enumerate(['+', '-']):
            x = 663+i*49
            y = 30+4*math.sin(self.pg.time.get_ticks()/900+i*math.pi)
            color = (177, 88, 104) if i == 0 else (73, 130, 191)
            self.pg.draw.circle(self.ventana, color, (x, y), 13, 1)
            self.texto(signo, x-5, y-10, color)
        nombres = ['Ⅱ Pausar' if self.corriendo else '▶ Mover', '+ Positiva', '− Negativa',
                   '× Quitar', '≡ Comparar', '↻ Reiniciar']
        colores = [(115, 87, 43), (130, 55, 67), (39, 86, 141),
                   (72, 65, 89), (30, 105, 103), (50, 70, 97)]
        for i, (rect, nombre) in enumerate(zip(self.botones, nombres)):
            activo = (i == 1 and self.agregar == 1) or (i == 2 and self.agregar == -1)
            objetivo = float(rect.collidepoint(self.pg.mouse.get_pos()) or activo)
            self.hover[i] += (objetivo-self.hover[i])*.22
            color = tuple(min(255, int(c+28*self.hover[i])) for c in colores[i])
            self.pg.draw.rect(self.ventana, color, rect, border_radius=7)
            if activo:
                self.pg.draw.rect(self.ventana, (242, 206, 124), rect, 2, border_radius=7)
            self.texto(nombre, rect.x+12, rect.y+5, (240, 246, 255))
        self.ventana.blit(self.mapa, self.plano)
        for i, pos in enumerate(self.pos):
            centro = self.pixel(pos)
            color = (190, 65, 60) if self.q[i] > 0 else (45, 110, 175)
            if i == self.seleccion:
                self.pg.draw.circle(self.ventana, (225, 171, 40), centro, 12, 2)
            self.pg.draw.circle(self.ventana, color, centro, 8)
            self.texto('+' if self.q[i] > 0 else '-', centro[0]-5, centro[1]-10, (255, 255, 255))
        seleccionadas = 5 if self.seleccion is not None else 0
        corte = 4+seleccionadas
        grupos = [('SIMULACIÓN', self.panel[:4], (105, 181, 245)),
                  ('CARGA SELECCIONADA', self.panel[4:corte], (245, 156, 132)),
                  ('ENERGÍA', self.panel[corte:corte+2], (192, 160, 240)),
                  ('RENDIMIENTO / COMPARACIÓN', self.panel[corte+2:], (88, 204, 183))]
        y = 90
        for titulo, lineas, color in grupos:
            if not lineas:
                continue
            alto = 29+len(lineas)*16
            self.pg.draw.rect(self.ventana, (25, 39, 57), (575, y, 395, alto), border_radius=9)
            self.pg.draw.rect(self.ventana, color, (575, y+9, 4, alto-18), border_radius=2)
            self.texto(titulo, 588, y+5, color)
            for i, linea in enumerate(lineas):
                self.texto(linea, 588, y+27+i*16)
            y += alto+6
        self.texto(f'x, y: de {-self.extension:g} a {self.extension:g} m | Corte z=0', 35, 615)
        mensaje = 'Clic en el plano: colocar carga' if self.agregar else 'Clic: seleccionar | Arrastrar en pausa | Espacio: pausa'
        self.texto(mensaje, 35, 638)
        self.texto('Azul -60 V / blanco 0 / rojo +60 V', 585, 615)
        self.texto('Verde: campo E  |  Gris: equipotenciales', 585, 638)
        self.pg.display.flip()

    def evento(self, ev):
        pg = self.pg
        if ev.type == pg.KEYDOWN and ev.key == pg.K_SPACE:
            self.corriendo = not self.corriendo
            self.acumulado = 0.
        if ev.type == pg.MOUSEBUTTONUP:
            self.arrastrando = False
        if ev.type == pg.MOUSEMOTION and self.arrastrando:
            self.pos[self.seleccion] = self.mundo(ev.pos)
            self.vel[self.seleccion] = 0
            self.edicion()
        if ev.type != pg.MOUSEBUTTONDOWN or ev.button != 1:
            return
        for i, rect in enumerate(self.botones):
            if rect.collidepoint(ev.pos):
                if i == 0:
                    self.corriendo = not self.corriendo
                    self.acumulado = 0.
                elif i in (1, 2):
                    self.corriendo = False
                    self.agregar = 1 if i == 1 else -1
                elif i == 3 and self.seleccion is not None:
                    self.pos = np.delete(self.pos, self.seleccion, axis=0)
                    self.vel = np.delete(self.vel, self.seleccion, axis=0)
                    self.q = np.delete(self.q, self.seleccion)
                    self.seleccion = 0 if len(self.q) else None
                    self.edicion()
                elif i == 4:
                    self.medir()
                    self.reloj.tick()
                elif i == 5:
                    self.reiniciar()
                return
        if not self.plano.collidepoint(ev.pos):
            return
        if self.agregar and len(self.q) < 64:
            self.pos = np.vstack((self.pos, self.mundo(ev.pos)))
            self.vel = np.vstack((self.vel, [0., 0.]))
            self.q = np.append(self.q, self.agregar*2e-9)
            self.seleccion = len(self.q)-1
            self.agregar = 0
            self.edicion()
        elif len(self.q):
            distancias = [np.linalg.norm(np.array(self.pixel(p))-ev.pos) for p in self.pos]
            i = int(np.argmin(distancias))
            if distancias[i] < 18:
                self.seleccion = i
                self.arrastrando = not self.corriendo

    def fotograma(self, segundos):
        if self.corriendo:
            self.acumulado += min(segundos, .1)
            pasos = min(96, int(self.acumulado/self.dt))
            avanzar(self.pos, self.vel, self.q, self.dt, pasos)
            self.t += pasos*self.dt
            self.acumulado = min(self.dt, self.acumulado-pasos*self.dt)
            self.sucio = True
        distancia = np.max(abs(self.pos), initial=0)
        if distancia > .9*self.extension:
            self.extension = max(self.extension, distancia*1.3)
            self.sucio = True
        ahora = perf_counter()
        if self.sucio and ahora-self.ultimo_mapa >= self.intervalo_mapa:
            self.actualizar_mapa()
            self.ultimo_mapa = ahora
        if ahora-self.ultimo_panel >= .25:
            self.actualizar_panel()
            self.ultimo_panel = ahora
        self.dibujar()

    def ejecutar(self):
        activo = True
        try:
            while activo:
                segundos = self.reloj.tick(60)/1000
                for ev in self.pg.event.get():
                    if ev.type == self.pg.QUIT:
                        activo = False
                    self.evento(ev)
                self.fotograma(segundos)
        finally:
            self.pg.quit()


# 4. INICIO. --medir permite cumplir los experimentos sin abrir la ventana.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--medir', action='store_true')
    parser.add_argument('--mallas', nargs='+', type=int, default=[100, 240])
    parser.add_argument('--hilos', nargs='+', type=int, default=[1, min(4, config.NUMBA_NUM_THREADS)])
    parser.add_argument('--repeticiones', type=int, default=7)
    parser.add_argument('--salida', default='resultados')
    args = parser.parse_args()
    if min(args.mallas) < 40 or max(args.mallas) > 1200 or args.repeticiones < 5:
        parser.error('Mallas de 40 a 1200; al menos 5 repeticiones.')
    if min(args.hilos) < 1 or max(args.hilos) > config.NUMBA_NUM_THREADS:
        parser.error(f'Hilos válidos: 1 a {config.NUMBA_NUM_THREADS}')
    args.hilos = sorted(set(args.hilos))
    if args.medir:
        if len(set(args.mallas)) < 2:
            parser.error('Usa al menos dos tamaños de malla.')
        experimentos(args)
    else:
        set_num_threads(max(args.hilos))
        print('Preparando Numba; espera unos segundos...', flush=True)
        Simulador(args.mallas[0]).ejecutar()


if __name__ == '__main__':
    main()
