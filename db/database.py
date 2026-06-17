import sqlite3
import json
import os

DB_PATH = 'tiro_simulator.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de tiros (relacionada con un usuario y con el JSON del Grupo 2 completo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            shot_id TEXT UNIQUE NOT NULL,
            result TEXT,
            raw_json TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_or_create_user(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Intentar obtener al usuario
    cursor.execute('SELECT id, name FROM users WHERE name = ?', (name,))
    row = cursor.fetchone()
    
    if row is None:
        # Crear usuario si no existe
        cursor.execute('INSERT INTO users (name) VALUES (?)', (name,))
        conn.commit()
        user_id = cursor.lastrowid
    else:
        user_id = row[0]
        
    conn.close()
    return user_id

def log_shot(user_id, shot_result_json):
    # shot_result_json es el string JSON oficial generado y validado por el Grupo 2
    try:
        data = json.loads(shot_result_json)
        shot_id = data.get('shot_id')
        result = data.get('result')
        
        if not shot_id or not result:
            return False

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO shots (user_id, shot_id, result, raw_json)
            VALUES (?, ?, ?, ?)
        ''', (user_id, shot_id, result, shot_result_json))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error guardando tiro en BD: {e}")
        return False

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM users ORDER BY name ASC')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]
