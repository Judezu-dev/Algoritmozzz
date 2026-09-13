#Construir un programa que lea una frase y la invierta palabra a palabra, y también letra a letra. Para este
#problema consultar la función split().

frase = input("Ingrese la frase que desea invertir palabra a palabra y letra a letra: ")

palabras = frase.split(" ")
salida1 = ""
salida2 = ""

for i in range(len(palabras)):
    salida1 = palabras[i] + " " + salida1
print(salida1)

for i in range(len(frase)):
    salida2 = frase[i] + salida2
print(salida2)