valor1 = int(input("Ingrese el primer valor: "))
valor2 = int(input("Ingrese el segundo valor: "))

if valor1 == valor2:
    print(f"El mcm es {valor1}")
elif valor1 > valor2:
    for i in range(valor1*valor2, valor1 - 1, -1):
        if i % valor1  == 0 and i % valor2 == 0:
            mcm = i
    print(f"El mcm es {mcm}")
else:
    for i in range(valor1*valor2, valor2 - 1, -1):
        if i % valor1  == 0 and i % valor2 == 0:
            mcm = i
    print(f"El mcm es {mcm}")
