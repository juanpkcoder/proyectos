# Solicitar al usuario que ingrese un número y muestre su tabla de multiplicar del 1 al 10

numero = int(input("Ingrese un numero: "))
i = 1
while i <= 10:
    print(numero, "x", i, "=", numero * i)
    i += 1