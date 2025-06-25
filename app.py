from flask import Flask, render_template, request, redirect, url_for, session
import csv, os

app = Flask(__name__)
app.secret_key = 'stnk123'
CSV_FILE = 'data.csv'

USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'user': {'password': 'user123', 'role': 'user'}
}

def load_data():
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_data(data):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = USERS.get(uname)
        if user and user['password'] == pwd:
            session['user'] = uname
            session['role'] = user['role']
            return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Login gagal. Cek kembali username/password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/user', methods=['GET', 'POST'])
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    data = load_data()
    fields = list(data[0].keys()) if data else [
        "NO.", "NOKA", "NAMA STNK/BPKB", "TGL SOLD", "No. DO / No. Faktur DMS HAKA",
        "No. SPK", "IDENTIFICATION NO.", "STATUS SOLD", "DEC DATE", "BSTB", "KELUAR",
        "KEMBALI", "SALES", "SUPERVISOR", "MODEL", "UNIT TYPE",
        "ACTUAL JARAK HARI ANTARA SOLD DAN SALES INPUT", "STATUS INPUT",
        "TANGGAL SELESAI INPUT", "ACTUAL DATE (10 HARI KERJA)",
        "TANGGAL ALOKASI UNIT DI CRM", "STATUS ALOKASI UNIT",
        "TANGGAL PENGAJUAN FAKTUR KENDARAAN KE ATPM", "ACTUAL DATE (14 HARI KERJA)",
        "TANGGAL TERIMA FAKTUR KENDARAAN DARI ATPM", "STATUS PENGAJUAN FAKTUR",
        "REMARKS", "EMAIL COSTUMER", "TANGGAL PENGAJUAN STNK KE BIRO JASA",
        "ACTUAL DATE (15 HARI KERJA)", "TANGGAL TERIMA STNK DARI BIRO JASA",
        "STATUS PENERIMAAN STNK", "TANGGAL SERAH TERIMA STNK KE CUST"
    ]

    if request.method == 'POST':
        new_entry = {field: request.form.get(field, "") for field in fields}
        data.append(new_entry)
        save_data(data)

        if new_entry.get("STATUS INPUT", "").upper() == "NOT YET":
            session['reminder'] = "STNK belum lengkap. Segera input ulang."
            session['wa_target'] = f"https://wa.me/?text=STNK belum lengkap untuk {new_entry.get('NAMA STNK/BPKB')}"
        return redirect(url_for('user_dashboard'))

    return render_template('user_dashboard.html', data=data, fields=fields)

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    data = load_data()
    return render_template('admin_dashboard.html', data=data)

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_user(index):
    data = load_data()
    if index >= len(data):
        return "Data tidak ditemukan", 404

    if request.method == 'POST':
        for key in data[index]:
            data[index][key] = request.form.get(key, "")
        save_data(data)
        session['reminder'] = "✅ Data berhasil diperbarui."
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    template = 'edit_admin.html' if session.get('role') == 'admin' else 'edit_user.html'
    return render_template(template, data=data[index], index=index)

if __name__ == '__main__':
    app.run(debug=True)
