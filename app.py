from flask import Flask, request, redirect, session, jsonify
import sqlite3
import os
import requests
import base64
import re
import hashlib
import hmac
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key-change-in-prod')

# Razorpay Config
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_xxxxx')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'xxxxx')
RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', 'webhook_secret')
BASE_URL = os.environ.get('BASE_URL', 'https://c-hub-mh4n.onrender.com')

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS containers
                 (id INTEGER PRIMARY KEY, title TEXT, photo TEXT, city TEXT,
                  type TEXT, price INTEGER, deposit INTEGER, phone TEXT,
                  status TEXT DEFAULT 'Available', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY, container_id INTEGER, name TEXT,
                  phone TEXT, start_date TEXT, end_date TEXT, payment_id TEXT,
                  payment_status TEXT DEFAULT 'Pending', payment_link_id TEXT,
                  amount INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def validate_phone(phone):
    return bool(re.match(r'^[6-9]\d{9}$', phone))

def validate_url(url):
    return bool(re.match(r'^https?://.*\.(jpg|jpeg|png|webp)$', url, re.I))

def create_payment_link(amount, container_id, container_title, customer_name, customer_phone):
    url = "https://api.razorpay.com/v1/payment_links"
    auth = base64.b64encode(f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}".encode()).decode()

    data = {
        "amount": amount * 100,
        "currency": "INR",
        "description": f"10% Advance for {container_title}",
        "customer": {"name": customer_name, "contact": customer_phone},
        "notify": {"sms": True},
        "reminder_enable": True,
        "callback_url": f"{BASE_URL}/payment-success?container_id={container_id}",
        "callback_method": "get",
        "expire_by": int((datetime.now() + timedelta(hours=24)).timestamp())
    }

    try:
        r = requests.post(url, json=data, headers={"Authorization": f"Basic {auth}"}, timeout=10)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def verify_webhook_signature(body, signature):
    expected = hmac.new(RAZORPAY_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

STYLE = '''<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',system-ui;background:#f2f4f5;padding-bottom:90px}
.header{background:#002f34;color:white;padding:16px 20px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.1)}
.header h1{font-size:20px;font-weight:700}
.header p{font-size:12px;opacity:0.8;margin-top:2px}
.header-btn{position:absolute;top:16px;right:20px;background:#23e5db;color:#002f34;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:700;text-decoration:none}
.container{padding:12px;max-width:600px;margin:auto}
.card{background:white;border-radius:12px;padding:0;margin:16px 0;box-shadow:0 2px 8px rgba(0,0,0,0.08);overflow:hidden;position:relative}
.card-img{width:100%;height:220px;object-fit:cover;background:#eee;transition:0.3s}
.card.sold.card-img{filter:brightness(0.5)}
.sold-badge{position:absolute;top:12px;left:12px;color:white;padding:6px 14px;border-radius:6px;font-weight:700;font-size:13px;z-index:10;box-shadow:0 2px 8px rgba(0,0,0,0.3)}
.card-body{padding:14px}
.tag{display:inline-block;background:#e8f8f5;color:#002f34;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-right:6px}
.card h3{margin:10px 0 6px;font-size:17px;color:#002f34;line-height:1.3}
.price{color:#002f34;font-size:24px;font-weight:700}
.price-sub{font-size:14px;color:#666;font-weight:400}
.meta{font-size:13px;color:#666;margin:8px 0;display:flex;gap:12px;flex-wrap:wrap}
.btn{background:#002f34;color:white;border:none;padding:14px;border-radius:8px;font-size:15px;font-weight:600;width:100%;cursor:pointer;transition:0.2s;text-decoration:none;display:block;text-align:center}
.btn:active{transform:scale(0.98)}
.btn-green{background:#23e5db;color:#002f34}
.btn-grey{background:#e4e4e4;color:#999;cursor:not-allowed}
.btn-red{background:#ff3b30;color:white}
.btn-whatsapp{background:#25D366;color:white}
input,select{width:100%;padding:13px;border:2px solid #e4e4e4;border-radius:8px;font-size:15px;margin:8px 0;transition:0.2s}
input:focus,select:focus{outline:none;border-color:#23e5db}
input.error{border-color:#ff3b30}
label{font-weight:600;font-size:13px;color:#002f34;display:block;margin-top:12px}
.error-text{color:#ff3b30;font-size:12px;margin-top:4px}
.fab{position:fixed;bottom:20px;right:20px;background:#23e5db;color:#002f34;width:56px;height:56px;border-radius:50%;border:none;font-size:28px;box-shadow:0 6px 16px rgba(35,229,219,0.4);cursor:pointer;z-index:99}
.empty{text-align:center;padding:60px 20px;color:#999}
.empty h3{color:#666;margin-bottom:8px}
.form-card{background:white;border-radius:12px;padding:20px;margin:16px 0}
.commission-box{background:#fff3cd;padding:14px;border-radius:8px;margin:16px 0;border:1px solid #ffc107}
.owner-panel{background:#e8f8f5;border:2px solid #23e5db}
.verify-box{background:#e8f8f5;padding:14px;border-radius:8px;margin:16px 0;border:2px solid #23e5db}
.search-box{background:white;padding:12px;border-radius:12px;margin:16px 0;display:flex;gap:8px}
.search-box select,.search-box input{margin:0}
.table{width:100%;border-collapse:collapse;font-size:13px}
.table th,.table td{padding:10px;text-align:left;border-bottom:1px solid #e4e4e4}
.table th{background:#f2f4f5;font-weight:600}
</style>'''

@app.route('/')
def home():
    owner_phone = session.get('owner_phone', None)
    search_city = request.args.get('city', '')
    search_type = request.args.get('type', '')

    conn = sqlite3.connect('database.db')
    query = "SELECT * FROM containers WHERE 1=1"
    params = []
    if search_city:
        query += " AND city LIKE?"
        params.append(f'%{search_city}%')
    if search_type:
        query += " AND type=?"
        params.append(search_type)
    query += " ORDER BY id DESC"

    containers = conn.cursor().execute(query, params).fetchall()
    conn.close()

    header_btn = f'<a href="/logout" class="header-btn">🚪 Logout</a>' if owner_phone else f'<a href="/verify" class="header-btn">👑 Owner Login</a>'

    html = f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Container Bazaar</h1><p>Navi Mumbai • Buy • Rent</p>{header_btn}</div>
    <div class="container">'''

    if owner_phone:
        html += f'<div class="verify-box" style="text-align:center"><b>👑 Owner Mode Active</b><br><span style="font-size:13px">Phone: {owner_phone}</span><br><a href="/admin" style="font-size:12px;color:#002f34">View Bookings</a></div>'

    html += f'''<div class="search-box">
    <form method="GET" style="display:flex;gap:8px;width:100%">
    <input name="city" placeholder="Search City" value="{search_city}" style="flex:1">
    <select name="type" style="flex:1"><option value="">All Types</option>
    <option value="Rent" {'selected' if search_type=='Rent' else ''}>Rent</option>
    <option value="Sell" {'selected' if search_type=='Sell' else ''}>Sell</option></select>
    <button class="btn" style="width:auto;padding:13px 20px">🔍</button>
    </form></div>'''

    if not containers:
        html += '<div class="empty"><h3>Koi container nahi mila</h3><p>Neeche + dabake pehla list karo</p></div>'

    for id, title, photo, city, type, price, deposit, phone, status, created in containers:
        sold_class = 'sold' if status in ['Sold','Booked'] else ''
        is_my_container = owner_phone and phone == owner_phone

        if status == 'Sold':
            badge = '<div class="sold-badge" style="background:#ff3b30">SOLD</div>'
            btn = '<button class="btn btn-grey" disabled>Sold Out</button>'
        elif status == 'Booked':
            badge = '<div class="sold-badge" style="background:#ff9500">BOOKED</div>'
            btn = '<button class="btn btn-grey" disabled>Booked</button>'
        else:
            badge = ''
            if is_my_container:
                btn = f'<a href="/manage/{id}" class="btn btn-green">👑 MANAGE MY CONTAINER</a>'
            else:
                btn = f'<a href="/book/{id}" class="btn">Contact Seller</a>'

        html += f'''<div class="card {sold_class}">
        {badge}
        <img class="card-img" src="{photo}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container+Image'">
        <div class="card-body">
        <div><span class="tag">{type}</span><span class="tag">{city}</span></div>
        <h3>{title}</h3>
        <div class="price">₹{price:,}<span class="price-sub"> {'/day' if type=='Rent' else ''}</span></div>
        <div class="meta"><span>💰 Deposit: ₹{deposit:,}</span><span>📞 {phone[:5]}*****</span></div>
        {btn}
        </div></div>'''
    return html + '</div><a href="/add"><button class="fab">+</button></a></body></html>'

@app.route('/verify', methods=['GET','POST'])
def verify():
    error = ''
    if request.method == 'POST':
        phone = request.form.get('phone', '').strip()
        if not validate_phone(phone):
            error = 'Valid 10-digit phone number daalo'
        else:
            session['owner_phone'] = phone
            return redirect('/')
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Owner Login</h1></div>
    <div class="container"><div class="form-card">
    <h3 style="margin-bottom:10px">👑 Owner Verification</h3>
    <p style="color:#666;font-size:14px;margin-bottom:15px">Apna phone number daalo jo container list karte waqt diya tha</p>
    <form method="POST">
    <label>Your Phone Number</label>
    <input name="phone" type="tel" placeholder="9876543210" required class="{'error' if error else ''}" value="{request.form.get('phone','')}">
    {f'<div class="error-text">{error}</div>' if error else ''}
    <br><br><button class="btn btn-green">Verify & Continue</button></form></div>
    <a href="/" class="btn btn-grey">Back</a></div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('owner_phone', None)
    return redirect('/')

@app.route('/add', methods=['GET','POST'])
def add():
    errors = {}
    if request.method == 'POST':
        title = request.form.get('title','').strip()
        photo = request.form.get('photo','').strip()
        city = request.form.get('city','').strip()
        type_val = request.form.get('type','')
        price = request.form.get('price','')
        deposit = request.form.get('deposit','')
        phone = request.form.get('phone','').strip()

        if not title or len(title) < 5: errors['title'] = 'Minimum 5 characters'
        if not validate_url(photo): errors['photo'] = 'Valid image URL daalo (.jpg/.png)'
        if not city: errors['city'] = 'City required'
        if not type_val: errors['type'] = 'Type select karo'
        try:
            price = int(price)
            if price <= 0 or price > 10000000: errors['price'] = 'Price ₹1-1Cr ke beech'
        except: errors['price'] = 'Valid number daalo'
        try:
            deposit = int(deposit)
            if deposit < 0: errors['deposit'] = 'Deposit 0 ya zyada'
        except: errors['deposit'] = 'Valid number daalo'
        if not validate_phone(phone): errors['phone'] = 'Valid 10-digit phone'

        if not errors:
            conn = sqlite3.connect('database.db')
            conn.cursor().execute("INSERT INTO containers (title,photo,city,type,price,deposit,phone) VALUES (?,?,?,?,?,?,?)",
                                  (title, photo, city, type_val, price, deposit, phone))
            conn.commit()
            conn.close()
            session['owner_phone'] = phone
            return redirect('/')

    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>List Your Container</h1><p>Free mein add karo</p></div>
    <div class="container"><div class="form-card"><form method="POST">
    <label>Container Title</label>
    <input name="title" placeholder="20ft Dry Container" required value="{request.form.get('title','')}" class="{'error' if 'title' in errors else ''}">
    {f'<div class="error-text">{errors.get("title","")}</div>' if 'title' in errors else ''}

    <label>Photo URL</label>
    <input name="photo" type="url" placeholder="https://i.ibb.co/xyz123/container.jpg" required value="{request.form.get('photo','')}" class="{'error' if 'photo' in errors else ''}">
    {f'<div class="error-text">{errors.get("photo","")}</div>' if 'photo' in errors else ''}

    <label>City</label>
    <input name="city" value="{request.form.get('city','Navi Mumbai')}" required class="{'error' if 'city' in errors else ''}">
    {f'<div class="error-text">{errors.get("city","")}</div>' if 'city' in errors else ''}

    <label>Listing Type</label>
    <select name="type" required class="{'error' if 'type' in errors else ''}">
    <option value="">Select</option>
    <option value="Rent" {'selected' if request.form.get('type')=='Rent' else ''}>Rent pe dena hai</option>
    <option value="Sell" {'selected' if request.form.get('type')=='Sell' else ''}>Bechna hai</option>
    </select>
    {f'<div class="error-text">{errors.get("type","")}</div>' if 'type' in errors else ''}

    <label>Price ₹</label>
    <input name="price" type="number" placeholder="1500" required value="{request.form.get('price','')}" class="{'error' if 'price' in errors else ''}">
    {f'<div class="error-text">{errors.get("price","")}</div>' if 'price' in errors else ''}

    <label>Security Deposit ₹</label>
    <input name="deposit" type="number" placeholder="10000" required value="{request.form.get('deposit','')}" class="{'error' if 'deposit' in errors else ''}">
    {f'<div class="error-text">{errors.get("deposit","")}</div>' if 'deposit' in errors else ''}

    <label>Your Phone</label>
    <input name="phone" type="tel" placeholder="9876543210" required value="{request.form.get('phone','')}" class="{'error' if 'phone' in errors else ''}">
    {f'<div class="error-text">{errors.get("phone","")}</div>' if 'phone' in errors else ''}

    <br><br><button class="btn btn-green">Post Now</button></form></div>
    <a href="/" class="btn btn-grey">Cancel</a></div></body></html>'''

@app.route('/manage/<int:id>')
def manage(id):
    owner_phone = session.get('owner_phone', None)
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    conn.close()
    if not cont or not owner_phone or cont[7]!= owner_phone: return redirect('/')

    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Manage Container</h1></div><div class="container">
    <div class="card"><img class="card-img" src="{cont[2]}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container'">
    <div class="card-body"><h3>{cont[1]}</h3>
    <div class="price">₹{cont[5]:,}<span class="price-sub"> {'/day' if cont[4]=='Rent' else ''}</span></div>
    <div class="meta"><span>📍 {cont[3]}</span><span>💰 Deposit: ₹{cont[6]:,}</span></div></div></div>
    <div class="form-card owner-panel">
    <h3 style="color:#002f34;margin-bottom:10px">👑 Owner Panel</h3>
    <p style="color:#666;font-size:14px;margin-bottom:15px">Current Status: <b>{cont[8]}</b></p>
    <a href="/available/{id}" class="btn btn-green">Mark Available Again</a><br><br>
    <a href="/" class="btn btn-grey">Back to Home</a>
    </div></div></body></html>'''

@app.route('/book/<int:id>', methods=['GET','POST'])
def book(id):
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    if not cont:
        conn.close()
        return redirect('/')

    commission = int(cont[5] * 0.1)
    final_amount = int(commission * 1.02) # 2% gateway charge customer se

    if cont[8]!= 'Available':
        conn.close()
        return f'''<html><head>{STYLE}</head><body><div class="header"><h1>Not Available</h1></div>
        <div class="container"><div class="form-card" style="text-align:center">
        <div style="font-size:48px">❌</div><h3 style="margin:15px 0">Ye container ab available nahi hai</h3>
        <p style="color:#666">Ye pehle hi {cont[8]} ho chuka hai</p>
        <a href="/" class="btn">Back to Home</a></div></div></body></html>'''

    errors = {}
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        phone = request.form.get('phone','').strip()
        start = request.form.get('start','')
        end = request.form.get('end','')

        if not name or len(name) < 3: errors['name'] = 'Minimum 3 characters'
        if not validate_phone(phone): errors['phone'] = 'Valid 10-digit phone'
        if not start: errors['start'] = 'Start date required'
        if not end: errors['end'] = 'End date required'
        if start and end and start > end: errors['end'] = 'End date start se baad honi chahiye'

        if not errors:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO bookings (container_id,name,phone,start_date,end_date,amount) VALUES (?,?,?,?,?,?)",
                           (id, name, phone, start, end, final_amount))
            booking_id = cursor.lastrowid

            new_status = 'Sold' if cont[4]=='Sell' else 'Booked'
            conn.cursor().execute("UPDATE containers SET status=? WHERE id=?", (new_status, id))
            conn.commit()

            payment_data = create_payment_link(final_amount, id, cont[1], name, phone)
            if payment_data:
                conn.cursor().execute("UPDATE bookings SET payment_link_id=? WHERE id=?", (payment_data['id'], booking_id))
                conn.commit()
                conn.close()
                return redirect(payment_data['short_url'])
            else:
                conn.close()
                return f'''<html><head>{STYLE}</head><body><div class="header"><h1>Error</h1></div>
                <div class="container"><div class="form-card" style="text-align:center">
                <h3>Payment link create nahi hua</h3><p>Please try again</p>
                <a href="/" class="btn">Back to Home</a></div></div></body></html>'''

    conn.close()
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Book Container</h1></div><div class="container">
    <div class="card"><img class="card-img" src="{cont[2]}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container'">
    <div class="card-body"><h3>{cont[1]}</h3>
    <div class="price">₹{cont[5]:,}<span class="price-sub"> {'/day' if cont[4]=='Rent' else ''}</span></div>
    <div class="meta"><span>📍 {cont[3]}</span><span>💰 Deposit: ₹{cont[6]:,}</span></div>
    <a href="https://wa.me/91{cont[7]}" class="btn btn-whatsapp" style="margin-top:10px">💬 WhatsApp Owner</a>
    </div></div>
    <div class="commission-box">
    <b>⚡ Booking Advance: ₹{final_amount:,}</b><br>
    <span style="font-size:13px;color:#666">₹{commission:,} + ₹{final_amount-commission:,} (2% gateway fee)</span>
    </div>
    <div class="form-card"><form method="POST">
    <label>Your Name</label>
    <input name="name" required value="{request.form.get('name','')}" class="{'error' if 'name' in errors else ''}">
    {f'<div class="error-text">{errors.get("name","")}</div>' if 'name' in errors else ''}

    <label>Phone Number</lab
