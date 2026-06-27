from flask import Flask, request, redirect
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS containers
                 (id INTEGER PRIMARY KEY, title TEXT, photo TEXT, city TEXT,
                  type TEXT, price INTEGER, deposit INTEGER, phone TEXT)''')
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
.container{padding:12px;max-width:600px;margin:auto}
.card{background:white;border-radius:12px;padding:0;margin:16px 0;box-shadow:0 2px 8px rgba(0,0,0,0.08);overflow:hidden}
.card-img{width:100%;height:220px;object-fit:cover;background:#eee}
.card-body{padding:14px}
.tag{display:inline-block;background:#e8f8f5;color:#002f34;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-right:6px}
.card h3{margin:10px 0 6px;font-size:17px;color:#002f34;line-height:1.3}
.price{color:#002f34;font-size:24px;font-weight:700}
.price-sub{font-size:14px;color:#666;font-weight:400}
.meta{font-size:13px;color:#666;margin:8px 0;display:flex;gap:12px}
.btn{background:#002f34;color:white;border:none;padding:14px;border-radius:8px;font-size:15px;font-weight:600;width:100%;cursor:pointer;transition:0.2s}
.btn:active{transform:scale(0.98)}
.btn-green{background:#23e5db;color:#002f34}
.btn-grey{background:#e4e4e4;color:#002f34}
input,select{width:100%;padding:13px;border:2px solid #e4e4e4;border-radius:8px;font-size:15px;margin:8px 0;transition:0.2s}
input:focus,select:focus{outline:none;border-color:#23e5db}
label{font-weight:600;font-size:13px;color:#002f34;display:block;margin-top:12px}
.fab{position:fixed;bottom:20px;right:20px;background:#23e5db;color:#002f34;width:56px;height:56px;border-radius:50%;border:none;font-size:28px;box-shadow:0 6px 16px rgba(35,229,219,0.4);cursor:pointer;z-index:99}
.empty{text-align:center;padding:60px 20px;color:#999}
.empty h3{color:#666;margin-bottom:8px}
.form-card{background:white;border-radius:12px;padding:20px;margin:16px 0}
</style>'''

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    containers = conn.cursor().execute("SELECT * FROM containers ORDER BY id DESC").fetchall()
    conn.close()
    html = f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Container Bazaar</h1><p>Navi Mumbai • Buy • Rent</p></div>
    <div class="container">'''
    if not containers: html += '<div class="empty"><h3>Koi container nahi mila</h3><p>Neeche + dabake pehla list karo</p></div>'
    for id, title, photo, city, type, price, deposit, phone in containers:
        html += f'''<div class="card">
        <img class="card-img" src="{photo}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container+Image'">
        <div class="card-body">
        <div><span class="tag">{type}</span><span class="tag">{city}</span></div>
        <h3>{title}</h3>
        <div class="price">₹{price:,}<span class="price-sub"> {'/day' if type=='Rent' else ''}</span></div>
        <div class="meta"><span>💰 Deposit: ₹{deposit:,}</span></div>
        <a href="/book/{id}"><button class="btn">Contact Seller</button></a>
        </div></div>'''
    return html + '</div><a href="/add"><button class="fab">+</button></a></body></html>'

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        data = (request.form['title'], request.form['photo'], request.form['city'],
                request.form['type'], int(request.form['price']), int(request.form['deposit']), request.form['phone'])
        conn = sqlite3.connect('database.db')
        conn.cursor().execute("INSERT INTO containers (title,photo,city,type,price,deposit,phone) VALUES (?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        return redirect('/')
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>List Your Container</h1><p>Free mein add karo</p></div>
    <div class="container"><div class="form-card"><form method="POST">
    <label>Container Title</label><input name="title" placeholder="20ft Dry Container" required>
    <label>Photo URL</label><input name="photo" type="url" placeholder="https://image-link.jpg" required>
    <label>City</label><input name="city" value="Navi Mumbai" required>
    <label>Listing Type</label><select name="type"><option value="Rent">Rent pe dena hai</option><option value="Sell">Bechna hai</option></select>
    <label>Price ₹</label><input name="price" type="number" placeholder="1500" required>
    <label>Security Deposit ₹</label><input name="deposit" type="number" placeholder="10000" required>
    <label>Your Phone</label><input name="phone" type="tel" placeholder="9876543210" required>
    <br><br><button class="btn btn-green">Post Now</button></form></div>
    <a href="/"><button class="btn btn-grey">Cancel</button></a></div></body></html>'''

