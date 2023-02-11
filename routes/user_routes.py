import psycopg2
from flask import jsonify, request, Blueprint
from flask_cors import CORS
from faker import Faker
from app import conn, cursor

app_users = Blueprint("app_users", __name__)

@app_users.route('/user/add', methods=['POST'])
def add_user():
    data = request.get_json()
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    org_id = data.get('org_id')
    phone = data.get('phone')
    email = data.get('email')
    city = data.get('city')
    state = data.get('state')
    
    cursor.execute('''
               INSERT INTO users (first_name, last_name, org_id, email, phone, city, state)
               VALUES (%s, %s, %s, %s, %s, %s, %s);
               ''', (first_name, last_name, org_id, phone, email, city, state))
    conn.commit()
    return 'user added', 201


@app_users.route('/users', methods=['GET'])
def get_all_users():
    cursor.execute("""
                    SELECT 
                        u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active,
                        o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type
                    FROM users u
                        JOIN organizations o
                            ON u.org_id = o.org_id
                    ORDER BY user_id ASC;
                   """)
    response = cursor.fetchall()
    
    if response:
        users = []
        for u in response:
            user_record = {
                "active": u[8],
                "city": u[5],
                "email": u[4],
                "first_name": u[1],
                "last_name": u[2],
                "organization": {
                    "active": u[14],
                    "city": u[12],
                    "name": u[10],
                    "org_id": u[9],
                    "phone": u[11],
                    "state": u[13],
                    "type": u[15]
                },
                "phone": u[3],
                "state": u[6],
                "user_id": u[0]
            }
            users.append(user_record)
        return jsonify(users), 200
        
    return "no users found", 404


@app_users.route('/users/get')
def get_all_active_users():
    cursor.execute ('''
        SELECT 
            u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active,
            o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type
        FROM users u
            JOIN organizations o
                ON u.org_id = o.org_id
        WHERE active='t';
    ''')
    
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

@app_users.route('/users/get/inactive', methods=['GET'])
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


@app_users.route('/users/populate', methods=['POST'])
def populate_mock_users():
    data = Faker()
    
    first_name = data.first_name()
    last_name = data.last_name()
    org_id = 3
    email = data.email()
    phone = data.phone_number()
    city = data.city()
    state = data.state()
    # active = data.get('active')
    
    cursor.execute("""
                    INSERT INTO users (first_name, last_name, org_id, email, phone, city, state)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,(first_name, last_name, org_id, email, phone, city, state))
    conn.commit()  
    return 'user added successfully', 201


@app_users.route('/users/get/<user_id>', methods=['GET'])
def get_user(user_id):
    cursor.execute('''
                   SELECT 
                        u.user_id, u.first_name, u.last_name, u.email, u.phone, u.city, u.state, u.org_id, u.active,
                        o.org_id, o.name, o.phone, o.city, o.state, o.active, o.type
                    FROM users u
                        JOIN organizations o
                            ON u.org_id = o.org_id
                    WHERE user_id=%s;
                   ''', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        return "User not found", 404
    
    user_dict = {
        "active": user[8],
        "city": user[5],
        "email": user[4],
        "first_name": user[1],
        "last_name": user[2],
        "organization": {
            "active": user[14],
            "city": user[12],
            "name": user[10],
            "org_id": user[9],
            "phone": user[11],
            "state": user[13],
            "type": user[15]
        },
        "phone": user[3],
        "state": user[6],
        "user_id": user[0]
    }
    return jsonify(user_dict), 200


@app_users.route('/users/update/<user_id>', methods=['POST'])
def update_user_by_id(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        return "User not found", 404
    
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
    
    update_query = "UPDATE users SET "
    update_values = []
    if first_name is not None:
        update_query += 'first_name=%s, '
        update_values.append(first_name)
    if last_name is not None:
        update_query += 'last_name=%s, '
        update_values.append(last_name)
    if email is not None:
        update_query += "email=%s, "
        update_values.append(email)
    if phone is not None:
        update_query += "phone=%s, "
        update_values.append(phone)
    if city is not None:
        update_query += "city=%s, "
        update_values.append(city)
    if state is not None:
        update_query += "state=%s, "
        update_values.append(state)
    if active is not None:
        update_query += "active=%s, "
        update_values.append(active)
    update_query = update_query[:-2] + " WHERE user_id=%s"
    update_values.append(user_id)
    
    cursor.execute(update_query, tuple(update_values))
    conn.commit()
    
    return "User updated successfully", 200


@app_users.route('/users/delete/<user_id>', methods=['DELETE'])
def user_delete(user_id):
    cursor.execute ("DELETE FROM users WHERE user_id=%s", (user_id,)) 
    conn.commit ( )
    return("User Deleted"), 200
        

@app_users.route('/users/active/<user_id>', methods=['POST'])
def toggle_active(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()

    if user:
        active = user[7]
        new_active = not active
        cursor.execute("UPDATE users SET active=%s WHERE user_id=%s", (new_active, user_id))
        conn.commit()
        return "user updated successfully", 200
    else:
        return "user not found", 404