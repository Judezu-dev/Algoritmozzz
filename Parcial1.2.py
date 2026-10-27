n = int(input("Ingrese hasta que número contaremos los primos: "))
primos = 0

if n <=1:
    print("pues ninguno we") #El 1 no es primo :v

for i in range(2,n+1): 
    primo = True
    for j in range(2, int(i**0.5) + 1): #Comprobamos hasta la raiz cuadrada del numero, ya que el resto no son necesarios
        if i % j == 0: 
            primo = False
            break #Si encuentra un j entre el rango que genere residuo 0, se acaba inmediatamente el bucle y ya no es primo.

    if primo:
        primos += 1

if n > 1:
    print(f"Hay {primos} numeros primos menores o iguales a {n}")