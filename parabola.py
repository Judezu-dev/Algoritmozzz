import numpy as np
import math as m
import matplotlib.pyplot as plt

ay = -9.8
v_0 = 40
ang = m.radians(45)
vx_0 = v_0 * m.cos(ang)
vy_0 = v_0 * m.sin(ang)
y0 = 20
x0 = 0

n = 1000
pos_x = np.zeros(n)
pos_y = np.zeros(n)

t = 0
t_max = 100
dt = (t_max - t) / n

vy = vy_0
x = x0
y = y0

i = 0
while t < t_max and y>=0:
    vy = vy + ay * dt
    y = y + vy * dt
    x = x + vx_0 * dt

    pos_x[i] = x 
    pos_y[i] = y

    t += dt
    i += 1

print(pos_x, pos_y)
plt.plot(pos_x[:i], pos_y[:i], "r-")
plt.grid("on")
plt.show()