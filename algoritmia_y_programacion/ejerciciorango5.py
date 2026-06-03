# Calcular promedio de notas
cantidad = int(input("Ingresa la cantidad de notas a registrar (ejem: 5): "))
suma = 0

for i in range(1, cantidad + 1):
    nota = float(input(f"Ingresa la nota {i}: "))
    suma += nota

promedio = suma / cantidad
print("El promedio general es:", promedio)
