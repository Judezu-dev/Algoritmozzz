#Sistema binario
numero = int(input("Ingrese el número que desea pasar a binario: ")) #Para que el usuario ingrese el numero pues

resultado = "" #un string vacío que usaremos para la conversión

while numero > 0: #Evalúa mientras el numero sea mayor que cero, pq en ese momento dejamos de dividir
    resultado = str(numero%2) + resultado #el residuo entre 2 se incorpora, el resultado está a la izquierda pq se va de el ultimo residuo hasta el primero
    numero = numero//2 #Pasamos al siguiente numero a evaluar

print(f"En binario es: \n {resultado}")