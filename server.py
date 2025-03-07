from flask import Flask, request, render_template, session, redirect, url_for, flash
from new_model import model_data
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super_secret_key')

# Database Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'testbase'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        company = request.form.get("cname")
        num = request.form.get("num")
        url = f"https://www.facebook.com/{company}/reviews"
        output = model_data(url, int(num))
        return render_template("output.html", msg=output)
    return render_template("form.html", username=session.get('username'))

@app.route('/home')
def home():
    return render_template("form.html", username=session.get('username'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO user (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        cursor.close()
        
        flash("Registered successfully", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE username=%s', (username,))
        record = cursor.fetchone()
        cursor.close()
        
        if record and check_password_hash(record[2], password):
            session['loggedin'] = True
            session['username'] = record[1]
            flash("Login successful", "success")
            return redirect(url_for('home'))
        else:
            flash("Incorrect username or password", "danger")
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE username=%s', (username,))
        record = cursor.fetchone()
        
        if record and check_password_hash(record[2], password):
            cursor.execute('DELETE FROM user WHERE username=%s', (username,))
            mysql.connection.commit()
            cursor.close()
            session.clear()
            flash("Account successfully deleted", "success")
            return redirect(url_for('register'))
        else:
            flash("Incorrect username or password", "danger")
    return render_template('delete.html')

if __name__ == '__main__':
    app.run(debug=True)
