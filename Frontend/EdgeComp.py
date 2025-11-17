from flask import Flask, render_template_string
import random

app = Flask(__name__)

# ---------------------
# SIMULAÇÕES
# ---------------------

def simular_relatorio_semana():
    luz_media = random.randint(5, 30)
    return {"ruim": luz_media}

def simular_relatorio_ontem():
    luz_media = random.randint(0, 10)
    return {"ruim": luz_media}

def simular_grafico_hoje():
    horas = ['00h','03h','06h','09h','12h','15h','18h','21h']
    valores = [random.randint(0, 600) for _ in horas]  # agora pode mostrar a faixa crítica
    return horas, valores

# ---------------------
# INTERFACE
# ---------------------

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proteção Contra Luz Azul</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #2d0b47;
            color: white;
            height: 100vh;

            display: flex;
            justify-content: center;
            align-items: center;
        }

        .center-container {
            text-align: center;
        }

        button {
            padding: 12px 28px;
            font-size: 18px;
            background: #9b4de0;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
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
            text-align: center;
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
        <h1>Proteção Contra Luz Azul</h1>
        <button onclick="mostrarConteudo()">Iniciar</button>
    </div>

    <div id="conteudo">

        <div class="cards-container">
            <div class="card">
                <h2>Relatório da Semana</h2>
                <p>⚠ Somente Luz Azul: <b>{{ semana['ruim'] }} vezes</b></p>
            </div>

            <div class="card">
                <h2>Relatório de Ontem</h2>
                <p>⚠ Somente Luz Azul: <b>{{ ontem['ruim'] }} vezes</b></p>
            </div>
        </div>

        <div class="grafico">
            <h2>Gráfico de Luminosidade (Hoje)</h2>
            <canvas id="graficoHoje"></canvas>
        </div>

    </div>

<script>
    function mostrarConteudo() {
        document.getElementById("inicio").style.display = "none";
        document.body.style.display = "block"; // desbloqueia layout normal
        document.getElementById("conteudo").style.display = "block";
        gerarGrafico();
    }

    function gerarGrafico() {
        const ctx = document.getElementById('graficoHoje').getContext('2d');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: {{ horas | safe }},
                datasets: [
                    {
                        label: 'Luminosidade',
                        data: {{ valores | safe }},
                        borderColor: '#c77dff',
                        borderWidth: 3,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: 'white' }},
                    annotation: {
                        annotations: {
                            faixaCritica: {
                                type: 'box',
                                yMin: 200,
                                yMax: 500,
                                backgroundColor: "rgba(255,0,0,0.25)",
                                borderWidth: 0
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 600,
                        ticks: { color: "white" }
                    },
                    x: {
                        ticks: { color: "white" }
                    }
                }
            }
        });
    }
</script>

<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@1.4.0"></script>

</body>
</html>
"""

# ---------------------
# ROTA
# ---------------------

@app.route("/")
def index():
    semana = simular_relatorio_semana()
    ontem = simular_relatorio_ontem()
    horas, valores = simular_grafico_hoje()

    return render_template_string(
        HTML,
        semana=semana,
        ontem=ontem,
        horas=horas,
        valores=valores
    )

if __name__ == "__main__":
    app.run(debug=True)
