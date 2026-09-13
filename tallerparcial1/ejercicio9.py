#Aproximación de pi con criterio de tolerancia
import math as m

tolerancia = float(input("Ingrese el valor de la tolerancia: "))
n = 1
pedro = 1
serie = 0
terminos = 0

while 1/n > tolerancia:
    serie += ((-1)**(pedro + 1))*1/n
    n += 2
    pedro += 1
    terminos += 1

pi = 4 * serie

error_porcentual = (m.pi - pi)/m.pi * 100
print(f"La aproximación mediante leibniz da: {pi}")
print(f"Se usaron {terminos} terminos")
print(f"El error porcentual es de {error_porcentual}%")

#A medida que la tolerancia disminuye de forma 10**-n, los terminos necesarios son 5 * 10**n