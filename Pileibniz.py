numero_terminos = int(input("Ingrese el número de términos de la serie: "))
suma = 0
i =0
while i <= numero_terminos:
    suma = suma + ((-1)**i) / (2*i + 1)
    i = i+1
print (f"El valor aproximado de pi es: {suma*4}")