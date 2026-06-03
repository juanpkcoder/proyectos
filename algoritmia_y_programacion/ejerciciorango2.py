#contar letras en una palabra
print("señor usuario ingrese una palabra a continuacion:")
palabra = input("ingrese una palabra:")
if palabra.isalpha():
    print("la palabra es una palabra")
else:
    print("la palabra no es una palabra")
    palabra = input("ingrese una palabra con solo letras:")

count=0
for letra in palabra:
    count +=1
print("la palabra tiene", count, "letras")

    