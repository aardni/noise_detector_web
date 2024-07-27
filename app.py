from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import sqlite3
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Tambahkan pengaturan CORS di sini
socketio = SocketIO(app, cors_allowed_origins="*")  # Atau ganti "*" dengan URL spesifik jika perlu

# Simpan notifikasi kebisingan dalam daftar
notifications = []

@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.execute('SELECT timestamp, noise_level FROM noise_database ORDER BY timestamp DESC')
    notifications = [{'timestamp': row[0], 'noise_level': row[1]} for row in cursor.fetchall()]

    # Hitung total notifikasi hari ini
    today = datetime.now().strftime('%Y-%m-%d')
    cursor = conn.execute('SELECT COUNT(*) FROM noise_database WHERE DATE(timestamp) = ?', (today,))
    total_notifications_today = cursor.fetchone()[0]

    # Hitung total notifikasi minggu ini
    start_of_week = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    cursor = conn.execute('SELECT COUNT(*) FROM noise_database WHERE DATE(timestamp) >= ?', (start_of_week,))
    total_notifications_week = cursor.fetchone()[0]
    conn.close()
    return render_template('index.html', notifications=notifications, total_notifications_today=total_notifications_today, total_notifications_week=total_notifications_week)


# Fungsi untuk menghubungkan ke database
def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/alert', methods=['GET'])
def alert():
    noise_level = request.args.get('noise_level')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notification = {'timestamp': timestamp, 'noise_level': noise_level}
    notifications.append(notification)

    # Emit notifikasi ke semua klien yang terhubung
    socketio.emit('new_notification', notification)

    conn = connect_db()
    conn.execute('INSERT INTO noise_database (timestamp, noise_level) VALUES (?, ?)', (timestamp, noise_level))
    conn.commit()
    conn.close()

    # Mengembalikan respons JSON
    return jsonify({
        'status': 'success',
        'message': 'Alert received',
        'notification': notification
    }), 200

@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0', port=5001)
