from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)

# Konfigurasi database
app.config['MYSQL_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_PORT'] = int(os.environ.get('DB_PORT')) if os.environ.get('DB_PORT') else 3306
app.config['MYSQL_USER'] = os.environ.get('DB_USERNAME')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('DB_DATABASE')

mysql = MySQL(app)

# Fungsi untuk menghasilkan kunci rahasia
def generate_secret_key(length=24):
    import string
    import secrets
    alphabet = string.ascii_letters + string.digits
    secret_key = ''.join(secrets.choice(alphabet) for i in range(length))
    return secret_key

# Menetapkan secret_key untuk aplikasi Flask
app.secret_key = os.environ.get('SECRET_KEY') or generate_secret_key()

@app.route("/")
def index():
    if 'user_id' in session:
        return render_template("dashboard_user.html")
    else:
        return redirect(url_for('login'))

# Cek database
@app.route("/check_database")
def check_database():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        return f"Connected to database successfully! MySQL version: {version[0]}"
    except Exception as e:
        return f"Failed to connect to database: {str(e)}"

@app.route("/registrasi", methods=["GET", "POST"])
def registrasi():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']

        # Validasi bahwa kedua kolom kata sandi cocok
        if password != repeat_password:
            flash("Password and Repeat password must match!", "error")
            return redirect(url_for('registrasi'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash("Registration successful!", "success")
        return redirect(url_for('registrasi'))

    return render_template("registrasi.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("SELECT id, password FROM users WHERE email = %s", [email])
        user = cur.fetchone()

        # Close connection
        cur.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for('login'))

    return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)
