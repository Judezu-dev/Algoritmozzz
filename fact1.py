numero = int(input("Número al cual se le quiere sacar el factorial: "))

fact = 1

while numero > 0:
    fact = fact * numero
    numero = numero - 1
print(f"El factorial es: {fact}")