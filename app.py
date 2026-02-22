from flask import Flask
from db import db
from config.config import Config
from models.models import Admin, Company, Student, PlacementDrive, Application, Role, Approvalstatus,Drivestatus
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

def create_db(admin_email='admin@college.local', admin_password='admin123'):
    
    # create all tables
    db.create_all()
    print("Database tables created successfully.")

    # create default admin if not exists
    existing = Admin.query.filter_by(email=admin_email).first()
    if existing:
        print('Admin already exists:', existing.email)
        return existing

    admin = Admin(
        name='Default Admin',
        email=admin_email,
        phone='1234567890'
    )

    admin.set_password(admin_password)
    db.session.add(admin)
    db.session.commit()

    print('Created default admin:', admin.email)
    return admin





if __name__ == "__main__":
    with app.app_context():
        create_db()

    app.run(debug=True)