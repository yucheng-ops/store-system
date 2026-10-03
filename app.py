import os
import socket
import sqlite3
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import qrcode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'store_secret_2026'
socketio = SocketIO(app, cors_allowed_origins="*")

DB_PATH = 'repairs.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            name TEXT,
            phone TEXT,
            item_type TEXT,
            issue TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def mask_name(name):
    if not name: return ""
    return name[0] + "*" if len(name) <= 2 else name[0] + "*" + name[-1]

def mask_phone(phone):
    if not phone: return ""
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) == 10 and digits.startswith('09'):
        return f"{digits[:4]}-***-{digits[7:]}"
    return phone

@app.route('/')
def customer_form():
    return render_template('index.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@socketio.on('submit_repair')
def handle_repair_submission(data):
    order_id = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}"
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
        (order_id, created_at, data.get('name',''), data.get('phone',''), data.get('itemType',''), data.get('issue',''))
    )
    conn.commit()
    conn.close()

    emit('new_order', {
        'id': order_id,
        'time': created_at.split()[1],
        'raw_name': data.get('name',''),
        'masked_name': mask_name(data.get('name','')),
        'raw_phone': data.get('phone',''),
        'masked_phone': mask_phone(data.get('phone','')),
        'item_type': data.get('itemType',''),
        'issue': data.get('issue','')
    }, broadcast=True)

if __name__ == '__main__':
    local_ip = get_local_ip()
    customer_url = f"http://{local_ip}:5000"
    
    print("\n" + "="*50)
    print("  門市客戶接洽系統 - 已啟動")
    print("="*50)
    print(f"顧客填單網址 (請掃下方 QR Code): {customer_url}")
    print(f"門市後台網址: http://localhost:5000/admin")
    print("="*50 + "\n")
    
    qr = qrcode.QRCode()
    qr.add_data(customer_url)
    qr.print_ascii(invert=True)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)