n = int(input("Ingresa el numero de letras: "))
entrada = input("Inserta tu frase: ")
palabras = entrada.split(" ")
numero = 0

for i in (palabras):
    if len(i) == n:
        palabra = i
        numero = numero + 1
        print(palabra)

print(f"Hay {numero} palabras con {n} letras")