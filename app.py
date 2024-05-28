from flask import Flask, render_template,request,session


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard_user.html")

@app.route("/registrasi")
def registrasi():
    return render_template("registrasi.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)