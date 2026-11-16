# Reproducción


Controles: espacio pausa; clic selecciona; arrastrar en pausa recoloca.
Agregar + o - y luego clic coloca una carga de ±2 nC. Quitar borra la seleccionada.
La gráfica usa una escala de color fija ±60 V; el cálculo no se recorta.
La escala espacial se amplía automáticamente si una carga se aleja.
El código se organiza en física, mediciones, ventana y main.


Comando utilizado:

python3 simulador_electrico.py --medir --mallas 150 350 600 --hilos 1 2 4 8 --repeticiones 7

Hardware y Python: hardware.json. Versiones: requirements.txt.
Usar hilos 1, 2, 4, ... hasta los núcleos físicos del equipo para el estudio completo.
