entrada = input("¿Qué frase quiere invertir?: ")
salida = ""

palabras = entrada.split(" ")

for i in range(len(palabras)):
    salida = palabras[i] + " " + salida

print(salida)