import json
import sqlite3
import logging
import threading
import time
import joblib
import numpy as np
import paho.mqtt.client as mqtt

# --- Konfigurasi ---
BROKER = "192.168.57.2"
PORT = 1883
TOPIC_SENSOR = "iot/bme280"    # Sensor subscribe
TOPIC_PREDICT = "iot/predict"  # Hasil prediksi
TOPIC_TANAMAN = "iot/tanaman"  # Publish tanaman tiap 30 detik

DB_PATH = "database.db"

model = joblib.load('knn_model_smart_farm.pkl')

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- MQTT Client ---
client = mqtt.Client()


# ---------------- Fungsi Database ----------------
def load_tanaman_from_db(db_path: str = DB_PATH):
    """Ambil semua data tanaman dari database"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tanaman")
            rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "nama": row[2],
                "jenis_zona": row[1],
                "keterangan": row[3],
                "latin": row[4],
                "suhu_optimal": row[5],
                "kelembaban_optimal": row[6],
            }
            for row in rows
        ]
    except sqlite3.Error as e:
        logging.error("DB Error: %s", e)
        return []


# ---------------- Fungsi Prediksi ----------------
def predict_zone(suhu: float, tekanan: float, ketinggian: float):
    """Lakukan prediksi zona menggunakan model ML"""
    if model is None:
        logging.warning("Model belum di-load, prediksi dummy dikembalikan")
        return {"zone": "Unknown", "conf": 0.0}

    x_input = np.array([[suhu, tekanan, ketinggian]])
    pred = model.predict(x_input)
    proba = model.predict_proba(x_input)[0]
    confidence = float(max(proba))

    result_pred = pred[0] if isinstance(pred, (list, np.ndarray)) else pred
    return {"zone": str(result_pred), "conf": round(confidence * 100, 2)}


# ---------------- Fungsi MQTT ----------------
def publish_result(topic: str, data: dict):
    """Publish hasil ke MQTT"""
    try:
        payload = json.dumps(data)
        client.publish(topic, payload)
        logging.info("📤 Published to %s: %s", topic, payload)
    except Exception as e:
        logging.error("Gagal publish: %s", e)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("✅ Connected to MQTT Broker")
        client.subscribe(TOPIC_SENSOR)
        logging.info("📡 Subscribed to %s", TOPIC_SENSOR)
    else:
        logging.error("MQTT Connection failed: %s", rc)


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        logging.info("📥 Received from %s: %s", msg.topic, payload)

        data = json.loads(payload)
        suhu = data.get("temperature")
        tekanan = data.get("pressure")
        ketinggian = data.get("altitude")

        if None in (suhu, tekanan, ketinggian):
            logging.warning("Data sensor tidak lengkap, abaikan")
            return

        # Prediksi zona
        prediction = predict_zone(suhu, tekanan, ketinggian)

        # Publish hasil
        publish_result(TOPIC_PREDICT, prediction)

    except json.JSONDecodeError:
        logging.error("Payload bukan JSON valid")
    except Exception as e:
        logging.exception("Error saat proses pesan: %s", e)


# ---------------- Scheduler Tanaman ----------------
def schedule_tanaman(interval: int = 30):
    """Ambil data tanaman setiap interval detik dan publish ke MQTT"""
    while True:
        tanaman_list = load_tanaman_from_db()
        publish_result(TOPIC_TANAMAN, tanaman_list)
        time.sleep(interval)


# ---------------- Entry Point ----------------
def run():
    try:
        client.on_connect = on_connect
        client.on_message = on_message

        # Jalankan thread untuk publish tanaman periodik
        threading.Thread(target=schedule_tanaman, args=(30,), daemon=True).start()

        client.connect(BROKER, PORT, 60)
        logging.info("🔄 Connecting to broker %s:%s", BROKER, PORT)

        client.loop_forever()
    except Exception as e:
        logging.exception("MQTT Error: %s", e)


if __name__ == "__main__":
    run()