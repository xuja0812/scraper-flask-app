from flask import Flask, request, render_template, session, redirect, url_for
from new_model import model_data
import mysql.connector
from flask_mysqldb import MySQL

conn = mysql.connector.connect(host="localhost", port="3307",user="root", password="", database="testbase")
cursor = conn.cursor()

app = Flask(__name__)
app.secret_key = 'super secret key'
primary = 0

# MAIN PAGE TO GENERATE REVIEWS

@app.route('/', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        company = request.form.get("cname")
        num = request.form.get("num")
        url = "https://www.facebook.com/"+company+"/reviews"
        output = model_data(url, int(num))
        return render_template("output.html",msg=output)
    if 'username' in session:
        return render_template("form.html", username=session['username'])
    else:
        return render_template("form.html")

@app.route('/home')
def home():
    if('username' in session):
        return render_template("form.html", username=session['username'])
    else:
        return render_template("form.html")

# ALLOWS A USER TO REGISTER THEIR USERNAME AND PASSWORD

@app.route('/register', methods=['GET','POST'])
def register():
    msg=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('INSERT INTO user (user, username, password) VALUES (%s, %s, %s)',(primary, username, password))
        primary += 1
        conn.commit()
        msg = "Registered successfully"
    return render_template('register.html', msg=msg)

# ALLOWS A USER TO LOG IN TO THEIR ACCOUNT

@app.route('/login', methods=['GET','POST'])
def login():
    msg=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM user WHERE username=%s AND password=%s',(username, password))

        record = cursor.fetchone()
        if record: # session is the duration where the user logs in and out
            session['loggedin'] = True
            session['username'] = record[1]
            # return redirect(url_for('home'))
            return render_template('form.html',username=session['username'])
        else:
            msg='Incorrect username or password, try again.'
    if 'username' in session:
        msg = "You are already logged in."
    return render_template('index.html', msg=msg)

# ALLOWS A USER TO LOG OUT OF THEIR ACCOUNT

@app.route('/logout', methods=['GET','POST'])
def logout():
    if request.method == 'POST':
        session.pop('loggedin', None)
        session.pop('username', None)
    return render_template("logout.html")

# ALLOWS A USER TO DELETE THEIR PROFILE

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    msg = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('DELETE FROM user WHERE username=%s AND password=%s',(username, password))
        msg = "Sucessfully deleted account"
    return render_template('delete.html',msg=msg)

if(__name__=='__main__'):
    app.run()
