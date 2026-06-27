from flask import Flask, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'container-bazaar-secret-key-123' # Session ke liye zaroori

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS containers
                 (id INTEGER PRIMARY KEY, title TEXT, photo TEXT, city TEXT,
                  type TEXT, price INTEGER, deposit INTEGER, phone TEXT,
                  status TEXT DEFAULT 'Available')''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY, container_id INTEGER, name TEXT,
                  phone TEXT, start_date TEXT, end_date TEXT)''')
    conn.commit()
    conn.close()

init_db()

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
.meta{font-size:13px;color:#666;margin:8px 0;display:flex;gap:12px}
.btn{background:#002f34;color:white;border:none;padding:14px;border-radius:8px;font-size:15px;font-weight:600;width:100%;cursor:pointer;transition:0.2s}
.btn:active{transform:scale(0.98)}
.btn-green{background:#23e5db;color:#002f34}
.btn-grey{background:#e4e4e4;color:#999;cursor:not-allowed}
.btn-red{background:#ff3b30;color:white}
input,select{width:100%;padding:13px;border:2px solid #e4e4e4;border-radius:8px;font-size:15px;margin:8px 0;transition:0.2s}
input:focus,select:focus{outline:none;border-color:#23e5db}
label{font-weight:600;font-size:13px;color:#002f34;display:block;margin-top:12px}
.fab{position:fixed;bottom:20px;right:20px;background:#23e5db;color:#002f34;width:56px;height:56px;border-radius:50%;border:none;font-size:28px;box-shadow:0 6px 16px rgba(35,229,219,0.4);cursor:pointer;z-index:99}
.empty{text-align:center;padding:60px 20px;color:#999}
.empty h3{color:#666;margin-bottom:8px}
.form-card{background:white;border-radius:12px;padding:20px;margin:16px 0}
.commission-box{background:#fff3cd;padding:14px;border-radius:8px;margin:16px 0;border:1px solid #ffc107}
.owner-panel{background:#e8f8f5;border:2px solid #23e5db}
.verify-box{background:#e8f8f5;padding:14px;border-radius:8px;margin:16px 0;border:2px solid #23e5db}
</style>'''

@app.route('/')
def home():
    owner_phone = session.get('owner_phone', None)

    conn = sqlite3.connect('database.db')
    containers = conn.cursor().execute("SELECT * FROM containers ORDER BY id DESC").fetchall()
    conn.close()

    header_btn = f'<a href="/logout" class="header-btn">🚪 Logout</a>' if owner_phone else f'<a href="/verify" class="header-btn">👑 Owner Login</a>'

    html = f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Container Bazaar</h1><p>Navi Mumbai • Buy • Rent</p>{header_btn}</div>
    <div class="container">'''

    if owner_phone:
        html += f'<div class="verify-box" style="text-align:center"><b>👑 Owner Mode Active</b><br><span style="font-size:13px">Phone: {owner_phone}</span></div>'

    if not containers:
        html += '<div class="empty"><h3>Koi container nahi mila</h3><p>Neeche + dabake pehla list karo</p></div>'

    for id, title, photo, city, type, price, deposit, phone, status in containers:
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
            # YAHAN MAGIC HAI - Owner ko MANAGE, Customer ko CONTACT SELLER
            if is_my_container:
                btn = f'<a href="/manage/{id}"><button class="btn btn-green">👑 MANAGE MY CONTAINER</button></a>'
            else:
                btn = f'<a href="/book/{id}"><button class="btn">Contact Seller</button></a>'

        html += f'''<div class="card {sold_class}">
        {badge}
        <img class="card-img" src="{photo}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container+Image'">
        <div class="card-body">
        <div><span class="tag">{type}</span><span class="tag">{city}</span></div>
        <h3>{title}</h3>
        <div class="price">₹{price:,}<span class="price-sub"> {'/day' if type=='Rent' else ''}</span></div>
        <div class="meta"><span>💰 Deposit: ₹{deposit:,}</span></div>
        {btn}
        </div></div>'''
    return html + '</div><a href="/add"><button class="fab">+</button></a></body></html>'

@app.route('/verify', methods=['GET','POST'])
def verify():
    if request.method == 'POST':
        phone = request.form['phone']
        session['owner_phone'] = phone
        return redirect('/')
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Owner Login</h1></div>
    <div class="container"><div class="form-card">
    <h3 style="margin-bottom:10px">👑 Owner Verification</h3>
    <p style="color:#666;font-size:14px;margin-bottom:15px">Apna phone number daalo jo container list karte waqt diya tha</p>
    <form method="POST">
    <label>Your Phone Number</label><input name="phone" type="tel" placeholder="9876543210" required>
    <br><br><button class="btn btn-green">Verify & Continue</button></form></div>
    <a href="/"><button class="btn btn-grey">Back</button></a></div></body></html>'''

