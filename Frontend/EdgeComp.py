from flask import Flask, render_template_string
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# ============================
# CONFIG MQTT
# ============================
MQTT_BROKER = "44.223.43.74"
MQTT_KEEPALIVE = 15
MQTT_PORT = 1883
MQTT_TOPIC = "/TEF/device069/attrs" 

# ============================
# ARMAZENAMENTO DOS DADOS
# ============================
luminosidade_hoje = []  
status_hoje = []        
luminosidade_ontem = []
luminosidade_semana = []

ultimo_dia = time.localtime().tm_mday

# ============================
# PROCESSAMENTO DE LUZ
# ============================
def classificar_luz(valor):
    return 200 <= valor <= 500

def atualizar_relatorios(valor, status):
    global ultimo_dia, luminosidade_hoje, status_hoje, luminosidade_ontem, luminosidade_semana

    dia_atual = time.localtime().tm_mday
    if dia_atual != ultimo_dia:
        luminosidade_ontem = luminosidade_hoje.copy()
        luminosidade_semana.append(len([v for v in luminosidade_ontem if classificar_luz(v)]))
        if len(luminosidade_semana) > 7:
            luminosidade_semana.pop(0)
        luminosidade_hoje = []
        status_hoje = []
        ultimo_dia = dia_atual

    luminosidade_hoje.append(valor)
    status_hoje.append(status)

def calcular_relatorio_semana():
    ruim_total = sum(luminosidade_semana)
    return {"ruim": ruim_total}

def calcular_relatorio_ontem():
    ruim = len([v for v in luminosidade_ontem if classificar_luz(v)])
    return {"ruim": ruim}

def dados_grafico_hoje():
    horas = [datetime.now().strftime("%H:%M") for _ in luminosidade_hoje]
    return horas, luminosidade_hoje, status_hoje

# ============================
# MQTT CALLBACKS
# ============================
def on_connect(client, userdata, flags, rc):
    print("MQTT conectado!")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        valor = int(payload['ldr'])
        status = payload.get('status', 'OK')  

        atualizar_relatorios(valor, status)
        socketio.emit("atualizar_luz", {"valor": valor, "status": status})

    except Exception as e:
        print("Erro ao ler mensagem MQTT:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
client.loop_start()

# ============================
# FLASK + FRONTEND
# ============================
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins="*")

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Proteção Contra Luz Azul</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
<style>
body { margin:0; font-family: Arial, sans-serif; background:#2d0b47; color:white; height:100vh; display:flex; justify-content:center; align-items:center; }
.center-container { text-align:center; }
button { padding:12px 28px; font-size:18px; background:#9b4de0; color:white; border:none; border-radius:8px; cursor:pointer; }
#conteudo { display:none; width:90%; max-width:1100px; margin:40px auto; }
.cards-container { display:flex; gap:20px; justify-content:center; margin-bottom:30px; }
.card { flex:1; background:#3c1361; padding:20px; border-radius:12px; min-width:250px; text-align:center; }
.grafico { background:#3c1361; padding:20px; border-radius:12px; margin-top:20px; }
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
let socket = io();
let graficoHoje;
let labels = {{ horas | safe }};
let valores = {{ valores | safe }};
let statusArray = {{ status | safe }};

function mostrarConteudo() {
    document.getElementById("inicio").style.display = "none";
    document.body.style.display = "block"; 
    document.getElementById("conteudo").style.display = "block";
    gerarGrafico();
}

function gerarGrafico() {
    const ctx = document.getElementById('graficoHoje').getContext('2d');
    graficoHoje = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Luminosidade',
                data: valores,
                borderColor: '#c77dff',
                borderWidth: 3,
                tension: 0.3,
                pointBackgroundColor: statusArray.map(s => s === 'ALERTA' ? 'red' : '#c77dff')
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: 'white' } } },
            scales: {
                y: { ticks: { color: "white" } },
                x: { ticks: { color: "white" } }
            }
        }
    });
}

// Atualização em tempo real
socket.on("atualizar_luz", function(data) {
    let valor = data.valor;
    let status = data.status;

    valores.push(valor);
    let now = new Date();
    labels.push(`${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`);
    statusArray.push(status);

    graficoHoje.data.labels = labels;
    graficoHoje.data.datasets[0].data = valores;
    graficoHoje.data.datasets[0].pointBackgroundColor = statusArray.map(s => s === 'ALERTA' ? 'red' : '#c77dff');
    graficoHoje.update();

    if(status === "ALERTA") {
        alert("⚠ ALERTA! Luminosidade intermediária detectada!");
    }
});
</script>

</body>
</html>
"""

@app.route("/")
def index():
    horas, valores, status = dados_grafico_hoje()
    semana = calcular_relatorio_semana()
    ontem = calcular_relatorio_ontem()
    return render_template_string(
        HTML,
        semana=semana,
        ontem=ontem,
        horas=horas,
        valores=valores,
        status=status
    )

if __name__ == "__main__":
    print("Servidor Flask rodando em http://localhost:5000 ...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
