from collections import Counter
import math

def calcular_entropia(numeros, bins=10):
    """
    Calcula la Entropía de Shannon para una secuencia de números.
    """
    if not numeros:
        return {
            "entropia": 0,
            "max_entropia": math.log2(bins) if bins > 0 else 0,
            "bins": bins
        }

    # Agrupa los números en 'bins' (intervalos/clases)
    etiquetas = [int(n * bins) for n in numeros]
    conteo = Counter(etiquetas)
    
    total = sum(conteo.values())
    
    # Calcula la probabilidad de cada clase
    probabilidades = [f / total for f in conteo.values()]
    
    # Calcula la entropía. Se excluyen probabilidades de 0 para evitar errores matemáticos.
    entropia = -sum(p * math.log2(p) for p in probabilidades if p > 0)
    
    # La entropía máxima teórica es log2 del número de clases
    max_entropia = math.log2(bins)

    return {
        "entropia": entropia,
        "max_entropia": max_entropia,
        "bins": bins
    } 