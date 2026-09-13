#Construir un programa que lea un número variable de valores enteros. El resultado que entregará el
#programa es la media de los números pares de entre los leídos, es decir, la suma de todos los valores
#pares dividida por el número de estos. Implementarlo usando listas, y también sin usarlas.

num = int(input("Cantidad de elementos: "))
numeros = []
for i in range(num):
    numeros.append(int(input("Elemento: ")))

pares = 0
suma = 0

for i in range(len(numeros)):
    if numeros[i]/2 == numeros[i]//2:
        pares += 1
        suma += numeros[i]

if pares == 0:
    print("Ningun numero par fue ingresado")
else: 
    print(f"La media de todos los numeros pares es {suma/pares}")