from flask import Flask, jsonify, render_template
import paho.mqtt.client as mqtt
import json
import threading

app = Flask(__name__)

# Configuration MQTT
BROKER = "localhost"
PORT = 1883
TOPIC = "darts"

data = {}

def on_connect(client, userdata, flags, rc):
    print("Connecté au broker MQTT avec le code de retour", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global data
    print("Message reçu :", msg.payload.decode())
    data = json.loads(msg.payload.decode())  # Mettre à jour les données

# Initialiser le client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Thread pour gérer MQTT séparément
def start_mqtt():
    mqtt_client.connect(BROKER, PORT, 60)
    mqtt_client.loop_forever()

threading.Thread(target=start_mqtt, daemon=True).start()

# Route pour récupérer les données
@app.route('/api/data')
def get_data():
    response = jsonify(data)
    response.charset = 'utf-8'  # Spécification de l'encodage UTF-8
    return response

# Route pour la page HTML
@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


