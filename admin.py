from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database setup
DB_PATH = "car_tracker.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_plate TEXT NOT NULL,
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        color TEXT NOT NULL,
        year INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS speed_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER,
        speed REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        location TEXT,
        FOREIGN KEY (car_id) REFERENCES cars (id)
    )
    ''')

    # Insert some sample data if the database is empty
    cursor.execute("SELECT COUNT(*) FROM cars")
    if cursor.fetchone()[0] == 0:
        # Sample cars
        sample_cars = [
            ('ABC-123', 'Toyota', 'Corolla', 'Blue', 2018),
            ('XYZ-789', 'Honda', 'Civic', 'Red', 2020),
            ('DEF-456', 'Ford', 'Mustang', 'Black', 2019),
            ('GHI-789', 'Tesla', 'Model 3', 'White', 2022),
            ('JKL-012', 'BMW', 'X5', 'Silver', 2021)
        ]
        cursor.executemany('''
        INSERT INTO cars (license_plate, make, model, color, year)
        VALUES (?, ?, ?, ?, ?)
        ''', sample_cars)

        # Sample speed records
        for car_id in range(1, 6):
            sample_speeds = [
                (car_id, 65.5, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Highway 101'),
                (car_id, 45.2, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Main Street'),
                (car_id, 72.8, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Interstate 5')
            ]
            cursor.executemany('''
            INSERT INTO speed_records (car_id, speed, timestamp, location)
            VALUES (?, ?, ?, ?)
            ''', sample_speeds)

    conn.commit()
    conn.close()


@app.route('/admin')
def index():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
    SELECT c.id, c.license_plate, c.make, c.model, c.color, c.year,
           MAX(s.speed) as max_speed, AVG(s.speed) as avg_speed, COUNT(s.id) as record_count
    FROM cars c
    LEFT JOIN speed_records s ON c.id = s.car_id
    GROUP BY c.id
    ORDER BY c.id
    ''')

    cars = cursor.fetchall()
    conn.close()

    return render_template('index_admin.html', cars=cars)


@app.route('/car/<int:car_id>')
def car_details(car_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get car details
    cursor.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
    car = cursor.fetchone()

    # Get speed records for this car
    cursor.execute('''
    SELECT id, speed, timestamp, location
    FROM speed_records
    WHERE car_id = ?
    ORDER BY timestamp DESC
    ''', (car_id,))

    speed_records = cursor.fetchall()
    conn.close()

    return render_template('car_details.html', car=car, speed_records=speed_records)


@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        license_plate = request.form['license_plate']
        make = request.form['make']
        model = request.form['model']
        color = request.form['color']
        year = request.form['year']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO cars (license_plate, make, model, color, year)
        VALUES (?, ?, ?, ?, ?)
        ''', (license_plate, make, model, color, year))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_car.html')


@app.route('/add_speed/<int:car_id>', methods=['GET', 'POST'])
def add_speed(car_id):
    if request.method == 'POST':
        speed = float(request.form['speed'])
        location = request.form['location']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO speed_records (car_id, speed, timestamp, location)
        VALUES (?, ?, ?, ?)
        ''', (car_id, speed, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), location))

        conn.commit()
        conn.close()

        return redirect(url_for('car_details', car_id=car_id))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
    car = cursor.fetchone()
    conn.close()

    return render_template('add_speed.html', car=car)


if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        # If database exists but may not have all the tables
        init_db()

    app.run(debug=True)