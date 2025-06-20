import numpy as np
from scipy.stats import chi2

def validar_chi_cuadrada(numeros, intervalos=5, alpha=0.05):
    # Divide el rango [0,1) en 'intervalos' partes iguales
    bins = np.linspace(0, 1, intervalos + 1)
    FO, _ = np.histogram(numeros, bins)
    FE = len(numeros) / intervalos

    # Calcula estadístico chi-cuadrado
    chi2_stat = np.sum((FO - FE) ** 2 / FE)
    gl = intervalos - 1
    valor_critico = chi2.ppf(1 - alpha, gl)

    # Resultado
    cumple = chi2_stat < valor_critico
    return {
        "FO": FO,
        "FE": FE,
        "chi2_stat": chi2_stat,
        "valor_critico": valor_critico,
        "gl": gl,
        "cumple": cumple
    }