@app.route('/book/<int:id>', methods=['GET','POST'])
def book(id):
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        conn.cursor().execute("INSERT INTO bookings (container_id,name,phone,start_date,end_date) VALUES (?,?,?,?,?)",
                              (id, request.form['name'], request.form['phone'], request.form['start'], request.form['end']))
        conn.commit()
        conn.close()
        return f'''<html><head>{STYLE}</head><body><div class="header"><h1>Success!</h1></div>
        <div class="container"><div class="form-card" style="text-align:center">
        <div style="font-size:48px">✅</div><h3 style="margin:15px 0">Request Sent</h3>
        <p style="color:#666;margin-bottom:20px">Owner ko {cont[7]} pe call/message karo ya wo tumhe contact karega</p>
        <a href="/"><button class="btn">Back to Home</button></a></div></div></body></html>'''
    conn.close()
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Book Container</h1></div><div class="container">
    <div class="card"><img class="card-img" src="{cont[2]}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container'">
    <div class="card-body"><h3>{cont[1]}</h3>
    <div class="price">₹{cont[5]:,}<span class="price-sub"> {'/day' if cont[4]=='Rent' else ''}</span></div>
    <div class="meta"><span>📍 {cont[3]}</span><span>💰 Deposit: ₹{cont[6]:,}</span></div>
    <div class="meta"><span>📞 {cont[7]}</span></div></div></div>
    <div class="form-card"><form method="POST">
    <label>Your Name</label><input name="name" required>
    <label>Phone Number</label><input name="phone" type="tel" required>
    <label>Start Date</label><input name="start" type="date" required>
    <label>End Date</label><input name="end" type="date" required>
    <br><br><button class="btn btn-green">Send Booking Request</button></form></div>
    <a href="/"><button class="btn btn-grey">Back</button></a></div></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port).meta{font-size:13px;color:#666;margin:8px 0;display:flex;gap:12px}
.btn{background:#002f34;color:white;border:none;padding:14px;border-radius:8px;font-size:15px;font-weight:600;width:100%;cursor:pointer;transition:0.2s}
.btn:active{transform:scale(0.98)}
.btn-green{background:#23e5db;color:#002f34}
.btn-grey{background:#e4e4e4;color:#002f34}
input,select{width:100%;padding:13px;border:2px solid #e4e4e4;border-radius:8px;font-size:15px;margin:8px 0;transition:0.2s}
input:focus,select:focus{outline:none;border-color:#23e5db}
label{font-weight:600;font-size:13px;color:#002f34;display:block;margin-top:12px}
.fab{position:fixed;bottom:20px;right:20px;background:#23e5db;color:#002f34;width:56px;height:56px;border-radius:50%;border:none;font-size:28px;box-shadow:0 6px 16px rgba(35,229,219,0.4);cursor:pointer;z-index:99}
.empty{text-align:center;padding:60px 20px;color:#999}
.empty h3{color:#666;margin-bottom:8px}
.form-card{background:white;border-radius:12px;padding:20px;margin:16px 0}
</style>'''

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    containers = conn.cursor().execute("SELECT * FROM containers ORDER BY id DESC").fetchall()
    conn.close()
    html = f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Container Bazaar</h1><p>Navi Mumbai • Buy • Rent</p></div>
    <div class="container">'''
    if not containers: html += '<div class="empty"><h3>Koi container nahi mila</h3><p>Neeche + dabake pehla list karo</p></div>'
    for id, title, photo, city, type, price, deposit, phone in containers:
        html += f'''<div class="card">
        <img class="card-img" src="{photo}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container+Image'">
        <div class="card-body">
        <div><span class="tag">{type}</span><span class="tag">{city}</span></div>
        <h3>{title}</h3>
        <div class="price">₹{price:,}<span class="price-sub"> {'/day' if type=='Rent' else ''}</span></div>
        <div class="meta"><span>💰 Deposit: ₹{deposit:,}</span></div>
        <a href="/book/{id}"><button class="btn">Contact Seller</button></a>
        </div></div>'''
    return html + '</div><a href="/add"><button class="fab">+</button></a></body></html>'

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        data = (request.form['title'], request.form['photo'], request.form['city'],
                request.form['type'], int(request.form['price']), int(request.form['deposit']), request.form['phone'])
        conn = sqlite3.connect('database.db')
        conn.cursor().execute("INSERT INTO containers (title,photo,city,type,price,deposit,phone) VALUES (?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        return redirect('/')
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>List Your Container</h1><p>Free mein add karo</p></div>
    <div class="container"><div class="form-card"><form method="POST">
    <label>Container Title</label><input name="title" placeholder="20ft Dry Container" required>
    <label>Photo URL</label><input name="photo" type="url" placeholder="https://image-link.jpg" required>
    <label>City</label><input name="city" value="Navi Mumbai" required>
    <label>Listing Type</label><select name="type"><option value="Rent">Rent pe dena hai</option><option value="Sell">Bechna hai</option></select>
    <label>Price ₹</label><input name="price" type="number" placeholder="1500" required>
    <label>Security Deposit ₹</label><input name="deposit" type="number" placeholder="10000" required>
    <label>Your Phone</label><input name="phone" type="tel" placeholder="9876543210" required>
    <br><br><button class="btn btn-green">Post Now</button></form></div>
    <a href="/"><button class="btn btn-grey">Cancel</button></a></div></body></html>'''

@app.route('/book/<int:id>', methods=['GET','POST'])
def book(id):
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        conn.cursor().execute("INSERT INTO bookings (container_id,name,phone,start_date,end_date) VALUES (?,?,?,?,?)",
                              (id, request.form['name'], request.form['phone'], request.form['start'], request.form['end']))
        conn.commit()
        conn.close()
        return f'''<html><head>{STYLE}</head><body><div class="header"><h1>Success!</h1></div>
        <div class="container"><div class="form-card" style="text-align:center">
        <div style="font-size:48px">✅</div><h3 style="margin:15px 0">Request Sent</h3>
        <p style="color:#666;margin-bottom:20px">Owner ko {cont[7]} pe call/message karo ya wo tumhe contact karega</p>
        <a href="/"><button class="btn">Back to Home</button></a></div></div></body></html>'''
    conn.close()
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Book Container</h1></div><div class="container">
    <div class="card"><img class="card-img" src="{cont[2]}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container'">
    <div class="card-body"><h3>{cont[1]}</h3>
    <div class="price">₹{cont[5]:,}<span class="price-sub"> {'/day' if cont[4]=='Rent' else ''}</span></div>
    <div class="meta"><span>📍 {cont[3]}</span><span>💰 Deposit: ₹{cont[6]:,}</span></div>
    <div class="meta"><span>📞 {cont[7]}</span></div></div></div>
    <div class="form-card"><form method="POST">
    <label>Your Name</label><input name="name" required>
    <label>Phone Number</label><input name="phone" type="tel" required>
    <label>Start Date</label><input name="start" type="date" required>
    <label>End Date</label><input name="end" type="date" required>
    <br><br><button class="btn btn-green">Send Booking Request</button></form></div>
    <a href="/"><button class="btn btn-grey">Back</button></a></div></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)font-size:13px;color:#666;margin:8px 0;display:flex;gap:12px}
.btn{background:#002f34;color:white;border:none;padding:14px;border-radius:8px;font-size:15px;font-weight:600;width:100%;cursor:pointer;transition:0.2s}
.btn:active{transform:scale(0.98)}
.btn-green{background:#23e5db;color:#002f34}
.btn-grey{background:#e4e4e4;color:#002f34}
input,select{width:100%;padding:13px;border:2px solid #e4e4e4;border-radius:8px;font-size:15px;margin:8px 0;transition:0.2s}
input:focus,select:focus{outline:none;border-color:#23e5db}
label{font-weight:600;font-size:13px;color:#002f34;display:block;margin-top:12px}
.fab{position:fixed;bottom:20px;right:20px;background:#23e5db;color:#002f34;width:56px;height:56px;border-radius:50%;border:none;font-size:28px;box-shadow:0 6px 16px rgba(35,229,219,0.4);cursor:pointer;z-index:99}
.empty{text-align:center;padding:60px 20px;color:#999}
.empty h3{color:#666;margin-bottom:8px}
.form-card{background:white;border-radius:12px;padding:20px;margin:16px 0}
</style>'''

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    containers = conn.cursor().execute("SELECT * FROM containers ORDER BY id DESC").fetchall()
    conn.close()
    html = f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Container Bazaar</h1><p>Navi Mumbai • Buy • Rent</p></div>
    <div class="container">'''
    if not containers: html += '<div class="empty"><h3>Koi container nahi mila</h3><p>Neeche + dabake pehla list karo</p></div>'
    for id, title, photo, city, type, price, deposit, phone in containers:
        html += f'''<div class="card">
        <img class="card-img" src="{photo}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container+Image'">
        <div class="card-body">
        <div><span class="tag">{type}</span><span class="tag">{city}</span></div>
        <h3>{title}</h3>
        <div class="price">₹{price:,}<span class="price-sub"> {'/day' if type=='Rent' else ''}</span></div>
        <div class="meta"><span>💰 Deposit: ₹{deposit:,}</span></div>
        <a href="/book/{id}"><button class="btn">Contact Seller</button></a>
        </div></div>'''
    return html + '</div><a href="/add"><button class="fab">+</button></a></body></html>'

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        data = (request.form['title'], request.form['photo'], request.form['city'],
                request.form['type'], int(request.form['price']), int(request.form['deposit']), request.form['phone'])
        conn = sqlite3.connect('database.db')
        conn.cursor().execute("INSERT INTO containers (title,photo,city,type,price,deposit,phone) VALUES (?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        return redirect('/')
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>List Your Container</h1><p>Free mein add karo</p></div>
    <div class="container"><div class="form-card"><form method="POST">
    <label>Container Title</label><input name="title" placeholder="20ft Dry Container" required>
    <label>Photo URL</label><input name="photo" type="url" placeholder="https://image-link.jpg" required>
    <label>City</label><input name="city" value="Navi Mumbai" required>
    <label>Listing Type</label><select name="type"><option value="Rent">Rent pe dena hai</option><option value="Sell">Bechna hai</option></select>
    <label>Price ₹</label><input name="price" type="number" placeholder="1500" required>
    <label>Security Deposit ₹</label><input name="deposit" type="number" placeholder="10000" required>
    <label>Your Phone</label><input name="phone" type="tel" placeholder="9876543210" required>
    <br><br><button class="btn btn-green">Post Now</button></form></div>
    <a href="/"><button class="btn btn-grey">Cancel</button></a></div></body></html>'''

@app.route('/book/<int:id>', methods=['GET','POST'])
def book(id):
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        conn.cursor().execute("INSERT INTO bookings (container_id,name,phone,start_date,end_date) VALUES (?,?,?,?,?)",
                              (id, request.form['name'], request.form['phone'], request.form['start'], request.form['end']))
        conn.commit()
        conn.close()
        return f'''<html><head>{STYLE}</head><body><div class="header"><h1>Success!</h1></div>
        <div class="container"><div class="form-card" style="text-align:center">
        <div style="font-size:48px">✅</div><h3 style="margin:15px 0">Request Sent</h3>
        <p style="color:#666;margin-bottom:20px">Owner ko {cont[7]} pe call/message karo ya wo tumhe contact karega</p>
        <a href="/"><button class="btn">Back to Home</button></a></div></div></body></html>'''
    conn.close()
    return f'''<html><head>{STYLE}</head><body>
    <div class="header"><h1>Book Container</h1></div><div class="container">
    <div class="card"><img class="card-img" src="{cont[2]}" onerror="this.src='https://via.placeholder.com/600x400/002f34/ffffff?text=Container'">
    <div class="card-body"><h3>{cont[1]}</h3>
    <div class="price">₹{cont[5]:,}<span class="price-sub"> {'/day' if cont[4]=='Rent' else ''}</span></div>
    <div class="meta"><span>📍 {cont[3]}</span><span>💰 Deposit: ₹{cont[6]:,}</span></div>
    <div class="meta"><span>📞 {cont[7]}</span></div></div></div>
    <div class="form-card"><form method="POST">
    <label>Your Name</label><input name="name" required>
    <label>Phone Number</label><input name="phone" type="tel" required>
    <label>Start Date</label><input name="start" type="date" required>
    <label>End Date</label><input name="end" type="date" required>
    <br><br><button class="btn btn-green">Send Booking Request</button></form></div>
    <a href="/"><button class="btn btn-grey">Back</button></a></div></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        data = (request.form['title'], request.form['photo'], request.form['city'],
                request.form['type'], request.form['price'], request.form['deposit'], request.form['phone'])
        conn = sqlite3.connect('database.db')
        conn.cursor().execute("INSERT INTO containers (title,photo,city,type,price,deposit,phone) VALUES (?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        return redirect('/')
    return '''<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:sans-serif;padding:10px} input,select{padding:8px;width:100%;margin:5px 0;font-size:16px} button{padding:12px;width:100%;background:blue;color:white;border:none}</style></head><body>
    <h2>Container List Karo</h2><form method="POST">
    Title: <input name="title" placeholder="20ft Container" required><br>
    Photo URL: <input name="photo" placeholder="Google se image link" required><br>
    City: <input name="city" value="Mumbai" required><br>
    Type: <select name="type"><option>Rent</option><option>Sell</option></select><br>
    Price ₹: <input name="price" type="number" required><br>
    Deposit ₹: <input name="deposit" type="number" required><br>
    Phone: <input name="phone" required><br><br><button>List Kar Do</button></form><br><a href="/">Back</a></body></html>'''

@app.route('/book/<int:id>', methods=['GET','POST'])
def book(id):
    conn = sqlite3.connect('database.db')
    cont = conn.cursor().execute("SELECT * FROM containers WHERE id=?", (id,)).fetchone()
    if request.method == 'POST':
        conn.cursor().execute("INSERT INTO bookings (container_id,name,phone,start_date,end_date) VALUES (?,?,?,?,?)",
                              (id, request.form['name'], request.form['phone'], request.form['start'], request.form['end']))
        conn.commit()
        conn.close()
        return f'''<html><body style="font-family:sans-serif;padding:20px"><h2>Booking Done!</h2><p>Owner {cont[7]} call karega.</p><a href='/'>Home</a></body></html>'''
    conn.close()
    return f'''<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{{font-family:sans-serif;padding:10px}} input{{padding:8px;width:100%;margin:5px 0;font-size:16px}} button{{padding:12px;width:100%;background:green;color:white;border:none}}</style></head><body>
    <h2>Book: {cont[1]}</h2><img src="{cont[2]}" width="100%" style="max-width:300px"><br><br>
    <b>₹{cont[5]}</b> {'per day' if cont[4]=='Rent' else 'total'}<br><br><form method="POST">
    Naam: <input name="name" required><br>Phone: <input name="phone" required><br>
    Start: <input name="start" type="date" required><br>End: <input name="end" type="date" required><br><br>
    <button>Confirm Booking</button></form><br><a href="/">Cancel</a></body></html>'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