@app.route('/logout')
def logout():
    session.pop('owner_phone', None)
    return redirect('/')

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        data = (request.form['title'], request.form['photo'], request.form['city'],
                request.form['type'], int(request.form['price']), int(request.form['deposit']), request.form['phone'])
        conn = sqlite3.connect('database.db')
        conn.cursor().execute("INSERT INTO containers (title,photo,city,type,price,deposit,phone) VALUES (?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        # Auto login owner ko
        session['owner_phone'] = request.form['phone']
        return redirect('/')
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>List Your Container</h1><p>Free mein add karo</p></div>
    <div class="container"><div class="form-card"><form method="POST">
    <label>Container Title</label><input name="title" placeholder="20ft Dry Container" required>
    <label>Photo URL</label><input name="photo" type="url" placeholder="https://i.ibb.co/xyz123/container.jpg" required>
    <label>City</label><input name="city" value="Navi Mumbai" required>
    <label>Listing Type</label><select name="type"><option value="Rent">Rent pe dena hai</option><option value="Sell">Bechna hai</option></select>
    <label>Price ₹</label><input name="price" type="number" placeholder="1500" required>
    <label>Security Deposit ₹</label><input name="deposit" type="number" placeholder="10000" required>
    <label>Your Phone</label><input name="phone" type="tel" placeholder="9876543210" required>
    <br><br><button class="btn btn-green">Post Now</button></form></div>
    <a href="/"><button class="btn btn-grey">Cancel</button></a></div></body></html>'''

@app.route('/manage/<int:id>')
def manage(id):
    owner_phone = session.get('owner_phone', None)
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    conn.close()

    if not cont or not owner_phone or cont[7]!= owner_phone:
        return redirect('/')

    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Manage Container</h1></div><div class="container">
    <div class="card"><img class="card-img" src="{cont[2]}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container'">
    <div class="card-body"><h3>{cont[1]}</h3>
    <div class="price">₹{cont[5]:,}<span class="price-sub"> {'/day' if cont[4]=='Rent' else ''}</span></div>
    <div class="meta"><span>📍 {cont[3]}</span><span>💰 Deposit: ₹{cont[6]:,}</span></div></div></div>
    <div class="form-card owner-panel">
    <h3 style="color:#002f34;margin-bottom:10px">👑 Owner Panel</h3>
    <p style="color:#666;font-size:14px;margin-bottom:15px">Current Status: <b>{cont[8]}</b></p>
    <a href="/available/{id}"><button class="btn btn-green">Mark Available Again</button></a><br><br>
    <a href="/"><button class="btn btn-grey">Back to Home</button></a>
    </div></div></body></html>'''

@app.route('/book/<int:id>', methods=['GET','POST'])
def book(id):
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    if not cont:
        conn.close()
        return redirect('/')

    commission = int(cont[5] * 0.1)

    if cont[8]!= 'Available':
        conn.close()
        return f'''<html><head>{STYLE}</head><body><div class="header"><h1>Not Available</h1></div>
        <div class="container"><div class="form-card" style="text-align:center">
        <div style="font-size:48px">❌</div><h3 style="margin:15px 0">Ye container ab available nahi hai</h3>
        <p style="color:#666">Ye pehle hi {cont[8]} ho chuka hai</p>
        <a href="/"><button class="btn">Back to Home</button></a></div></div></body></html>'''

    if request.method == 'POST':
        conn.cursor().execute("INSERT INTO bookings (container_id,name,phone,start_date,end_date) VALUES (?,?,?,?,?)",
                              (id, request.form['name'], request.form['phone'], request.form['start'], request.form['end']))

        new_status = 'Sold' if cont[4]=='Sell' else 'Booked'
        conn.cursor().execute("UPDATE containers SET status=? WHERE id=?", (new_status, id))
        conn.commit()
        conn.close()

        return f'''<html><head>{STYLE}</head><body><div class="header"><h1>Success!</h1></div>
        <div class="container"><div class="form-card" style="text-align:center">
        <div style="font-size:48px">✅</div><h3 style="margin:15px 0">Booking Confirmed</h3>
        <p style="color:#666;margin-bottom:10px">Container ab <b>{new_status}</b> mark ho gaya hai</p>
        <p style="color:#666;margin-bottom:20px">Owner ko {cont[7]} pe call karo aur 10% advance ₹{commission:,} UPI kar do: <b>yourname@paytm</b></p>
        <a href="/"><button class="btn">Back to Home</button></a></div></div></body></html>'''

    conn.close()
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Book Container</h1></div><div class="container">
    <div class="card"><img class="card-img" src="{cont[2]}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container'">
    <div class="card-body"><h3>{cont[1]}</h3>
    <div class="price">₹{cont[5]:,}<span class="price-sub"> {'/day' if cont[4]=='Rent' else ''}</span></div>
    <div class="meta"><span>📍 {cont[3]}</span><span>💰 Deposit: ₹{cont[6]:,}</span></div>
    <div class="meta"><span>📞 {cont[7]}</span></div></div></div>
    <div class="commission-box">
    <b>⚡ Booking Advance: ₹{commission:,}</b><br>
    <span style="font-size:13px;color:#666">10% commission Container Bazaar ko UPI karein</span><br>
    <b>UPI ID:</b> yourname@paytm
    </div>
    <div class="form-card"><form method="POST">
    <label>Your Name</label><input name="name" required>
    <label>Phone Number</label><input name="phone" type="tel" required>
    <label>Start Date</label><input name="start" type="date" required>
    <label>End Date</label><input name="end" type="date" required>
    <br><br><button class="btn btn-green">Confirm Booking</button></form></div>
    <a href="/"><button class="btn btn-grey">Back</button></a></div></body></html>'''

@app.route('/available/<int:id>')
def mark_available(id):
    owner_phone = session.get('owner_phone', None)
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT phone FROM containers WHERE id=?", (id,)).fetchone()

    if not cont or not owner_phone or cont[0]!= owner_phone:
        conn.close()
        return redirect('/')

    conn.cursor().execute("UPDATE containers SET status='Available' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
