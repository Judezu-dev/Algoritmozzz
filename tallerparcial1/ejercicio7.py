#Construir un programa que calcule la moda de una lista de elementos enteros. El programa debe indicar
#de manera explícita qué hace cuando el conjunto es multimodal, es decir, cuando hay más de un valor con
#la misma frecuencia máxima, y qué hace cuando ningún valor se repite.

Lista = []
Modas = []
num = int(input("Número de elementos: "))


for _ in range(num):
    Lista.append(int(input("Elemento:")))

frecuencias = {}
for i in Lista:
    if i in frecuencias:
        frecuencias[i] += 1
    else:
        frecuencias[i] = 1

maxf = 0
for conteo in frecuencias.values():
    if conteo > maxf:
        maxf = conteo

for i, valor in frecuencias.items():
    if valor == maxf:
        Modas.append(i)

if maxf == 1:
    print("Ningún valor se repite")
else:    
    print(f"La/s moda/s del conjunto es/son: {Modas} y se repite/n {maxf} veces5")





