rango = int(input("Ingrese el rango de números a evaluar: "))
for i in range(rango+1):
    if i**0.5 == int(i**0.5):
        print(f"{i} es un cuadrado perfecto y su raiz cuadrada es {int(i**0.5)}")