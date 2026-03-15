from flask import Flask,request,session,redirect,url_for,render_template
from db import db
from config.config import Config
from models.models import Admin, Company, Student, PlacementDrive, Application, Role, Approvalstatus,Drivestatus
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app) #sql and flask ko integrate karke start kara h

def create_db(admin_email='admin@college.local', admin_password='admin123'):
    
    # creating all tables
    db.create_all()
    print("Database tables created.")

    # creating default admin if it is not there or exists
    existing = Admin.query.filter_by(email=admin_email).first()
    if existing:
        print('Admin already exists:', existing.email)
        return existing

    admin = Admin(
        name='Admin_1',
        email=admin_email,
        phone='2342341234'
    )

    admin.set_password(admin_password)
    db.session.add(admin)
    db.session.commit()

    print('Created default admin:', admin.email)
    return admin

def seed_data():
    # Check if data is already present
    if Student.query.first() or Company.query.first():
        print("Data is already present.")
        return

    student1 = Student(
        name="Ram Chandra",
        phone="9453451234",
        email="ram@college.local",
        roll_number="1001",
        course="Computer Science",
        skills="Python,Java",
        department="CSE",
        year_of_study=3,
        resume_path="/resumes/ram_chandra.pdf"
    )

    student2 = Student(
        name="Arjun Bhatt",
        phone="9878987896",
        email="arjun@college.local",
        roll_number="1002",
        course="Electrical Engineering",
        skills="C++,C",
        department="EEE",
        year_of_study=2,
        resume_path="/resumes/arjun_bhatt.pdf"
    )

    # Sample companies
    company1 = Company(
        name="Vdesi",
        email="vdesi@company.local",
        company_name="Vdesi Tour & Travels",
        hr_contact="HR Manager",
        website="https://vdesi.com",
        approval_status=Approvalstatus.APPROVED
    )

    company2 = Company(
        name="Hetzz",
        email="hetzz@company.local",
        company_name="Hetzz Fashion",
        hr_contact="HR Director",
        website="https://hetzz.com",
        approval_status=Approvalstatus.PENDING
    )

    # Set passwords
    student1.set_password("student123")
    student2.set_password("student456")
    company1.set_password("company123")
    company2.set_password("company456")

    db.session.add_all([student1, student2, company1, company2])
    db.session.commit()

    print("Sample data seeded successfully.")










def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session or 'user_role' not in session:
                return redirect(url_for('login'))
            if session['user_role'] != required_role.value:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# Home route
@app.route("/")
def home():
    return render_template("home.html")



#Student Registeration

@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        data=request.form

        if Student.query.filter_by(email=data['email']).first():
            return "Email already registered. Please use a different email.", 400
        
        #Create student
        student = Student(
            name=data['name'],
            email=data['email'],
            roll_number=data['roll_number'],
            course=data['course'],
            skills=data['skills']
        )
        
        student.set_password(data['password'])
        
        db.session.add(student)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("StudentRegister.html")

        

#Company Registeration


@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        data=request.form

        if Company.query.filter_by(email=data['email']).first():
            return "Email already registered. Please use a different email.", 400
        
        #Create company
        company = Company(
            name=data['name'],
            email=data['email'],
            company_name=data['company_name'],
            hr_contact=data['hr_contact'],
            website=data['website'],
            approval_status=Approvalstatus.APPROVED
        )
        
        company.set_password(data['password'])
        
        db.session.add(company)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("CompanyRegister.html",error="error", success="success")


# login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data=request.form
        email=data['email']
        password=data['password']

        # check in students,company,admin
        user = (Student.query.filter_by(email=email).first()
                or Company.query.filter_by(email=email).first()
                or Admin.query.filter_by(email=email).first())
        
        if not user or not user.check_password(password):
            return render_template("login.html", error="Invalid email or password")
        
        if isinstance(user, Company) and user.approval_status != Approvalstatus.APPROVED:
            return render_template("login.html", error="Company not approved yet")

       
        session['user_id'] = user.id
        session['user_role'] = user.role.value

        return redirect(f"/dashboard/{user.role.value}")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# Admin Dashboard
@app.route("/dashboard/admin")
@role_required(Role.ADMIN)
def admin_dashboard():
    
    total_students = Student.query.count()
    total_companies = Company.query.count()
    total_placementdrives = PlacementDrive.query.count()
    total_applications = Application.query.count()   
    
    
    
    pending_companies = Company.query.filter_by(approval_status=Approvalstatus.PENDING).all()
    
    all_companies = Company.query.all()
    all_students = Student.query.all()
    ongoing_drives = PlacementDrive.query.filter(PlacementDrive.application_deadline >= db.func.current_date()).all()

    recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(10).all()


    return render_template("AdminDashboard.html", pending_companies=pending_companies,
                            all_companies=all_companies, 
                            all_students=all_students, 
                            ongoing_drives=ongoing_drives, 
                            recent_applications=recent_applications,
                            total_students=total_students, 
                           total_companies=total_companies, 
                           total_drives=total_placementdrives, 
                           total_applications=total_applications,
                           admin_name=session['user_id'])
    
    
@app.route("/admin/company/<int:id>/approve")
@role_required(Role.ADMIN)
def approve_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = Approvalstatus.APPROVED
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route("/admin/company/<int:id>/reject")
@role_required(Role.ADMIN)
def reject_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = Approvalstatus.REJECTED
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/company/<int:id>/blacklist")
@role_required(Role.ADMIN)
def blacklist_company(id):
    company = Company.query.get_or_404(id)
    company.approval_status = Approvalstatus.BLACKLISTED

    for drive in company.drives:
        drive.status = Drivestatus.COMPLETED
        
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/student/<int:id>/toggle-blacklist", methods=["POST"])
@role_required(Role.ADMIN)
def toggle_blacklist(id):
    student= Student.query.get_or_404(id)
    student.blacklist = not student.blacklist
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/search")
@role_required(Role.ADMIN)  
def admin_search():
    query = request.args.get('q', '') 
    # search students and companies by name or email
    student = Student.query.filter(
    (Student.name.ilike(f'%{query}%')) |
    (Student.email.ilike(f'%{query}%')) |
    (Student.phone.ilike(f'%{query}%'))).all()

    company = Company.query.filter(
    (Company.name.ilike(f'%{query}%')) |
    (Company.email.ilike(f'%{query}%'))).all()
    return render_template("admin/search_results.html", students=student, companies=company, query=query)





    
# Student Dashboard
@app.route("/dashboard/student")
@role_required(Role.STUDENT)
def student_dashboard():
    return render_template("StudentDashboard.html")

# Company Dashboard
@app.route("/dashboard/company")
@role_required(Role.COMPANY)
def company_dashboard():
    return render_template("CompanyDashboard.html")

# Admin approval

# @app.route("/admin/approve/<int:company_id>")
# @role_required(Role.ADMIN)
# def approve_company(company_id):
#     company = Company.query.get_or_404(company_id)
#     company.approval_status = Approvalstatus.APPROVED
#     db.session.commit()

#     return redirect(url_for('AdminDashboard'))


@app.route("/admin/drive/<int:id>/approve")
@role_required(Role.ADMIN)
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = Drivestatus.UPCOMING
    drive.approval_status = Approvalstatus.APPROVED
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


# Application starts from here

if __name__ == "__main__":
    with app.app_context():
        create_db()
        seed_data()
    app.run(debug=True)