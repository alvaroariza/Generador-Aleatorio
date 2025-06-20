import numpy as np
import sympy
from sympy.parsing.sympy_parser import parse_expr

def evaluar_aceptacion_rechazo(formula_str, a, b, n=50):
    """
    Realiza el método de Aceptación-Rechazo para generar variables aleatorias.
    """
    x = sympy.symbols('x')
    
    try:
        # Reemplazar caracteres para compatibilidad con sympy y evaluar la fórmula
        safe_replacements = {'e': str(np.e), 'pi': str(np.pi), '^': '**'}
        for old, new in safe_replacements.items():
            formula_str = formula_str.replace(old, new)
        
        f_expr = parse_expr(formula_str, local_dict={"x": x})
        f = sympy.lambdify(x, f_expr, 'numpy')
    except (sympy.SympifyError, SyntaxError, TypeError) as e:
        return {"error": f"Error en la sintaxis de la fórmula: {e}"}

    # Averiguar M (máximo de f(x) en [a, b])
    try:
        puntos_x = np.linspace(a, b, 2000) # Evaluar en 2000 puntos para una buena aproximación
        puntos_y = f(puntos_x)
        # Asegurarse de que no haya valores infinitos o NaN
        if not np.all(np.isfinite(puntos_y)):
            return {"error": "La función resulta en valores no finitos (inf o NaN) en el intervalo."}
        M = np.max(puntos_y)
        if M <= 0:
            return {"error": "El valor máximo de f(x) en el intervalo debe ser positivo."}
    except Exception as e:
        return {"error": f"No se pudo evaluar f(x) en el intervalo: {e}"}
    
    # Generar números aleatorios y realizar cálculos
    r1 = np.random.rand(n)
    r2 = np.random.rand(n)
    vax = a + (b - a) * r1
    fx_vax = f(vax)
    
    # Condición de aceptación
    aceptados_mask = r2 <= (fx_vax / M)
    
    # Construir tabla de resultados
    tabla = []
    variables_aceptadas = []
    for i in range(n):
        aceptado = bool(aceptados_mask[i])
        tabla.append({
            "r1": r1[i], "r2": r2[i], "vax": vax[i], "fx_vax": fx_vax[i],
            "fx_vax_div_M": fx_vax[i] / M if M != 0 else 0,
            "aceptado": "Sí" if aceptado else "No"
        })
        if aceptado:
            variables_aceptadas.append(vax[i])
            
    return {
        "tabla": tabla,
        "variables_aceptadas": variables_aceptadas,
        "M": float(M), "a": a, "b": b,
        "n_generados": n, "n_aceptados": len(variables_aceptadas)
    } 