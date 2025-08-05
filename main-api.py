from flask import Flask, request, jsonify
import sqlite3
import joblib
import numpy as np

app = Flask(__name__)
model = joblib.load('knn_model_smart_farm.pkl')

# Get semua tanaman
@app.route('/api/tanaman', methods=['GET'])
def get_tanaman():
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
    return jsonify(tanaman_list)

# Tambah tanaman
@app.route('/api/tanaman', methods=['POST'])
def add_item():
    data = request.get_json()
    nama = data['nama']
    jenis_zona = data['jenis_zona']
    keterangan = data.get('keterangan')
    latin = data['latin']
    suhu_optimal = data['suhu_optimal']
    kelembaban_optimal = data['kelembaban_optimal']

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tanaman (jenis_zona, nama, keterangan, latin, suhu_optimal, kelembaban_optimal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (jenis_zona, nama, keterangan, latin, suhu_optimal, kelembaban_optimal))
        conn.commit()
    return jsonify({'message': 'Tanaman ditambahkan'})

# Edit tanaman
@app.route('/api/tanaman/<int:id>', methods=['PUT'])
def edit_item(id):
    data = request.get_json()
    nama = data['nama']
    jenis_zona = data['jenis_zona']
    latin = data['latin']
    suhu_optimal = data['suhu_optimal']
    kelembaban_optimal = data['kelembaban_optimal']
    keterangan = data.get('keterangan')

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tanaman
            SET jenis_zona = ?, nama = ?, keterangan = ?, latin = ?, suhu_optimal = ?, kelembaban_optimal = ?
            WHERE id = ?
        ''', (jenis_zona, nama, keterangan, latin, suhu_optimal, kelembaban_optimal, id))
        conn.commit()
    return jsonify({'message': 'Tanaman berhasil diupdate'})

# Hapus tanaman
@app.route('/api/tanaman/<int:id>', methods=['DELETE'])
def delete_item(id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tanaman WHERE id = ?", (id,))
        conn.commit()
    return jsonify({'message': 'Tanaman berhasil dihapus'})

# Prediksi zona
@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        suhu = data.get('temperature')
        tekanan = data.get('pressure') 
        ketinggian = data.get('altitude')
        
        if None in [suhu, tekanan, ketinggian]:
            return jsonify({'error': 'Missing required fields: temperature, pressure, altitude'}), 400

        x_input = np.array([[suhu, tekanan, ketinggian]])
        pred = model.predict(x_input)
        proba = model.predict_proba(x_input)[0]
        confidence = max(proba)

        result_pred = pred[0] if isinstance(pred, (list, np.ndarray)) else pred
        result = {'zone': str(result_pred), 'confidence': round(confidence * 100, 2)} 
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5050)