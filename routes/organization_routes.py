import psycopg2
from flask import jsonify, request, Blueprint
from app import conn, cursor

orgs = Blueprint("orgs", __name__)


@orgs.route('/orgs')
def get_all_organizations():
    cursor.execute("SELECT name, phone, city, state, active, type, org_id FROM organizations ORDER BY org_id ASC")
    response = cursor.fetchall()
    
    if response:
        organizations = []
        for u in response:
            org_record = {
                "name": u[0],
                "phone": u[1],
                "city": u[2],
                "state": u[3],
                "active": u[4],
                "type": u[5],
                "org_id": u[6]
            }
            organizations.append(org_record)
        return jsonify(organizations), 200
    
    return "no organizations found", 404


@orgs.route('/orgs/<org_id>')
def get_org_by_id(org_id):
    cursor.execute("SELECT name, phone, city, state, active, type, org_id FROM organizations WHERE org_id=%s", (org_id,))
    org = cursor.fetchone()
    
    if not org:
        return "no organization found", 404
    
    organization = {
        "name": org[0],
        "phone": org[1],
        "city": org[2],
        "state": org[3],
        "active": org[4],
        "type": org[5],
        "org_id": org[6]
    }
    return jsonify(organization)
        


@orgs.route('/orgs/add', methods=['POST'])
def add_organization():
    data = request.get_json()
    
    name = data.get('name')
    phone = data.get('phone')
    if len(phone) > 20:
        return "Phone number cannot be longer than 20 characters", 400
    city = data.get('city')
    state = data.get('state')
    active = True
    if 'active' in data:
        active = data.get('active') != 'false'
    type = data.get('type')
    
    cursor.execute('''
                   INSERT INTO organizations (name, phone, city, state, active, type)
                   VALUES (%s, %s, %s, %s, %s, %s)
                   ''', (name, phone, city, state, active, type))
    conn.commit()
    return "Organization added", 201

@orgs.route('/orgs/update/<org_id>', methods=['POST'])
def update_organization(org_id):
    cursor.execute("SELECT name, phone, city, state, active, type FROM organizations WHERE org_id=%s", (org_id,))
    organization = cursor.fetchone()
    
    if not organization:
        return "Organization not found", 404
    
    data = request.get_json()
    org_id = data.get('org_id')
    name = data.get('name')
    phone = data.get('phone')
    city = data.get('city')
    state = data.get('state')
    active = data.get('active')
    type = data.get('type')
    
    if not org_id:
        return "org_id is required", 400
    
    update_query = "UPDATE organizations SET "
    update_values = []
    if name is not None:
        update_query += "name=%s, "
        update_values.append(name)
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
    if type is not None:
        update_query += "type=%s, "
        update_values.append(type)
    update_query = update_query[:-2] + " WHERE org_id=%s"
    update_values.append(org_id)
    
    cursor.execute(update_query, tuple(update_values))
    conn.commit()
    return "Organization updated successfully", 200

@orgs.route('/orgs/delete/<org_id>', methods=['DELETE'])
def delete_organization(org_id):
    cursor.execute("DELETE FROM organizations WHERE org_id=%s", (org_id,))
    conn.commit()
    return "organization deleted", 200

@orgs.route('/orgs/active/<org_id>', methods=['POST', 'PUT', 'PATCH'])
def toggle_active(org_id):
    cursor.execute('SELECT * FROM organizations WHERE org_id=%s', (org_id,))
    org = cursor.fetchone()
    
    if org:
        active = org[0]
        new_active = not active
        cursor.execute('UPDATE organizations SET active=%s WHERE org_id=%s', (new_active, org_id))
        conn.commit()
        return "organization updated successfully", 200
    else:
        return "organization not found", 404