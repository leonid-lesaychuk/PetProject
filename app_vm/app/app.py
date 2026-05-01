from flask import Flask, render_template, request, redirect, url_for
from prometheus_flask_exporter import PrometheusMetrics
import psycopg2
from psycopg2.extras import RealDictCursor
import os

import os
print(os.environ['DATABASE_URL']) 

app = Flask(__name__)
metrics = PrometheusMetrics(app) 

def get_db_connection():
    # Берем из окружения, если нет — используем значение по умолчанию
    url = os.getenv('DATABASE_URL', 'postgresql://postgres:sql@db:5432/mydb')
    return psycopg2.connect(url)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM messages ORDER BY created_at DESC')
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)',
        (name, email, message)
    )
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)