#Construir un programa que lea un entero positivo n y luego lea un entero positivo b que debe ser menor
#que 10. El programa deberá mostrar la representación del número n en base b.
#Tenga en cuenta que la base más pequeña que tiene sentido es b = 2, de modo que el valor leído debe
#validarse en el rango 2 ≤ b < 10; si está fuera de ese rango, el programa debe informarlo y solicitarlo
#nuevamente.

n = int(input("Ingrese un número entero: "))
b = int(input("Ingrese un entero positivo que servira de base: "))

while b<2 or b>10:
    print("¡El rango de enteros posible va de 2 hasta 10!")
    b = int(input("Ingrese un entero positivo que servira de base: "))

if 2<=b<10:
    numero = ""
    while n > 0:
        numero = str(n%b) + numero
        n = n // b
print(numero)


    

 