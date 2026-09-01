import math as m
angulo = float(input("Sin del ángulo en grados: "))
x = m.radians(angulo)
suma = 0
nterminos = int(input("Número de términos: "))
for i in range(nterminos):
    termino = ((-1)**i)*(x**(2*i+1))/m.factorial(2*i+1)
    suma = suma + termino
print(f"El seno de {angulo} es: {suma}")
