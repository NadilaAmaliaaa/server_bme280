from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import sqlite3
import joblib
import numpy as np


app = Flask(__name__)
app.secret_key = 'RAHASIA'
last_prediction = None

model = joblib.load('knn_model_smart_farm.pkl')
@app.before_request
def check_login():
    if 'username' not in session and request.endpoint not in ['login','get_tanaman','static','predict']:
        return redirect(url_for('login'))

@app.route('/')
def index():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tanaman")
        items = cursor.fetchall()
    return render_template('index_bme.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

        if user:
            stored_password = user[2]  # Mengambil kolom ke-2 (password) dalam hasil query
            if password == stored_password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash("Password salah!", "danger")
        else:
            flash("Username tidak ditemukan!", "danger")

    return render_template('login_bme.html')

@app.route("/logout")
def logout():
    session.clear()
    return render_template('login_bme.html')

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        nama = request.form['nama']
        jenis_zona = request.form['jenis_zona']
        keterangan = request.form.get('keterangan')
        latin = request.form['latin']
        suhu_optimal = request.form['suhu_optimal']
        kelembaban_optimal = request.form['kelembaban_optimal']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tanaman (jenis_zona, nama, keterangan, latin, suhu_optimal, kelembaban_optimal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (jenis_zona, nama, keterangan, latin, suhu_optimal, kelembaban_optimal))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_item_bme.html')


# Edit barang
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        nama = request.form['nama']
        jenis_zona = request.form['jenis_zona']
        latin = request.form['latin']
        suhu_optimal = request.form['suhu_optimal']
        kelembaban_optimal = request.form['kelembaban_optimal']
        keterangan = request.form.get('keterangan')

        cursor.execute('''
            UPDATE tanaman
            SET jenis_zona = ?, nama = ?, keterangan = ?, latin = ?, suhu_optimal = ?, kelembaban_optimal = ?
            WHERE id = ?
        ''', (jenis_zona, nama, keterangan, latin, suhu_optimal, kelembaban_optimal, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute('SELECT * FROM tanaman WHERE id = ?', (id,))
    item = cursor.fetchone()
    conn.close()
    return render_template('edit_item_bme.html', item=item)

# Hapus barang
@app.route('/delete_item/<int:id>')
def delete_item(id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tanaman WHERE id = ?", (id,))
        conn.commit()

    return redirect(url_for('index'))

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

@app.route('/api/predict', methods=['POST'])
def predict():
    global last_prediction
    try:
        print("📡 Received prediction request")
        print("📄 Request headers:", dict(request.headers))
        print("📦 Raw data:", request.get_data())
        
        # Coba ambil JSON dengan berbagai cara
        if request.is_json:
            data = request.get_json()
        else:
            # Fallback: coba parse manual
            import json
            raw_data = request.get_data(as_text=True)
            print("📝 Raw text data:", raw_data)
            data = json.loads(raw_data) if raw_data else {}
        
        print("📊 Parsed data:", data)
        
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        suhu = data.get('temperature')
        tekanan = data.get('pressure') 
        ketinggian = data.get('altitude')
        
        if None in [suhu, tekanan, ketinggian]:
            return jsonify({'error': 'Missing required fields: temperature, pressure, altitude'}), 400

        print(f"🌡 Suhu: {suhu}, 🌊 Tekanan: {tekanan}, 🏔 Ketinggian: {ketinggian}")

        # Prediksi
        x_input = np.array([[suhu, tekanan, ketinggian]])
        pred = model.predict(x_input)
        print("🔮 Prediction result:", pred)
        proba = model.predict_proba(x_input)[0]
        confidence = max(proba)

        # Handle berbagai format output model
        if isinstance(pred, (list, np.ndarray)):
            result_pred = pred[0] if len(pred) > 0 else "Unknown"
        else:
            result_pred = pred
            
        result = {'zone': str(result_pred), 'conf': round(int(confidence * 100),2)} 
        print("✅ Sending response:", result,)
        # if last_prediction != result_pred:
        #     last_prediction = result_pred
        #     # Kirim request ke bot Venom
        #     import requests
        #     try:
        #         requests.post("http://localhost:3000/send-message", json={
        #             "message": f"Prediksi berubah! Zona sekarang: {result_pred} ({result['conf']}% yakin)"
        #         })
        #         print("📩 Notifikasi WhatsApp dikirim")
        #     except Exception as e:
        #         print("⚠ Gagal kirim notifikasi:", e)
        return jsonify(result)
        
    except Exception as e:
        print("❌ Prediction error:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5050)
