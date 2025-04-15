from flask import Flask, render_template, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)


DATABASE = 'barberia.db'


@app.route('/')
def index():
    return render_template('index.html')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            servicio TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/citas', methods=['GET'])
def obtener_citas():
    conn = get_db_connection()
    citas = conn.execute('SELECT * FROM citas ORDER BY fecha, hora').fetchall()
    conn.close()
    

    citas_list = [dict(cita) for cita in citas]
    return jsonify(citas_list)

@app.route('/api/citas', methods=['POST'])
def crear_cita():
    data = request.get_json()
    

    required_fields = ['cliente', 'fecha', 'hora', 'servicio']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO citas (cliente, fecha, hora, servicio) VALUES (?, ?, ?, ?)',
        (data['cliente'], data['fecha'], data['hora'], data['servicio'])
    )
    conn.commit()
    cita_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': cita_id, **data}), 201

@app.route('/api/citas/<int:cita_id>', methods=['PUT'])
def actualizar_cita(cita_id):
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE citas SET cliente = ?, fecha = ?, hora = ?, servicio = ? WHERE id = ?',
        (data['cliente'], data['fecha'], data['hora'], data['servicio'], cita_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Cita no encontrada'}), 404
    
    return jsonify({'id': cita_id, **data})

@app.route('/api/citas/<int:cita_id>', methods=['DELETE'])
def eliminar_cita(cita_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM citas WHERE id = ?', (cita_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'error': 'Cita no encontrada'}), 404
    
    return jsonify({'mensaje': 'Cita eliminada correctamente'})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    init_db()
    app.run(debug=True)