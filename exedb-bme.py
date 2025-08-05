import sqlite3

def create_tabel():
    # Koneksi ke database (jika tidak ada, akan dibuat otomatis)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Perintah untuk membuat tabel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tanaman (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jenis_zona TEXT NOT NULL CHECK(jenis_zona IN ('Cool_Humid', 'Hot_Dry', 'Unstable')),
            nama TEXT NOT NULL,
            keterangan TEXT,
            latin TEXT,
            suhu_optimal TEXT,
            kelembaban_optimal TEXT
        )
    ''')

    # Simpan perubahan dan tutup koneksi
    conn.commit()
    conn.close()

    print("Tabel berhasil dibuat!") 

def create_tabel_user():
    # Koneksi ke database (jika tidak ada, akan dibuat otomatis)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Perintah untuk membuat tabel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Simpan perubahan dan tutup koneksi
    conn.commit()
    conn.close()

    print("Tabel berhasil dibuat!")

create_tabel_user()
create_tabel()