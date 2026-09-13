import numpy as np

M = np.array([[1.0,2.0,3.0],[4.0,5.0,6.0]])

print(M)
print(M.shape)
print(len(M))

filas, columnas = M.shape

for i in range (filas):
    for j in range (columnas):
        print(M[i,j],end=", ")

