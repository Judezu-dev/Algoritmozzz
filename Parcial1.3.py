#fibonnaci
rango = int(input("Cúantos n terminos de la serie de fibonacci desea: "))
fibo = [0 , 1 ] #agrego los primeros dos terminos para no tener problemas luego

ultimo = 1
penultimo = 0

suma = 0
for i in range(rango-2): #el -2 es pq ya están definidos los primeros dos po
    suma = penultimo + ultimo
    penultimo = ultimo
    ultimo = suma
    fibo.append(suma)

pares = 0

for j in fibo:
    if j > 0:
        if j % 2 == 0:
            pares += 1

print(fibo)
print(f"La proporción de pares es {pares}/{rango}")