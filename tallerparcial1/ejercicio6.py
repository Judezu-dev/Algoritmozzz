#varianza

num = int(input("Cantidad de elementos: "))
numeros = []
for i in range(num):
    numeros.append(int(input("Elemento: ")))

media = sum(numeros)/num

suma = 0
for i in numeros:
    suma += (i-media)**2

print(suma/(num))

#Este codigo calcula la varianza poblacional, debido a que usa todos los datos y el denominador de la suma es n, no (n-1), que corresponde a la varianza muestral, que no necesita de todos los datos del conjunto, pero si necesita de la correcion de Bessel