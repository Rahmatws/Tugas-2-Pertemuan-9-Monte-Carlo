# app.py
from flask import Flask, jsonify, request, render_template
import random
import mysql.connector

app = Flask(__name__)

# Konfigurasi koneksi ke database MySQL
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',        # Ganti dengan host Anda
        user='root',             # Ganti dengan user Anda
        password='',             # Ganti dengan password Anda
        database='universitas'    # Nama database
    )
    return connection

# Fungsi untuk menghitung probabilitas dan interval kumulatif
def hitung_interval(data):
    total_semua = sum(row['total'] for row in data)
    probabilitas = []
    kumulatif = 0
    interval = []

    for row in data:
        prob = row['total'] / total_semua
        kumulatif += prob
        probabilitas.append({
            "tahun": row['tahun'],
            "jumlah": row['total'],
            "probabilitas": round(prob, 4),
            "kumulatif": round(kumulatif, 4),
            "interval": (round(kumulatif - prob, 4), round(kumulatif, 4))
        })

    return probabilitas

# Fungsi untuk LCG
# Parameters: modulus `m`, multiplier `a`, increment `c`, seed `zi`
def lcg(a, c, m, zi, n):
    rng_results = []
    for _ in range(n):
        zi = (a * zi + c) % m
        rng_results.append(zi)
    return rng_results

# Route untuk halaman utama
@app.route('/')
def home():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Mengambil data mahasiswa per jurusan dan tahun
    cursor.execute('SELECT jurusan, tahun, total FROM mahasiswa WHERE tahun BETWEEN 2022 AND 2024')
    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('coba1.html', mahasiswa_data=data)

# Route untuk mendapatkan data prediksi berdasarkan jurusan
@app.route('/prediksi', methods=['POST'])
def prediksi():
    jurusan = request.json.get('jurusan')

    if not jurusan:
        return jsonify({"error": "Jurusan tidak dipilih"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Mengambil data mahasiswa per tahun berdasarkan jurusan
    query = 'SELECT tahun, total FROM mahasiswa WHERE jurusan = %s AND tahun BETWEEN 2022 AND 2024'
    cursor.execute(query, (jurusan,))
    data = cursor.fetchall()

    cursor.close()
    connection.close()

    if not data:
        return jsonify({"error": "Tidak ada data untuk jurusan tersebut"}), 404

    # Hitung probabilitas dan interval
    interval_data = hitung_interval(data)

    # Generate bilangan acak menggunakan LCG
    a, c, m, zi, n = 1103515245, 12345, 2**31, 7, 10  # Parameter LCG
    rng_values = lcg(a, c, m, zi, n)
    angka_tiga_digit = [str(rng).zfill(3)[-3:] for rng in rng_values]

    # Prediksi berdasarkan interval
    prediksi = []
    for angka in angka_tiga_digit:
        nilai = int(angka) / 1000
        for row in interval_data:
            if row['interval'][0] <= nilai < row['interval'][1]:
                prediksi.append({"tahun": 2025, "jumlah": row['jumlah'], "fakultas": jurusan})
                break

    return jsonify({
        "interval_data": interval_data,
        "rng_values": rng_values,
        "angka_tiga_digit": angka_tiga_digit,
        "prediksi": prediksi
    })

# Route untuk prediksi semua fakultas
@app.route('/prediksi_semua', methods=['GET'])
def prediksi_semua():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Mengambil data mahasiswa per jurusan dan tahun
    query = 'SELECT jurusan, tahun, total FROM mahasiswa WHERE tahun BETWEEN 2022 AND 2024'
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    connection.close()

    if not data:
        return jsonify({"error": "Tidak ada data untuk fakultas"}), 404

    # Memisahkan data berdasarkan jurusan
    jurusan_data = {}
    for row in data:
        jurusan = row['jurusan']
        if jurusan not in jurusan_data:
            jurusan_data[jurusan] = []
        jurusan_data[jurusan].append(row)

    # Prediksi untuk setiap jurusan
    all_predictions = []
    a, c, m, zi, n = 1103515245, 12345, 2**31, 7, 1  # Parameter LCG dengan `n=1`
    for jurusan, rows in jurusan_data.items():
        interval_data = hitung_interval(rows)
        rng_values = lcg(a, c, m, zi, n)
        angka_tiga_digit = [str(rng).zfill(3)[-3:] for rng in rng_values]

        for angka in angka_tiga_digit:
            nilai = int(angka) / 1000
            for row in interval_data:
                if row['interval'][0] <= nilai < row['interval'][1]:
                    all_predictions.append({
                        "fakultas": jurusan,
                        "tahun": 2025,
                        "jumlah": row['jumlah']
                    })
                    break

    return jsonify({"prediksi_semua": all_predictions})

if __name__ == '__main__':
    app.run(debug=True)
