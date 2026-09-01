print("describe de donde hasta donde desea evaluar la integral de x al cuadrado mediante aproximacion de sumas de riemann, desde a hasta b, y un delta de x")
a = int(input("Ingresa el valor de a: "))
b = int(input("Ingresa el valor de b: "))
n = int(input("número de rectangulos o barras: "))
delta = (b-a)/n

suma = 0
#serie de riemann
for i in range(n):
    x = a + i * delta
    y = x**2
    suma = suma + y * delta

print(f"La integral definida desde {a} hasta {b} de x al cuadrado mediante aproximacion de sumas de riemann es {suma}")


