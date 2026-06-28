from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Config - Yahan apna number aur UPI daal de
ADMIN_PASSWORD = 'chaitanya@2011'  # Isse badal dena
WHATSAPP_NUMBER = '9664006523'  # Tera number: 91 + number
UPI_ID = 'name@upi'  # Teri UPI ID
BUSINESS_NAME = 'Container Bazaar'

# Dummy data
containers = [
    {'id': 1, 'size': '20ft', 'type': 'Standard', 'price': 2500, 'location': 'Mumbai', 'available': True},
    {'id': 2, 'size': '40ft', 'type': 'High Cube', 'price': 4000, 'location': 'Delhi', 'available': True},
    {'id': 3, 'size': '20ft', 'type': 'Refrigerated', 'price': 3500, 'location': 'Chennai', 'available': True},
    {'id': 4, 'size': '40ft', 'type': 'Standard', 'price': 4200, 'location': 'Mumbai', 'available': True},
]

bookings = []

@app.route('/')
def index():
    return render_template('index.html', containers=containers)

@app.route('/book/<int:container_id>', methods=['GET', 'POST'])
def book(container_id):
    container = next((c for c in containers if c['id'] == container_id), None)
    if not container:
        flash('Container not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        start_date = request.form.get('start', '').strip()
        days = request.form.get('days', '').strip()
        
        # Validation
        errors = {}
        if not name:
            errors['name'] = 'Name required'
        if not phone or len(phone) < 10:
            errors['phone'] = 'Valid phone required'
        if not start_date:
            errors['start'] = 'Start date required'
        if not days or not days.isdigit():
            errors['days'] = 'Valid days required'
            
        if errors:
            return render_template('book.html', container=container, errors=errors)
        
        # Calculate total
        total = container['price'] * int(days)
        booking_id = secrets.token_hex(4).upper()
        
        booking = {
            'id': booking_id,
            'container_id': container_id,
            'name': name,
            'phone': phone,
            'start': start_date,
            'days': int(days),
            'total': total,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        bookings.append(booking)
        
        return redirect(url_for('confirm', booking_id=booking_id))
    
    return render_template('book.html', container=container, errors={})

@app.route('/confirm/<booking_id>')
def confirm(booking_id):
    booking = next((b for b in bookings if b['id'] == booking_id), None)
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('index'))
    
    container = next((c for c in containers if c['id'] == booking['container_id']), None)
    upi_link = f'upi://pay?pa={UPI_ID}&pn={BUSINESS_NAME}&am={booking["total"]}&cu=INR&tn=Container{booking_id}'
    whatsapp_msg = f'Hi, I booked Container ID {booking["container_id"]} for {booking["days"]} days. Booking ID: {booking_id}. Total: Rs {booking["total"]}'
    whatsapp_link = f'https://wa.me/{WHATSAPP_NUMBER}?text={whatsapp_msg}'
    
    return render_template('confirm.html', booking=booking, container=container, upi_link=upi_link, whatsapp_link=whatsapp_link)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Wrong password', 'error')
    
    if session.get('admin'):
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    return render_template('dashboard.html', bookings=bookings, containers=containers)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
