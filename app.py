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

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    containers = conn.cursor().execute("SELECT * FROM containers").fetchall()
    conn.close()
    html = '''<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{font-family:sans-serif;padding:10px} button{padding:12px;border:none;border-radius:5px;font-size:16px;width:100%} input,select{padding:8px;width:100%;margin:5px 0;font-size:16px}.card{border:1px solid #ccc;padding:15px;margin:10px 0;border-radius:8px}</style></head><body>
    <h1>Container Bazaar - Mumbai</h1>
    <a href="/add"><button style="background:#007bff;color:white">+ Apna Container List Karo</button></a><hr>'''
    if not containers: html += '<p>Abhi koi container nahi hai. Pehla tum list karo!</p>'
    for id, title, photo, city, type, price, deposit, phone in containers:
        html += f'''<div class="card"><h3>{title}</h3><img src="{photo}" width="100%" style="max-width:300px"><br><br>
        <b>{city}</b> | <b>{type}</b><br><b>Price:</b> ₹{price} {'/day' if type=='Rent' else ''}<br>
        <b>Deposit:</b> ₹{deposit} | <b>Call:</b> {phone}<br><br>
        <a href="/book/{id}"><button style="background:green;color:white">Book Now</button></a></div>'''
    return html + '</body></html>'

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
