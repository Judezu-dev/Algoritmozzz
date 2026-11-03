import math

# Límite superior para los factores primos necesarios: sqrt(2^31 - 1) ≈ 46340
LIMITE_PRIMOS = 46341


def generar_criba():
    """Genera una lista de números primos hasta LIMITE_PRIMOS usando la Criba de Eratóstenes."""
    es_primo = [True] * LIMITE_PRIMOS
    es_primo[0] = es_primo[1] = False

    for i in range(2, int(math.isqrt(LIMITE_PRIMOS)) + 1):
        if es_primo[i]:
            for j in range(i * i, LIMITE_PRIMOS, i):
                es_primo[j] = False

    return [i for i, primo in enumerate(es_primo) if primo]


def calcular_b_minimo(a, primos):
    """Encuentra el menor B tal que A * B sea un cuadrado perfecto."""
    b = 1
    temp_a = a

    for p in primos:
        # Optimización: si p * p > temp_a, temp_a ya es un número primo o 1
        if p * p > temp_a:
            break

        if temp_a % p == 0:
            conteo = 0
            while temp_a % p == 0:
                conteo += 1
                temp_a //= p

            # Si el exponente del factor primo es impar, multiplicamos B por p
            if conteo % 2 != 0:
                b *= p

    # Si queda un residuo mayor a 1, ese residuo es un primo con exponente 1 (impar)
    if temp_a > 1:
        b *= temp_a

    return b


# Precomputar la criba de primos una sola vez
primos = generar_criba()


try:
    t = int(input("T = " ).strip())
    for _ in range(t):
        a = int(input("A = ").strip())
        print(f'B = {calcular_b_minimo(a, primos)}')
except (EOFError, ValueError):
    pass