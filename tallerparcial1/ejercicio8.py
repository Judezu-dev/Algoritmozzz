#Construir un programa que lea las longitudes de los tres lados de un triángulo y determine, en primer lugar,
#si esos tres valores pueden formar realmente un triángulo
import math as m
print("Ingresa los valores de tus lados")

a = int(input("Lado a: "))
while a <= 0:
    print("No se aceptan valores menores o iguales a 0")
    a = int(input("Lado a: "))

b = int(input("Lado b: "))
while b <= 0:
    print("No se aceptan valores menores o iguales a 0")
    b = int(input("Lado b: "))

c = int(input("Lado c: "))
while c <= 0:
    print("No se aceptan valores menores o iguales a 0")
    c = int(input("Lado c: "))

lista = [a,b,c]
mayor = max(lista)
lista.remove(mayor)

if sum(lista)>mayor:

    #lados
    print("si se puede burro, si hay triángulo")
    if a == b == c:
        print("Se forma un triángulo equilatero")
    elif a == b != c or b == c !=a or  a == c != b:
        print("Se forma un triángulo isósceles")
    else:
        print("Se forma un triángulo escaleno")


    #ángulos
    A = m.acos(((b**2 + c**2 - a**2)/(2*b*c)))
    B = m.acos(((a**2 + c**2 - b**2)/(2*a*c)))
    C = m.acos(((b**2 + a**2 - c**2)/(2*b*a)))

    angulomax = max(A,B,C)

    if angulomax == m.pi/2:
        print("Y es un triángulo rectángulo")
    elif angulomax > m.pi/2:
        print("Y es un triángulo obtusángulo")
    else:
        print("Y es un triángulo acutángulo") 
else:
    print("yucas, no hay triángulo")




