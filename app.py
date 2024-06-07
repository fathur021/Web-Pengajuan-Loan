from flask import Flask, render_template, request, session, redirect, flash, url_for, jsonify
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import pandas as pd
import numpy as np
import logging
from functools import wraps
import binascii

# Decorator untuk memeriksa apakah pengguna telah login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_secret_key():
    return binascii.hexlify(os.urandom(24)).decode()
# Decorator untuk memeriksa role admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You must be logged in to access this page.", "error")
            return redirect(url_for('login'))
        if session.get('role') != 1:
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

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

# Load the pre-trained model
try:
    model = joblib.load('gb.pkl')
except Exception as e:
    logging.error(f"Error loading model: {str(e)}")
    raise

# Definisikan fungsi preprocess_features
def preprocess_features(data):
    logging.debug(f"Data before preprocessing: {data}")

    # Mapping for categorical features
    data['Married'] = 1 if data.get('Married').lower() == 'yes' else 0
    data['Gender'] = 1 if data.get('Gender').lower() == 'male' else 0
    data['Education'] = 1 if data.get('Education').lower() == 'graduate' else 0
    data['Self_Employed'] = 1 if data.get('Self_Employed').lower() == 'yes' else 0
    data['Credit_History'] = 1 if data.get('Credit_History') == 1 else 0

    # Mapping for Property_Area
    area_mapping = {'rural': 0, 'semiurban': 1, 'urban': 2}
    data['Property_Area'] = area_mapping.get(data.get('Property_Area').lower(), 0)

    # Convert numeric fields to appropriate types
    try:
        data['Dependents'] = int(data.get('Dependents', '0'))
    except ValueError as e:
        logging.error(f"Error converting Dependents: {e}")
        data['Dependents'] = 0

    try:
        data['ApplicantIncome'] = float(data.get('ApplicantIncome', 0))
    except ValueError as e:
        logging.error(f"Error converting ApplicantIncome: {e}")
        data['ApplicantIncome'] = 0.0

    try:
        data['CoapplicantIncome'] = float(data.get('CoapplicantIncome', 0))
    except ValueError as e:
        logging.error(f"Error converting CoapplicantIncome: {e}")
        data['CoapplicantIncome'] = 0.0

    try:
        data['LoanAmount'] = float(data.get('LoanAmount', 0))
    except ValueError as e:
        logging.error(f"Error converting LoanAmount: {e}")
        data['LoanAmount'] = 0.0

    try:
        data['Loan_Amount_Term'] = float(data.get('Loan_Amount_Term', 0))
    except ValueError as e:
        logging.error(f"Error converting Loan_Amount_Term: {e}")
        data['Loan_Amount_Term'] = 0.0

    logging.debug(f"Data after preprocessing: {data}")
    return data

# Define the feature names
feature_names = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed',
                 'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount',
                 'Loan_Amount_Term', 'Credit_History', 'Property_Area']


@app.route("/")
def index():
    return render_template("login.html")

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
        cur.execute("SELECT id, password, role FROM users WHERE email = %s", [email])
        user = cur.fetchone()

        # Close connection
        cur.close()

        if user:
            stored_password = user[1]
            if check_password_hash(stored_password, password):
                session['user_id'] = user[0]
                session['role'] = user[2]  # buat role dalam sesi
                
                if session['role'] == 1:  # jika role adalah 1 (admin)    
                    flash("Login successful!", "success")
                    return redirect(url_for('dashboard_admin'))
                else:  # jika role aku dan kamu adalah  0 (pengguna biasa)
                    flash("Login berhasil!", "success")
                    return redirect(url_for('loan_history'))
            else:
                flash("Invalid email or password!", "error")
                return redirect(url_for('login'))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('role', None)  # Hapus role dari sesi
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('login'))

