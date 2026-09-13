#Calculadora de funciones trigonometricas con series
import math as m

print("Este programa calcula las funciones seno, coseno y tangente mediante series de 80 elementos 😺")

opcion = 0
while opcion != 4:
    opcion = int(input("Seleccione: 1. Seno | 2. Coseno | 3. Tangente | 4. Salir : "))

    if opcion == 1:
        angulo = float(input("Ingrese el ángulo en grados: "))
        x = m.radians(angulo)
        suma = 0
        nterminos = 80
        for i in range(nterminos):
            termino = ((-1)**i)*(x**(2*i+1))/m.factorial(2*i+1)
            suma = suma + termino
        print(f"El seno de {angulo} es: {suma}")

    elif opcion == 2:
        angulo = float(input("Ingrese el ángulo en grados: "))
        x = m.radians(angulo)
        suma = 0
        nterminos = 80
        for i in range(nterminos):
            termino = ((-1)**i)*(x**(2*i))/m.factorial(2*i)
            suma = suma + termino
        print(f"El coseno de {angulo} es: {suma}")

    elif opcion == 3:
        print("¡Lo siento! aún no se ha implementado la tangente, pero con esta opción se podrá hallar")

    elif opcion == 4:
        print("¡Ádios!")

    else: print("ingrese un valor válido") 

