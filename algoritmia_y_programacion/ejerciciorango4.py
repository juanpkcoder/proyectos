import random
numero_secreto = random.randint(1, 10)
intentos = 3
print("He pensado en un número entre 1 y 10. ¡Tienes 3 intentos para adivinarlo!")
for intento in range(1, intentos + 1):
    try:
        adivinanza = int(input(f"Intento {intento}: Ingresa tu número: "))
    except ValueError:
        print("Por favor, ingresa un número entero válido.")
        continue
    if adivinanza == numero_secreto:
        print("¡Felicidades! Has adivinado el número.")
        break
    else:
        if intento < intentos:
            if adivinanza < numero_secreto:
                print("Incorrecto. El número es mayor.")
            else:
                print("Incorrecto. El número es menor.")
        else:
            print(f"Lo siento, te has quedado sin intentos. El número era {numero_secreto}.")
