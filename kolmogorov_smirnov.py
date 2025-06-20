import numpy as np
from scipy.stats import ksone

def validar_kolmogorov_smirnov(numeros, alpha):
    """
    Realiza la prueba de bondad de ajuste de Kolmogorov-Smirnov para una distribución uniforme.
    Sigue los pasos especificados por el usuario.
    """
    n = len(numeros)
    if n == 0:
        return None

    # 1. Ordenar los números de menor a mayor
    numeros_ordenados = sorted(numeros)
    
    # 2-4. Construir la tabla con los cálculos
    tabla_ks = []
    diferencias = []
    for i, y in enumerate(numeros_ordenados, 1):
        i_n = i / n
        dif = abs(y - i_n)
        diferencias.append(dif)
        tabla_ks.append({
            "indice": i,
            "numero": round(y, 4),
            "i_n": round(i_n, 4),
            "dif": round(dif, 4)
        })

    # 5. Averiguar el máximo de la columna de valores absolutos
    d_max = max(diferencias)

    # 6. Averiguar en la tabla KS el valor crítico
    # Usamos scipy para obtener el valor crítico de la tabla KS para una prueba de dos colas.
    valor_critico = ksone.ppf(1 - (alpha / 2), n)

    # 7. Si el máximo obtenido es menor al valor encontrado en la tabla se acepta la hipótesis
    cumple = d_max < valor_critico

    return {
        "tabla": tabla_ks,
        "d_max": float(d_max),
        "valor_critico": float(valor_critico),
        "cumple": bool(cumple),
        "n": n,
        "alpha": alpha
    } 