import psycopg2

from flask import Flask, jsonify, request
from flask_cors import CORS
from faker import Faker

app = Flask(__name__)
CORS(app)

conn = psycopg2.connect("dbname='theultdatabase' user='matt' host='localhost'")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR,
    phone VARCHAR,
    email VARCHAR NOT NULL UNIQUE,
    city VARCHAR,
    state VARCHAR,
    active BOOLEAN NOT NULL DEFAULT True
);
''')
conn.commit()


@app.route('/user/add', methods=['POST'])
def add_user():
    data = request.get_json()
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')
    email = data.get('email')
    city = data.get('city')
    state = data.get('state')
    
    cursor.execute('''
               INSERT INTO users (first_name, last_name, email, phone, city, state)
               VALUES (%s, %s, %s, %s, %s, %s);
               ''', (first_name, last_name, phone, email, city, state))
    conn.commit()
    return 'user added', 201


@app.route('/users', methods=['GET'])
def get_all_users():
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users")
    response = cursor.fetchall()
    
    if response:
        users = []
        for u in response:
            user_record = {
                "user_id": u[0],
                "first_name": u[1],
                "last_name": u[2],
                "email": u[3],
                "phone": u[4],
                "city": u[5],
                "state": u[6],
                "active": u[7]
            }
            users.append(user_record)
        return jsonify(users), 200
        
    return "no users found", 400


@app.route('/users/get/active', methods=['GET'])
def get_all_active_users():
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE active='t' ORDER BY user_id, first_name, last_name, email, phone, city, state, active")
    results = cursor.fetchall()
    
    if results:
        users = []
        for u in results:
            user_record = {
                'user_id':u[0],
                'first_name':u[1],
                'last_name':u[2],
                'email':u[3],
                'phone':u[4],
                'city':u[5],
                'state':u[6],
                'active':u[7]
            }
            users.append(user_record)
        return jsonify(users), 200
    
    return 'No users found', 404

@app.route('/users/get/inactive', methods=['GET'])
def get_all_inactive_users():
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, active FROM users WHERE active='f'")
    results = cursor.fetchall()
    
    if results:
        for u in results:
            users = []
            user_record = {
                "user_id": u[0],
                "first_name": u[1],
                "last_name": u[2],
                "email": u[3],
                "phone": u[4],
                "city": u[5],
                "state": u[6],
                "active": u[7]
            }
            users.append(user_record)
        return jsonify(users), 200
    
    return "no users found", 404


@app.route('/users/populate', methods=['POST'])
def populate_mock_users():
    data = Faker()
    
    first_name = data.first_name()
    last_name = data.last_name()
    email = data.email()
    phone = data.phone_number()
    city = data.city()
    state = data.state()
    # active = data.get('active')
    
    cursor.execute("""
                    INSERT INTO users (first_name, last_name, email, phone, city, state)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,(first_name, last_name, email, phone, city, state))
    conn.commit()  
    return 'user added successfully', 201


@app.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    results = cursor.fetchone()
    
    if results:
        user = []
        user_record = {
            "user_id": results[0],
            "first_name": results[1],
            "last_name": results[2],
            "email": results[3],
            "phone": results[4],
            "city": results[5],
            "state": results[6],
            "active": results[7]
        }
        user.append(user_record)
        return jsonify(user), 200
    return "user not found", 404


@app.route('/users/update/<user_id>', methods=['POST'])
def update_user_by_id(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    
    data = request.get_json()
    user_id = data.get('user_id')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    active = data.get('active')
    
    if user_id is None:
        return "user_id is required", 400
    
    cursor.execute("UPDATE users SET first_name=%s, last_name=%s, email=%s, phone=%s, city=%s, state=%s, active=%s WHERE user_id=%s",
                   (first_name, last_name, email, phone, city, state, active, user_id))
    conn.commit()
    
    return "User updated successfully", 200

@app.route('/users/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id=%s', (user_id,))
    results = cursor.fetchone()
    if results:
        cursor.execute('DELETE FROM users WHERE user_id=%s', (user_id,))
        conn.commit()
        return jsonify(f"User_id {user_id} deleted successfully"), 200
    
    return jsonify(f"User with the id {user_id} not found"), 404
        

@app.route('/users/active/<user_id>', methods=['POST'])
def toggle_active(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()

    if user:
        active = user[7]
        new_active = not active
        cursor.execute("UPDATE users SET active=%s WHERE user_id=%s", (new_active, user_id))
        conn.commit()
        return "user updated successfully"
    else:
        return "user not found", 404
   
    

    
    
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8086)