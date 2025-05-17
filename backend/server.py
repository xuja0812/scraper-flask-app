import os
from flask import Flask, request, jsonify, session, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from new_model import analyze_reviews
from dotenv import load_dotenv
import json

load_dotenv()  

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
CORS(app, supports_credentials=True)  

app.secret_key = os.getenv('FLASK_SECRET_KEY')
if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY not set in environment")

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'testbase')

mysql = MySQL(app)

def get_user_id(username):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM user WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return user[0]
    return None

@app.route('/api/generate', methods=['POST'])
def generate_api():
    if 'loggedin' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        url = data.get('url')
        num_reviews = int(data.get('num_reviews', 10))
        if not url:
            return jsonify({"error": "Missing URL parameter"}), 400

        result = analyze_reviews(url, num_reviews)

        user_id = get_user_id(session['username'])
        if user_id:
            summary = result.get('summary', {})
            positive = summary.get('positive')
            negative = summary.get('negative')
            neutral = summary.get('neutral') if 'neutral' in summary else (summary.get('total', 0) - positive - negative if summary else None)
            total = summary.get('total')
            average_score = summary.get('average_score')
            raw_result = json.dumps(result)  # store full result as JSON string

            cursor = mysql.connection.cursor()
            cursor.execute(
                """
                INSERT INTO scrapes (user_id, url, positive, negative, neutral, total, average_score, raw_result)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, url, positive, negative, neutral, total, average_score, raw_result)
            )
            mysql.connection.commit()
            cursor.close()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process reviews: {str(e)}"}), 500

@app.route('/api/scrapes', methods=['GET'])
def get_scrapes():
    if 'loggedin' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = get_user_id(session['username'])
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, url, positive, negative, neutral, total, average_score, created_at
        FROM scrapes
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()

    scrapes = []
    for r in rows:
        scrapes.append({
            "id": r[0],
            "url": r[1],
            "positive": r[2],
            "negative": r[3],
            "neutral": r[4],
            "total": r[5],
            "average_score": float(r[6]) if r[6] is not None else None,
            "created_at": r[7].isoformat() if r[7] else None
        })

    return jsonify({"scrapes": scrapes}), 200

@app.route('/api/register', methods=['POST'])
def register_api():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        hashed_pw = generate_password_hash(password)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        if cursor.fetchone():
            cursor.close()
            return jsonify({"error": "User already exists"}), 400

        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, hashed_pw))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"msg": "Registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_api():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):
            session['loggedin'] = True
            session['username'] = user[1]
            return jsonify({"msg": "Login successful", "username": user[1]}), 200
        else:
            return jsonify({"error": "Incorrect username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout_api():
    session.clear()
    return jsonify({"msg": "Logged out"}), 200

# not in use right now, should add tab in frontend
@app.route('/api/delete', methods=['POST'])
def delete_api():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            cursor.execute("DELETE FROM user WHERE username=%s", (username,))
            mysql.connection.commit()
            cursor.close()
            session.clear()
            return jsonify({"msg": "Account deleted"}), 200
        else:
            cursor.close()
            return jsonify({"error": "Incorrect username or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
