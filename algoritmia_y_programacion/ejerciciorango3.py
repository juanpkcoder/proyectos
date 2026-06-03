#contar vocales de una palabra

palabra = input("ingresa una palabra: ")
vocales = 0
for letra in palabra:
    if letra in "aeiouAEIOU":
        vocales += 1
print("la palabra tiene ", vocales, "vocales")
