#Solicitar al usuario una nota entre 0 y 5. Si ingresa un número fuera del rango, pídele que intente de nuevo

print("ingrese una nota entre 0 y 5")
nota = float(input("ingrese una nota entre 0 y 5: "))
while nota < 0 or nota > 5:
    print("error: la nota debe estar entre 0 y 5")
    nota = float(input("ingrese una nota entre 0 y 5: "))
print("nota valida", nota)

