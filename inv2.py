entrada = input("¿Qué quiere invertir?: ")
salida = ""

for i in range(len(entrada)):
    print(entrada[i])
    salida = entrada[i] + salida

print(salida)

if salida == entrada:
    print("Es un palindromo 😯")
else:
    print("No es palindromo, obviamente")