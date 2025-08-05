import sqlite3

def seed_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    users = [
        ('admin', 'admin123'),
        ('nadila', '12345678'),
        ('user1', 'password1'),
        ('user2', 'password2')
    ]

    cursor.executemany('INSERT INTO users (username, password) VALUES (?, ?)', users)

    conn.commit()
    conn.close()
    print("Seeder untuk tabel `users` berhasil dijalankan.")


def seed_tanaman():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    tanaman_data = [
        ("Cool_Humid", "Selada", "Sayuran daun", "Lactuca sativa", "15-20°C", "70-80%"),
        ("Cool_Humid", "Kol", "Sayuran bulat", "Brassica oleracea", "16-22°C", "75-85%"),
        ("Cool_Humid", "Wortel", "Akar sehat dan manis", "Daucus carota", "15-21°C", "65-75%"),
        ("Cool_Humid", "Kentang", "Umbi serbaguna", "Solanum tuberosum", "14-18°C", "60-70%"),
        ("Cool_Humid", "Kubis", "Sayuran dataran tinggi", "Brassica oleracea var. capitata", "15-20°C", "70-80%"),
        ("Cool_Humid", "Strawberry", "Buah manis", "Fragaria × ananassa", "18-22°C", "60-70%"),
        ("Cool_Humid", "Bayam", "Daun bergizi", "Amaranthus spp.", "18-24°C", "65-75%"),

        ("Hot_Dry", "Jagung", "Sumber karbohidrat", "Zea mays", "24-30°C", "50-60%"),
        ("Hot_Dry", "Tomat", "Buah serbaguna", "Solanum lycopersicum", "20-27°C", "60-70%"),
        ("Hot_Dry", "Cabe", "Tanaman pedas", "Capsicum spp.", "22-30°C", "55-65%"),
        ("Hot_Dry", "Kacang Tanah", "Sumber protein", "Arachis hypogaea", "25-32°C", "50-60%"),
        ("Hot_Dry", "Tebu", "Sumber gula", "Saccharum officinarum", "25-35°C", "50-60%"),
        ("Hot_Dry", "Semangka", "Buah segar", "Citrullus lanatus", "25-30°C", "50-60%"),
        ("Hot_Dry", "Melon", "Buah musim panas", "Cucumis melo", "23-28°C", "50-60%"),

        ("Unstable", "Singkong", "Akar karbohidrat", "Manihot esculenta", "20-30°C", "50-80%"),
        ("Unstable", "Pisang", "Buah tropis", "Musa spp.", "25-30°C", "60-80%"),
        ("Unstable", "Pepaya", "Buah tropis cepat tumbuh", "Carica papaya", "24-32°C", "60-80%"),
        ("Unstable", "Sorgum", "Tanaman toleran kekeringan", "Sorghum bicolor", "27-32°C", "50-70%"),
        ("Unstable", "Kacang Hijau", "Legum tahan kondisi ekstrem", "Vigna radiata", "24-32°C", "50-75%"),
        ("Unstable", "Ubi Jalar", "Umbi serbaguna", "Ipomoea batatas", "21-29°C", "50-80%"),
        ("Unstable", "Bayam Merah", "Sayur adaptif", "Amaranthus tricolor", "22-30°C", "55-75%"),
    ]

    cursor.executemany('''
        INSERT INTO tanaman (jenis_zona, nama, keterangan, latin, suhu_optimal, kelembaban_optimal)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', tanaman_data)

    conn.commit()
    conn.close()
    print("Seeder untuk tabel `tanaman` berhasil dijalankan.")

# Jalankan keduanya
seed_users()
seed_tanaman()
