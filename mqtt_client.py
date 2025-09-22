import json
import paho.mqtt.client as mqtt

BROKER = "192.168.57.2"  # Sesuaikan dengan broker Mosquitto kamu
PORT = 1883
TOPIC_REQUEST = "tanaman/get"
TOPIC_RESPONSE = "tanaman/response"

def on_connect(client, userdata, flags, rc):
    print("✅ Connected with result code", rc)
    client.subscribe(TOPIC_RESPONSE)
    # Kirim request setelah connect
    client.publish(TOPIC_REQUEST, "ambil_data")
    print("📤 Request dikirim ke", TOPIC_REQUEST)

def on_message(client, userdata, msg):
    print(f"📩 Response diterima di {msg.topic}")
    data = json.loads(msg.payload.decode())
    for t in data:
        print(f"- {t['nama']} ({t['latin']}), Zona: {t['jenis_zona']}")
    # print(data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()