@app.route("/dashboard_user", methods=["GET", "POST"])
def submit_user():
    logging.debug(f"Session before checking user_id: {session}")
    
    if 'user_id' not in session:
        flash("You must be logged in to submit data!", "error")
        return redirect(url_for('login'))  # Redirect ke halaman login jika pengguna belum login

    logging.debug(f"User ID in session: {session['user_id']}")
    
    if request.method == "POST":
        # Ambil data dari formulir
        Gender = request.form['gender']
        Married = request.form['married']
        Dependents = request.form['dependents']
        Education = request.form['education']
        Self_Employed = request.form['self-employed']
        ApplicantIncome = request.form['applicant-income']
        CoapplicantIncome = request.form['coapplicant-income']
        LoanAmount = request.form['loan-amount']
        Loan_Amount_Term = request.form['loan-amount-term']
        Credit_History = request.form['credit-history']
        Property_Area = request.form['property-area']

        try:
            cursor = mysql.connection.cursor()

            # Simpan data ke dalam database
            # Menggunakan parameterized query untuk menghindari SQL injection
            sql_query = """
            INSERT INTO data_user 
            (user_id, Gender, Married, Dependents, Education, Self_Employed, ApplicantIncome, 
            CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History, Property_Area) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_query, (session['user_id'], Gender, Married, Dependents, Education, 
                                        Self_Employed, ApplicantIncome, CoapplicantIncome, LoanAmount, 
                                        Loan_Amount_Term, Credit_History, Property_Area))

            mysql.connection.commit()
            cursor.close()

            flash("Data submitted successfully!", "success")
            return redirect(url_for('submit_user'))  # Redirect kembali ke halaman utama setelah berhasil mengirimkan data
        except Exception as e:
            flash(f"Failed to submit data: {str(e)}", "error")
            logging.error(f"Failed to submit data: {str(e)}")
            return redirect(url_for('index'))  # Redirect kembali ke halaman utama jika terjadi kesalahan
    else:
        return render_template("dashboard_user.html")  # Misalnya, template HTML untuk halaman dashboard pengguna

@app.route("/loan_history")
def loan_history():
    if 'user_id' in session:
        try:
            cursor = mysql.connection.cursor()
            
            # Mengambil data pinjaman aktif dari tabel data_user
            query_active = """
            SELECT 'active' AS status, du.Gender, du.Married, du.Dependents, du.Education, 
                   du.Self_Employed, du.ApplicantIncome, du.CoapplicantIncome, du.LoanAmount, 
                   du.Loan_Amount_Term, du.Credit_History, du.Property_Area, du.loan_status
            FROM data_user du
            WHERE du.user_id = %s
            """
            cursor.execute(query_active, [session['user_id']])
            active_loans = cursor.fetchall()
            
            # Mengambil data pinjaman yang sudah selesai dari tabel completed_loans
            query_completed = """
            SELECT 'completed' AS status, cl.Gender, cl.Married, cl.Dependents, cl.Education, 
                   cl.Self_Employed, cl.ApplicantIncome, cl.CoapplicantIncome, cl.LoanAmount, 
                   cl.Loan_Amount_Term, cl.Credit_History, cl.Property_Area, cl.loan_status
            FROM completed_loans cl
            WHERE cl.user_id = %s
            """
            cursor.execute(query_completed, [session['user_id']])
            completed_loans = cursor.fetchall()
            
            cursor.close()

            # Convert loan_data to a list of dictionaries
            loan_data_dicts = []
            for row in active_loans + completed_loans:
                loan_data_dicts.append({
                    'status': row[0],
                    'Gender': row[1],
                    'Married': row[2],
                    'Dependents': row[3],
                    'Education': row[4],
                    'Self_Employed': row[5],
                    'ApplicantIncome': row[6],
                    'CoapplicantIncome': row[7],
                    'LoanAmount': row[8],
                    'Loan_Amount_Term': row[9],
                    'Credit_History': row[10],
                    'Property_Area': row[11],
                    'loan_status': row[12]
                    
                })

            return render_template("loan_history.html", loan_data=loan_data_dicts)
        except Exception as e:
            flash(f"Gagal mengambil data pinjaman: {str(e)}", "error")
            return redirect(url_for('index'))
    else:
        flash("Anda harus login untuk melihat halaman ini!", "error")
        return redirect(url_for('login'))

@app.route("/dashboard_admin")
def dashboard_admin():
    # Pastikan pengguna telah login
    if 'user_id' in session:
        # Periksa peran pengguna
        if session['role'] == 1:  # Jika peran adalah admin
            try:
                cursor = mysql.connection.cursor()
                query = """
                SELECT du.user_id, u.name, du.Gender, du.Married, du.Dependents, du.Education, 
                       du.Self_Employed, du.ApplicantIncome, du.CoapplicantIncome, du.LoanAmount, 
                       du.Loan_Amount_Term, du.Credit_History, du.Property_Area
                FROM data_user du
                JOIN users u ON du.user_id = u.id
                """
                cursor.execute(query)
                user_data = cursor.fetchall()
                cursor.close()
                
                # Convert user_data to a list of dictionaries with processed feature values
                user_data_dicts = []
                for row in user_data:
                    user_data_dicts.append({
                        'user_id': row[0],
                        'Name': row[1],
                        'Gender': row[2],
                        'Married': row[3],
                        'Dependents': row[4],
                        'Education': row[5],
                        'Self_Employed': row[6],
                        'ApplicantIncome': row[7],
                        'CoapplicantIncome': row[8],
                        'LoanAmount': row[9],
                        'Loan_Amount_Term': row[10],
                        'Credit_History': row[11],
                        'Property_Area': row[12],
                        
                    })
                
                # Send user data with processed feature values to the HTML template
                return render_template("dashboard_admin.html", user_data=user_data_dicts)
            except Exception as e:
                flash(f"Failed to fetch user data: {str(e)}", "error")
                return redirect(url_for('login'))
        else:  # Jika peran bukan admin
            flash("You do not have permission to access this page!", "error")
            return redirect(url_for('login'))
    else:  # Jika pengguna belum login
        flash("You must be logged in to access this page!", "error")
        return redirect(url_for('login'))

@app.route('/predict_loan_status', methods=['POST'])
def predict_loan_status():
    try:
        data = request.get_json(force=True)
        logging.debug(f"Received data: {data}")

        # Ensure all features are present in the input data
        required_features = ['Gender', 'Married', 'Dependents', 'Education', 'Self_Employed', 
                             'ApplicantIncome', 'CoapplicantIncome', 'LoanAmount', 'Loan_Amount_Term', 
                             'Credit_History', 'Property_Area']

        missing_features = [feature for feature in required_features if feature not in data]
        if missing_features:
            raise ValueError(f"Missing features: {', '.join(missing_features)}")

        # Preprocess the input data
        input_data = preprocess_features(data)

        # Convert the data to a pandas DataFrame
        input_df = pd.DataFrame([input_data], columns=required_features)

        logging.debug(f"DataFrame before type conversion: {input_df.dtypes}")

        # Ensure correct data types
        input_df = input_df.astype({
            'Gender': 'int32', 'Married': 'int32', 'Dependents': 'int32',
            'Education': 'int32', 'Self_Employed': 'int32',
            'ApplicantIncome': 'int64', 'CoapplicantIncome': 'int32',
            'LoanAmount': 'int32', 'Loan_Amount_Term': 'int32',
            'Credit_History': 'int32', 'Property_Area': 'int32'
        })

        logging.debug(f"DataFrame after type conversion: {input_df.dtypes}")

        # Predict the loan status
        prediction = model.predict(input_df)
        logging.debug(f"Prediction: {prediction}")

        # Convert prediction to a JSON serializable format
        prediction_value = int(prediction[0])

        # Save the prediction to the database
        try:
            cursor = mysql.connection.cursor()

            # Update the loan status in the database for the given user_id
            update_query = """
            UPDATE data_user
            SET loan_status = %s
            WHERE user_id = %s
            """
            cursor.execute(update_query, (prediction_value, data['user_id']))

            mysql.connection.commit()
            cursor.close()

            logging.debug(f"Prediction saved to database for user_id: {data['user_id']}")

        except Exception as e:
            logging.error(f"Failed to save prediction to database: {str(e)}")
            return jsonify({'error': f"Failed to save prediction to database: {str(e)}"}), 500

        return jsonify({'prediction': prediction_value})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 400

    
@app.route("/admin_complete_loan_page")
def admin_complete_loan_page():
    app.logger.debug(f"Session data: {session}")

    try:
        cursor = mysql.connection.cursor()
        query = """
        SELECT du.user_id, u.name, du.Gender, du.Married, du.Dependents, du.Education, 
               du.Self_Employed, du.ApplicantIncome, du.CoapplicantIncome, du.LoanAmount, 
               du.Loan_Amount_Term, du.Credit_History, du.Property_Area, du.loan_status
        FROM data_user du
        JOIN users u ON du.user_id = u.id
        """
        cursor.execute(query)
        loan_data = cursor.fetchall()
        cursor.close()

        app.logger.debug(f"Fetched loan data: {loan_data}")

        loan_data_dicts = []
        for row in loan_data:
            loan_data_dict = {
                'user_id': row[0],
                'name': row[1],
                'Gender': row[2].capitalize(),
                'Married': 'Yes' if row[3].lower() == 'yes' else 'No',
                'Dependents': int(row[4]),
                'Education': row[5].capitalize(),
                'Self_Employed': 'Yes' if row[6].lower() == 'yes' else 'No',
                'ApplicantIncome': float(row[7]),
                'CoapplicantIncome': float(row[8]),
                'LoanAmount': float(row[9]),
                'Loan_Amount_Term': float(row[10]),
                'Credit_History': 'Yes' if row[11] == '1' else 'No',
                'Property_Area': row[12].capitalize(),
                'loan_status': 'Approved' if row[13] == '1' else 'Rejected'
            }
            loan_data_dicts.append(loan_data_dict)

        app.logger.debug(f"Processed loan data: {loan_data_dicts}")

        return render_template("admin_complete_loan_page.html", loan_data=loan_data_dicts)
    except Exception as e:
        app.logger.error(f"Error in admin_complete_loan_page: {str(e)}", exc_info=True)
        flash(f"Gagal mengambil data pinjaman: {str(e)}", "error")
        return redirect(url_for('dashboard_admin'))
    
@app.route("/complete_loan/<int:user_id>", methods=["POST"])
def complete_loan(user_id):
    if 'user_id' in session:
        try:
            with mysql.connection.cursor() as cursor:
                query = """
                SELECT user_id, Gender, Married, Dependents, Education, 
                       Self_Employed, ApplicantIncome, CoapplicantIncome, LoanAmount, 
                       Loan_Amount_Term, Credit_History, Property_Area, loan_status
                FROM data_user
                WHERE user_id = %s
                """
                cursor.execute(query, [user_id])
                loan_data = cursor.fetchone()

                if loan_data:
                    insert_query = """
                    INSERT INTO completed_loans 
                    (user_id, Gender, Married, Dependents, Education, 
                     Self_Employed, ApplicantIncome, CoapplicantIncome, LoanAmount, 
                     Loan_Amount_Term, Credit_History, Property_Area, loan_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, loan_data)

                    delete_query = "DELETE FROM data_user WHERE user_id = %s"
                    cursor.execute(delete_query, [user_id])

                    mysql.connection.commit()
                    flash("Pinjaman ditandai sebagai selesai!", "success")
                else:
                    flash("Tidak ada data pinjaman yang ditemukan untuk pengguna.", "error")

            return redirect(url_for('admin_complete_loan_page'))
        except Exception as e:
            app.logger.error(f"Error in complete_loan: {str(e)}", exc_info=True)
            flash(f"Gagal menyelesaikan pinjaman: {str(e)}", "error")
            return redirect(url_for('admin_complete_loan_page'))
    else:
        flash("Anda harus login untuk menyelesaikan pinjaman!", "error")
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
