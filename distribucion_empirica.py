def calcular_distribuciones(frecuencias, intervalos):
    total = sum(frecuencias)
    probabilidades = [f / total for f in frecuencias]
    acumulada = []
    suma = 0
    for p in probabilidades:
        suma += p
        acumulada.append(suma)
    return {
        "intervalos": intervalos,
        "frecuencias": frecuencias,
        "probabilidades": probabilidades,
        "acumulada": acumulada
    }