from flask import Flask, render_template_string
import random

app = Flask(__name__)

# ---------------------
# SIMULAÇÃO DE DADOS
# ---------------------
def simular_relatorio_semana():
    return {
        "temp_critica": random.randint(2, 15),
        "energia_total": round(random.uniform(20, 60), 2)
    }

def simular_relatorio_ontem():
    return {
        "temp_critica": random.randint(0, 5),
        "energia_total": round(random.uniform(3, 10), 2)
    }

def simular_grafico_hoje():
    horas = list(range(24))
    temp = [round(random.uniform(20, 70), 2) for _ in horas]
    pot = [round(random.uniform(50, 300), 2) for _ in horas]
    return horas, temp, pot


# ---------------------
# HTML COM TEMA ROXO E TELA CENTRALIZADA
# ---------------------

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dados de Segurança e Economia</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #2d0b47; /* Roxo escuro */
            color: white;
            height: 100vh;

            /* Esta linha que centralizava tudo e bloqueava os outros elementos */
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .center-container {
            text-align: center;
        }

        h1 {
            font-size: 32px;
        }

        button {
            padding: 12px 28px;
            font-size: 18px;
            background: #9b4de0;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: 0.2s;
        }

        button:hover {
            background: #b174f5;
        }

        #conteudo {
            display: none;
            width: 90%;
            max-width: 1100px;
            margin: 40px auto;
        }

        .cards-container {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-bottom: 30px;
        }

        .card {
            flex: 1;
            background: #3c1361;
            padding: 20px;
            border-radius: 12px;
            min-width: 250px;
        }

        .grafico {
            background: #3c1361;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>

    <div class="center-container" id="inicio">
        <h1>Dados de Segurança e Economia</h1>
        <button onclick="mostrarConteudo()">Iniciar</button>
    </div>

    <div id="conteudo">

        <div class="cards-container">
            <div class="card">
                <h2>Relatório da Semana</h2>
                <p>🔺 Temperatura acima do crítico: <b>0 vezes</b></p>
                <p>⚡ Gasto total de energia: <b>0 kWh</b></p>
            </div>

            <div class="card">
                <h2>Relatório de Ontem</h2>
                <p>🔺 Temperatura acima do crítico: <b>0 vezes</b></p>
                <p>⚡ Gasto total de energia: <b>0 kWh</b></p>
            </div>
        </div>

        <div class="grafico">
            <h2>Gráfico de Hoje</h2>
            <canvas id="graficoHoje"></canvas>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
        function mostrarConteudo() {
            // Oculta título e botão
            document.getElementById("inicio").style.display = "none";

            // Remove o flex que centralizava tudo
            document.body.style.display = "block";

            // Mostra o conteúdo
            document.getElementById("conteudo").style.display = "block";

            gerarGrafico();
        }

        function gerarGrafico() {
            const ctx = document.getElementById('graficoHoje').getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['00h', '03h', '06h', '09h', '12h', '15h', '18h', '21h'],
                    datasets: [
                        {
                            label: 'Temperatura (°C)',
                            data: [20, 22, 25, 27, 30, 28, 26, 23],
                            borderColor: '#c77dff',
                            borderWidth: 2
                        },
                        {
                            label: 'Consumo (W)',
                            data: [10, 12, 16, 20, 24, 23, 18, 15],
                            borderColor: '#9d4edd',
                            borderWidth: 2
                        }
                    ]
                },
                options: {
                    responsive: true
                }
            });
        }
    </script>

</body>
</html>
"""

# ---------------------
# ROTA PRINCIPAL
# ---------------------
@app.route("/")
def index():
    semana = simular_relatorio_semana()
    ontem = simular_relatorio_ontem()
    horas, temp, pot = simular_grafico_hoje()

    return render_template_string(
        HTML,
        semana=semana,
        ontem=ontem,
        horas=horas,
        temperaturas=temp,
        potencias=pot
    )

if __name__ == "__main__":
    app.run(debug=True)
