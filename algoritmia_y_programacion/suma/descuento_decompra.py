print("descuento de compra")
precio = float(input("ingrese el precio del producto: "))
if precio > 100:
    descuento = precio * 0.1
    precio_final = precio - descuento
    print("el precio final con descuento es: ", precio_final)