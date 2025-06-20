from flask import Flask, render_template, request, jsonify
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from generadorNumeros import (
    generador_mixto, generador_multiplicativo,
    evaluar_ciclo_completo_mixto, explicar_raiz_primitiva,
    obtener_longitud_periodo, generar_desde_entropy_sistema
)
from chi_cuadrada import validar_chi_cuadrada
from distribucion_empirica import calcular_distribuciones
from kolmogorov_smirnov import validar_kolmogorov_smirnov
from shannon_entropy import calcular_entropia
from aceptacion_rechazo import evaluar_aceptacion_rechazo

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    if not request.is_json:
        return jsonify({"error": "Se requiere JSON"}), 400
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos JSON vacíos"}), 400
    
    tipo = data['tipo']
    cantidad = int(data['cantidad'])
    
    if tipo == 'mixto':
        a = int(data['a'])
        b = int(data['b'])
        m = int(data['m'])
        semilla = int(data['semilla'])
        numeros = generador_mixto(a, b, m, semilla, cantidad)
        periodo = obtener_longitud_periodo(a, b, m, semilla, es_mixto=True)
        ciclo_completo, explicaciones = evaluar_ciclo_completo_mixto(a, b, m)
        resultado = {
            'numeros': numeros,
            'periodo': periodo,
            'ciclo_completo': ciclo_completo,
            'explicaciones': explicaciones
        }
    elif tipo == 'multiplicativo':
        a = int(data['a'])
        m = int(data['m'])
        semilla = int(data['semilla'])
        numeros = generador_multiplicativo(a, m, semilla, cantidad)
        periodo = obtener_longitud_periodo(a, 0, m, semilla, es_mixto=False)
        es_maximo, explicaciones = explicar_raiz_primitiva(a, m)
        resultado = {
            'numeros': numeros,
            'periodo': periodo,
            'es_maximo': es_maximo,
            'explicaciones': explicaciones
        }
    elif tipo == 'sistema':
        numeros = generar_desde_entropy_sistema(cantidad)
        resultado = {
            'numeros': numeros,
            'periodo': 'N/A',
            'explicaciones': ["Generador basado en la entropía del sistema (fuente física). No es pseudoaleatorio y no tiene un período predecible."]
        }
    
    return jsonify(resultado)

@app.route('/validar', methods=['POST'])
def validar():
    try:
        if not request.is_json:
            return jsonify({"error": "Se requiere JSON"}), 400
        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos JSON vacíos"}), 400
        print("Datos recibidos en /validar:", data)  # Depuración

        numeros = data.get('numeros')
        intervalos = int(data.get('intervalos', 0))
        alpha = float(data.get('alpha', 0.05))

        if not numeros or not isinstance(numeros, list):
            return jsonify({"error": "Lista de números inválida"}), 400
        if intervalos not in [2, 5]:
            return jsonify({"error": "Intervalos debe ser 2 o 5"}), 400

        # --- Validación Chi-cuadrada ---
        resultado_chi = validar_chi_cuadrada(numeros, intervalos, alpha)
        resultado_chi['FO'] = resultado_chi['FO'].tolist()
        resultado_chi['chi2_stat'] = float(resultado_chi['chi2_stat'])
        resultado_chi['valor_critico'] = float(resultado_chi['valor_critico'])
        resultado_chi['cumple'] = bool(resultado_chi['cumple'])
        
        # --- Validación Kolmogorov-Smirnov ---
        resultado_ks = validar_kolmogorov_smirnov(numeros, alpha)

        # --- Test de Entropía ---
        # Usamos los mismos intervalos que en Chi-cuadrada como "bins" para la entropía
        resultado_entropia = calcular_entropia(numeros, bins=intervalos)

        # Calcular distribución empírica
        paso = 1 / intervalos
        intervalos_lista = []
        for i in range(intervalos):
            lim_inf = round(i * paso, 4)
            lim_sup = round((i + 1) * paso, 4)
            intervalos_lista.append((lim_inf, lim_sup))

        frecuencias = list(resultado_chi["FO"])
        tabla = calcular_distribuciones(frecuencias, intervalos_lista)

        # Generar gráficos
        plt.figure(figsize=(10, 4))
        etiquetas = [f"{a}-{b}" for a, b in intervalos_lista]
        plt.subplot(1, 2, 1)
        plt.bar(etiquetas, tabla["probabilidades"], color='skyblue')
        plt.title("Distribución de PROBABILIDAD")
        plt.ylim(0, max(tabla["probabilidades"]) + 0.1)
        plt.xlabel("Intervalo")
        plt.ylabel("Probabilidad")
        plt.xticks(rotation=45, ha='right', fontsize=8)

        plt.subplot(1, 2, 2)
        plt.plot(etiquetas, tabla["acumulada"], marker='o', color='orange')
        plt.title("Distribución ACUMULATIVA")
        plt.ylim(0, 1.1)
        plt.xlabel("Intervalo")
        plt.ylabel("Acumulada")
        plt.xticks(rotation=45, ha='right', fontsize=8)

        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()

        grafico_base64 = base64.b64encode(image_png).decode()

        return jsonify({
            'chi_cuadrada': resultado_chi,
            'kolmogorov_smirnov': resultado_ks,
            'entropia': resultado_entropia,
            'distribucion': tabla,
            'grafico': grafico_base64
        })
    except Exception as e:
        print("Error en /validar:", e)
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route('/generar-variable', methods=['POST'])
def generar_variable():
    if not request.is_json:
        return jsonify({"error": "Se requiere JSON"}), 400
    
    data = request.get_json()
    metodo = data.get('metodo')
    formula = data.get('formula')
    resultado = {}
    
    if metodo == 'rechazo':
        try:
            a = float(data.get('a'))
            b = float(data.get('b'))
            n = int(data.get('n'))
            if n <= 0:
                return jsonify({"error": "La cantidad debe ser un número positivo."}), 400
            resultado = evaluar_aceptacion_rechazo(formula, a, b, n)
            if 'error' not in resultado:
                resultado['metodo'] = 'rechazo'
        except (ValueError, TypeError):
            return jsonify({"error": "Parámetros a, b o n inválidos."}), 400
    else:
        resultado = {"error": "Método no reconocido."}
        
    return jsonify(resultado)

@app.route('/variableAleatoria')
def variable_aleatoria_page():
    return render_template('variable_aleatoria.html')

if __name__ == '__main__':
    app.run(debug=True) 