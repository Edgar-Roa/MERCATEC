from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

conn_str = "dbname=MERCATEC user=postgres password=postgresql host=localhost"

# Ruta para la página de inicio
@app.route('/')
def index():
    return redirect(url_for('login'))  # Redirige a la página de login

# Ruta para el registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        email = request.form['email']
        password = request.form['password']

        # Encriptar la contraseña
        password_hash = generate_password_hash(password)

        # Conectar a la base de datos
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()

        # Insertar usuario en la base de datos
        try:
            cur.execute("""
                INSERT INTO usuarios (nombre, telefono, email, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (nombre, telefono, email, password_hash))
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            return render_template('registro.html', error="El usuario ya existe o el teléfono/email está en uso.")
        finally:
            cur.close()
            conn.close()

        # Redirigir a la página de inicio de sesión después del registro
        return redirect(url_for('login'))

    return render_template('registro.html')

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Conectar a la base de datos
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()

        # Consultar usuario en la base de datos
        cur.execute("SELECT password_hash FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        cur.close()
        conn.close()

        # Verificar si la contraseña es correcta
        if usuario and check_password_hash(usuario[0], password):
            # Redirigir a la página principal
            return redirect(url_for('principal'))
        else:
            # Mostrar error de login
            return render_template('login.html', error='Credenciales inválidas')

    return render_template('login.html')

# Ruta para la página principal
@app.route('/principal')
def principal():
    # Conectar a la base de datos para obtener productos
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    
    # Consultar los productos disponibles en la base de datos
    cur.execute("SELECT titulo, descripcion, precio FROM productos WHERE disponible = TRUE")
    productos = cur.fetchall()
    
    cur.close()
    conn.close()

    # Renderizar la plantilla principal.html y pasar los productos
    return render_template('principal.html', productos=productos)

# Ruta para la página de mensajes
@app.route('/mensajes')
def mensajes():
    # Conectar a la base de datos para obtener las conversaciones
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    
    # Consulta para obtener las conversaciones o mensajes recientes
    cur.execute("""
        SELECT u.nombre, m.contenido, m.fecha_envio
        FROM mensajes m
        JOIN usuarios u ON m.emisor_id = u.id
        ORDER BY m.fecha_envio DESC
        LIMIT 10
    """)
    conversaciones = cur.fetchall()
    
    cur.close()
    conn.close()

    # Renderizar la plantilla mensajes.html y pasar las conversaciones
    return render_template('mensajes.html', conversaciones=conversaciones)

if __name__ == '__main__':
    app.run(debug=True)
