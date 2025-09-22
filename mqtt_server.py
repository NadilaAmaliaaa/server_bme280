import sqlite3
import json
import paho.mqtt.client as mqtt

BROKER = "192.168.57.2"   # Ganti dengan IP broker jika bukan lokal
PORT = 1883
TOPIC_REQUEST = "tanaman/get"
TOPIC_RESPONSE = "tanaman/response"

def get_tanaman_from_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tanaman")
        items = cursor.fetchall()
    tanaman_list = [
        {
            'id': item[0],
            'nama': item[2],
            'jenis_zona': item[1],
            'keterangan': item[3],
            'latin': item[4],
            'suhu_optimal': item[5],
            'kelembaban_optimal': item[6],
        } for item in items
    ]
    return tanaman_list

def on_connect(client, userdata, flags, rc):
    print("✅ Connected with result code", rc)
    client.subscribe(TOPIC_REQUEST)

def on_message(client, userdata, msg):
    print(f"📩 Request diterima di {msg.topic}: {msg.payload.decode()}")
    if msg.topic == TOPIC_REQUEST:
        data = get_tanaman_from_db()
        client.publish(TOPIC_RESPONSE, json.dumps(data))
        print("📤 Response terkirim ke", TOPIC_RESPONSE)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
print("🚀 Server berjalan, menunggu request...")
client.loop_forever()