let numerosGenerados = [];

// Manejar cambio de tipo de generador
document.querySelectorAll('input[name="tipo"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const bContainer = document.getElementById('b-container');
        if (this.value === 'multiplicativo') {
            bContainer.style.display = 'none';
            document.getElementById('b').value = '0';
        } else {
            bContainer.style.display = 'block';
        }
    });
});

async function generarNumeros() {
    const tipo = document.querySelector('input[name="tipo"]:checked').value;
    const a = document.getElementById('a').value;
    const b = document.getElementById('b').value;
    const m = document.getElementById('m').value;
    const semilla = document.getElementById('semilla').value;
    const cantidad = document.getElementById('cantidad').value;

    if (!a || !m || !semilla || !cantidad || (tipo === 'mixto' && !b)) {
        alert('Por favor complete todos los campos requeridos');
        return;
    }

    try {
        const response = await fetch('/generar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tipo,
                a,
                b,
                m,
                semilla,
                cantidad
            })
        });

        const data = await response.json();
        numerosGenerados = data.numeros;
        
        // Mostrar resultados
        let html = `
            <h6>Números generados:</h6>
            <div class="numeros-generados">${numerosGenerados.join(', ')}</div>
            <h6 class="mt-3">Análisis del generador:</h6>
            <div class="explicacion-item">
                <i class="fas fa-sync"></i> Longitud del período: ${data.periodo}
            </div>`;

        if (tipo === 'mixto') {
            html += `
                <div class="explicacion-item">
                    <i class="fas fa-check-circle"></i> ¿Es ciclo completo?: ${data.ciclo_completo ? 'Sí' : 'No'}
                </div>`;
        } else {
            html += `
                <div class="explicacion-item">
                    <i class="fas fa-check-circle"></i> ¿Tiene longitud máxima (m-1 = ${m-1})?: ${data.periodo === m-1 ? 'Sí' : 'No'}
                </div>`;
        }

        html += '<h6 class="mt-3">Explicación:</h6>';
        data.explicaciones.forEach(exp => {
            html += `<div class="explicacion-item">${exp}</div>`;
        });

        document.getElementById('resultados-generacion').innerHTML = html;
        document.getElementById('btn-validar').disabled = false;
        document.getElementById('resultados-validacion').innerHTML = '';
        document.getElementById('graficos').innerHTML = '';

    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar los números');
    }
}

async function validarNumeros() {
    if (numerosGenerados.length === 0) {
        alert('Primero debe generar números');
        return;
    }

    const intervalos = document.getElementById('intervalos').value;
    const alpha = document.getElementById('alpha').value;

    try {
        const response = await fetch('/validar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                numeros: numerosGenerados,
                intervalos: parseInt(intervalos),
                alpha: parseFloat(alpha)
            })
        });

        const data = await response.json();

        if (data.error) {
            alert("Error del servidor: " + data.error);
            return;
        }
        
        // Mostrar resultados de chi-cuadrada
        let html = `
            <h6>Resultados de la prueba Chi-cuadrada:</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Intervalo</th>
                            <th>FO</th>
                            <th>FE</th>
                        </tr>
                    </thead>
                    <tbody>`;

        for (let i = 0; i < data.chi_cuadrada.FO.length; i++) {
            html += `
                <tr>
                    <td>${i+1}</td>
                    <td>${data.chi_cuadrada.FO[i]}</td>
                    <td>${data.chi_cuadrada.FE.toFixed(2)}</td>
                </tr>`;
        }

        html += `
                    </tbody>
                </table>
            </div>
            <div class="explicacion-item">
                <i class="fas fa-calculator"></i> Chi2 calculado: ${data.chi_cuadrada.chi2_stat.toFixed(4)}
            </div>
            <div class="explicacion-item">
                <i class="fas fa-chart-line"></i> Valor crítico (gl=${data.chi_cuadrada.gl}, α=${alpha}): ${data.chi_cuadrada.valor_critico.toFixed(4)}
            </div>
            <div class="explicacion-item">
                <i class="fas fa-check-circle"></i> ¿Cumple la prueba?: ${data.chi_cuadrada.cumple ? 'Sí' : 'No'}
            </div>`;

        // Mostrar distribución empírica
        html += `
            <h6 class="mt-4">Distribución empírica:</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Intervalo</th>
                            <th>Frecuencia</th>
                            <th>Probabilidad</th>
                            <th>Acumulada</th>
                        </tr>
                    </thead>
                    <tbody>`;

        for (let i = 0; i < data.distribucion.intervalos.length; i++) {
            html += `
                <tr>
                    <td>${data.distribucion.intervalos[i][0]}-${data.distribucion.intervalos[i][1]}</td>
                    <td>${data.distribucion.frecuencias[i]}</td>
                    <td>${data.distribucion.probabilidades[i].toFixed(2)}</td>
                    <td>${data.distribucion.acumulada[i].toFixed(2)}</td>
                </tr>`;
        }

        html += `
                    </tbody>
                </table>
            </div>`;

        document.getElementById('resultados-validacion').innerHTML = html;
        
        // Mostrar resultados de Kolmogorov-Smirnov
        if (data.kolmogorov_smirnov) {
            const ks = data.kolmogorov_smirnov;
            let ksHtml = `
                <h6 class="mt-4">Resultados de la prueba Kolmogorov-Smirnov:</h6>
                <div class="explicacion-item">
                    <i class="fas fa-calculator"></i> Dmax calculado: ${ks.d_max.toFixed(4)}
                </div>
                <div class="explicacion-item">
                    <i class="fas fa-chart-line"></i> Valor crítico (n=${ks.n}, α=${ks.alpha}): ${ks.valor_critico.toFixed(4)}
                </div>
                <div class="explicacion-item">
                    <i class="fas fa-check-circle"></i> ¿Cumple la prueba?: ${ks.cumple ? 'Sí' : 'No'}
                </div>
                <h6 class="mt-3">Tabla de cálculo KS:</h6>
                <div class="table-responsive" style="max-height: 250px; overflow-y: auto;">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>i</th>
                                <th>Y(i)</th>
                                <th>i/n</th>
                                <th>|Y(i) - i/n|</th>
                            </tr>
                        </thead>
                        <tbody>`;
            
            ks.tabla.forEach(row => {
                ksHtml += `
                    <tr>
                        <td>${row.indice}</td>
                        <td>${row.numero}</td>
                        <td>${row.i_n}</td>
                        <td>${row.dif}</td>
                    </tr>`;
            });

            ksHtml += `
                        </tbody>
                    </table>
                </div>`;
            document.getElementById('resultados-ks').innerHTML = ksHtml;
        }

        // Mostrar gráficos
        document.getElementById('graficos').innerHTML = `
            <img src="data:image/png;base64,${data.grafico}" alt="Gráficos de distribución">`;

    } catch (error) {
        console.error('Error:', error);
        alert('Error al validar los números');
    }
} 