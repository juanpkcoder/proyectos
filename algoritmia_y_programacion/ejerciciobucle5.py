# adivina el numero
import random
numero = random.randint(1, 10)
intentos = 0
while True:
    intentos += 1
    adivinanza = int(input("adivina el numero: "))
    if adivinanza == numero:
        print("adivinaste el numero en", intentos, "intentos")
        break
    elif adivinanza < numero:
        print("el numero es mayor")
    else:
        print("el numero es menor")