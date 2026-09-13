n = int(input("Ingrese un número: "))
primo = True

if n <= 1:
    print(f"{n} no es primo")

for i in range(2, int(n**0.5)+1):
    if n % i == 0:
        primo = False
        break
if primo:
    print(f"{n} es primo")
else:
    print(f"{n} no es primo")