# solicitar al usuario numeros hasta q ingrese cero y muestre la suma total

suma = 0
numero = 1
while numero != 0:
    numero = int(input("Ingrese un numero: "))
    suma = suma + numero
print("La suma total es: ", suma)