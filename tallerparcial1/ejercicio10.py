rango = int(input("Ingrese el rango de números a evaluar: "))
primos = []

if rango <=1:
    print("pues ninguno we")

for n in range(2,rango+1):
    primo = True
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            primo = False
            break

    if primo:
        primos.append(n)

if rango > 1:
    print(f"Los números primos entre 0 y {rango} son: \n{primos} \nSon {len(primos)} y el mayor es {max(primos)}")
        