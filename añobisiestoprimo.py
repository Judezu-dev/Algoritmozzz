año = int(input ("Introduce el año: "))

if año % 4 == 0 and año % 100 != 0 or año % 400 == 0:
     print ("El año es bisiesto")
else :
    print ("El año no es bisiesto")

def es_primo(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

if es_primo(año):
    print("El año es primo")
else:
    print("El año no es primo")