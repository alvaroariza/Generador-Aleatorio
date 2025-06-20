document.addEventListener('DOMContentLoaded', function() {
    const formulaInput = document.getElementById('formula');
    const keyboard = document.getElementById('virtual-keyboard');
    const generateBtn = document.getElementById('generate');

    // Lógica del teclado
    keyboard.addEventListener('click', function(e) {
        if (e.target.tagName !== 'BUTTON' && !e.target.closest('button')) return;
        const button = e.target.closest('button');
        if (button.id === 'generate') return; // La lógica de generar está abajo

        const key = button.dataset.key;
        const id = button.id;
        
        if (!key && !id) return;
        let currentValue = formulaInput.value;

        if (id === 'backspace') formulaInput.value = currentValue.slice(0, -1);
        else if (id === 'clear') formulaInput.value = '';
        else if (key) formulaInput.value += key;
    });

    // Lógica del botón Generar
    generateBtn.addEventListener('click', async function() {
        const formula = formulaInput.value;
        const a = document.getElementById('intervalo_a').value;
        const b = document.getElementById('intervalo_b').value;
        const n = document.getElementById('cantidad_va').value;

        if (!formula) {
            alert('Por favor, ingrese una fórmula.');
            return;
        }

        if (a === '' || b === '' || n === '') {
            alert('Por favor, complete los campos de intervalo y cantidad.');
            return;
        }
        if (parseFloat(a) >= parseFloat(b)) {
            alert('El inicio del intervalo (a) debe ser menor que el final (b).');
            return;
        }

        const body = { metodo: 'rechazo', formula, a, b, n };
        
        try {
            const response = await fetch('/generar-variable', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            displayResults(data);
        } catch (error) {
            console.error('Error en la petición:', error);
            alert('Ocurrió un error al contactar al servidor.');
        }
    });

    function displayResults(data) {
        const resultsContainer = document.getElementById('va-results');
        let html = 'Esperando generación...';

        if (data.metodo === 'rechazo') {
            const eficiencia = (data.n_aceptados / data.n_generados) * 100;
            html = `
                <h6>Resultados (Aceptación-Rechazo)</h6>
                <div class="explicacion-item">Valor de M (máximo): <strong>${data.M.toFixed(4)}</strong></div>
                <div class="explicacion-item">Aceptados: <strong>${data.n_aceptados} de ${data.n_generados}</strong> (${eficiencia.toFixed(1)}%)</div>
                
                <h6 class="mt-3">Tabla de Simulación:</h6>
                <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                    <table class="table table-sm table-hover">
                        <thead><tr><th>r1</th><th>r2</th><th>VAX</th><th>f(VAX)</th><th>f(VAX)/M</th><th>Aceptado</th></tr></thead>
                        <tbody>`;
            data.tabla.forEach(row => {
                html += `<tr>
                    <td>${row.r1.toFixed(4)}</td><td>${row.r2.toFixed(4)}</td><td>${row.vax.toFixed(4)}</td>
                    <td>${row.fx_vax.toFixed(4)}</td><td>${row.fx_vax_div_M.toFixed(4)}</td>
                    <td><span class="badge bg-${row.aceptado === 'Sí' ? 'success' : 'danger'}">${row.aceptado}</span></td>
                </tr>`;
            });
            html += '</tbody></table></div>';
            
            if (data.variables_aceptadas.length > 0) {
                html += `<h6 class="mt-3">Variables Aceptadas:</h6><div class="numeros-generados">${data.variables_aceptadas.map(v => v.toFixed(4)).join(', ')}</div>`;
            }
        }
        resultsContainer.innerHTML = html;
    }
}); 