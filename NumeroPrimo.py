n = int(input("Ingrese un número: "))

def es_primo(n):
    if n <= 1:
        return False
    # Comprobamos hasta la raíz cuadrada de n
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

if es_primo(n):
    print(f"{n} es un número primo.")
else:
    print(f"{n} no es un número primo.")