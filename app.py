import psycopg2

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

conn = psycopg2.connect("dbname='theultdatabase' user='matt' host='localhost'")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR,
    org_id SERIAL,
    phone VARCHAR,
    email VARCHAR NOT NULL UNIQUE,
    city VARCHAR,
    state VARCHAR,
    active BOOLEAN NOT NULL DEFAULT True
);
''')
conn.commit()

cursor.execute("""
               CREATE TABLE IF NOT EXISTS organizations (
                   org_id SERIAL PRIMARY KEY,
                   name VARCHAR NOT NULL,
                   phone VARCHAR,
                   city VARCHAR,
                   state VARCHAR,
                   active BOOLEAN NOT NULL DEFAULT True,
                   type VARCHAR
               );
               """)
conn.commit()

if __name__ == "__main__":
    from routes import app_users, orgs
    app.register_blueprint(app_users)
    app.register_blueprint(orgs)
    app.run(host='0.0.0.0', port=8086)