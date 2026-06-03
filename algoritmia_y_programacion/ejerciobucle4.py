#cuenta regresiva desde 50 hasta 0 de 5 en 5 y muestra "boom"

from time import sleep

numero = 50
while numero > 0:
    print(numero)
    sleep(1)
    numero -= 5
print("¡boom!")