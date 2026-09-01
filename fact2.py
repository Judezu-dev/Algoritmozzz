numero = int(input("Número al cual se le quiere sacar el factorial: "))

fact = 1
i = 1

while i <= numero:
    fact = fact * i
    i = i + 1
print(f"El factorial es: {fact}")