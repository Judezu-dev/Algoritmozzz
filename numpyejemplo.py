import numpy as np
import matplotlib.pyplot as plt
from time import perf_counter_ns

matriz1 = np.array([[2,0,0],[0,2,0],[0,0,2]])
matriz2 = np.array([[1,2,3],[4,5,6],[7,8,9]])

i = int(input("fila: "))
j = int(input("columna: "))
resultado = matriz1@matriz2

print(matriz1)
print(resultado)
