#Escribir un programa que lea un entero positivo y escriba el mismo número intercalando un “0” entre cada
#cifra. Por ejemplo: 4567 se convierte en 4050607.

numero = input("Ingrese el numero al que le desea intercalar 0: ")
salida = ""

for i in range(len(numero)):
    if i < int(len(numero))-1:
        salida = salida + numero[i] + "0"
    else: 
        salida = salida + numero[i]
print(salida)