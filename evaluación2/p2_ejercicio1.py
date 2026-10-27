def procesar_caracter(c, salto, modo):
    """Cifra o descifra un solo carácter respetando mayúsculas y minúsculas."""
    if not c.isalpha():
        return c

    s = salto if modo == "C" else -salto

    if c.isupper():
        base = ord("A")
        return chr((ord(c) - base + s) % 26 + base)
    elif c.islower():
        base = ord("a")
        return chr((ord(c) - base + s) % 26 + base)

    return c


def procesar_frase(modo, frase):
    resultado = []
    i = 0
    indice_palabra = 0
    n = len(frase)

    while i < n:
        if not frase[i].isalpha():
            resultado.append(frase[i])
            i += 1
        else:
            salto = 3 if indice_palabra % 2 == 0 else 4

            while i < n and frase[i].isalpha():
                resultado.append(procesar_caracter(frase[i], salto, modo))
                i += 1

            indice_palabra += 1

    return "".join(resultado)


def main():
    try:
        
        modo = input("Ingresa C para Cifrar y D para Descifrar: ")
        
        frase = input("Ingresa la frase que pasará por el cifrado César con saltos de 3 y 4 letras, pero no te diré cuál es cuál 😺: ")

        # Validación del modo de operación
        if modo not in ("C", "D"):
            print("Error: El modo debe ser 'C' (cifrar) o 'D' (descifrar).")
            return
        
        print(procesar_frase(modo, frase))
    except EOFError:
        # Maneja casos donde la entrada esté vacía o finalice inesperadamente
        print("...")
        pass

main()