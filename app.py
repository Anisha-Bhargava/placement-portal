from datetime import datetime
from flask import Flask,request,session,redirect,url_for,render_template
from db import db
from config.config import Config
from models.models import Admin, Company, Student, PlacementDrive, Application, Role, Approvalstatus,Drivestatus,Applicationstatus
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
from flask import abort
import os

app = Flask(__name__)
os.makedirs(app.instance_path, exist_ok=True)
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
        data = request.form
        student = Student(
            name=data["name"],
            email=data["email"],
            roll_number=data["roll_number"],
            course=data["course"],
            phone=data.get("phone"),
            skills=data.get("skills")
        )
        student.set_password(data["password"])
        file = request.files.get("resume")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join("static/resumes", filename)
            os.makedirs("static/resumes", exist_ok=True)
            file.save(filepath)
            student.resume_path = f"resumes/{filename}"

        db.session.add(student)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("student_register.html", form_title="Student Registration", form_action="/register/student", student=None)

#Profile Editing
@app.route("/student/profiles/<int:id>", methods=["GET", "POST"])
@role_required(Role.STUDENT)
def student_profile(id):
    student = Student.query.get_or_404(id)

    if request.method == "POST":   
        data = request.form
        student.name = data["name"]
        student.email = data["email"]
        student.phone = data.get("phone")
        student.roll_number = data["roll_number"]
        student.course = data["course"]
        student.skills = data.get("skills")

        file = request.files.get("resume")
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            filepath = os.path.join("static/resumes", filename)
            os.makedirs("static/resumes", exist_ok=True)
            file.save(filepath)
            student.resume_path = f"resumes/{filename}"
        db.session.commit()
        return redirect("/dashboard/student")
    return render_template("StudentRegister.html", form_title="Edit Profile", form_action=f"/student/profiles/{id}", student=student)


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
            approval_status=Approvalstatus.PENDING
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

         # user.role.value == company then check approved or not if not approved show error message else redirect to dashboard
        company= Company.query.filter_by(email=email).first()
        if company and company.check_password(password):
            if not company.is_approved():
                return render_template("login.html", error="Company not approved yet")
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

@app.route("/search") 
def search():
    query = request.args.get('q', '')
    #Admin role search
    if session.get('user_role') == "admin":
        if not query:
            return render_template(
                "admin/search_results.html",
                students=[],
                companies=[],
                query=query
            )

        students = Student.query.filter(
            (Student.name.ilike(f'%{query}%')) |
            (Student.email.ilike(f'%{query}%')) |
            (Student.phone.ilike(f'%{query}%'))
        ).all()

        companies = Company.query.filter(
                (Company.company_name.ilike(f'%{query}%')) |
                (Company.email.ilike(f'%{query}%')) |
                (Company.phone.ilike(f'%{query}%')) |
                (Company.website.ilike(f'%{query}%')) |
                (Company.hr_contact.ilike(f'%{query}%'))
            ).all()

        return render_template(
            "admin/search_results.html",
            students=students,
            companies=companies,
            query=query
        )
    
    # Student role search
    elif session['user_role'] == "student":
        if not query:
            # If query is empty, return all approved drives
            drives = PlacementDrive.query.filter(
                PlacementDrive.approval_status == Approvalstatus.APPROVED,
                PlacementDrive.status != Drivestatus.COMPLETED
            ).all()
        else:
            # Search by job title, company name, or description
            drives = PlacementDrive.query.filter(
                PlacementDrive.approval_status == Approvalstatus.APPROVED,
                PlacementDrive.status != Drivestatus.COMPLETED,
                (PlacementDrive.job_title.ilike(f"%{query}%")) |
                (PlacementDrive.company_id.ilike(f"%{query}%")) |
                (PlacementDrive.job_description.ilike(f"%{query}%"))
            ).all()
        return render_template("student/searchJobs.html",drives=drives,query=query)
    
    
# Student Dashboard
@app.route("/dashboard/student")
@role_required(Role.STUDENT)
def student_dashboard():
    student = Student.query.get(session['user_id'])

    drives = PlacementDrive.query.filter(
        PlacementDrive.approval_status == Approvalstatus.APPROVED,
        PlacementDrive.status != Drivestatus.COMPLETED
    ).all()
    
    company = Company.query.all()
    applied_applications = Application.query.filter_by(student_id=student.id).all()
    total_applied = len(applied_applications)

    notification = [app for app in applied_applications if app.status != Applicationstatus.APPLIED]

    return render_template(
        "StudentDashboard.html",
        student=student,
        company=company,
        drives=drives,
        applications= applied_applications,
        total_applied=total_applied,
        notifications=notification,
        ApplicationStatus=Applicationstatus
    )
    

# Company Dashboard
@app.route("/dashboard/company")
@role_required(Role.COMPANY)
def company_dashboard():
    company = Company.query.get(session['user_id'])
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    total_drives = len(drives)
    total_applications = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id
    ).count()
    
    return render_template(
        "CompanyDashboard.html",
        company=company,
        drives=drives,
        total_drives=total_drives,
        total_applications=total_applications,
        Drivestatus=Drivestatus   #imp
    )

@app.route("/company/drive/create", methods=["GET", "POST"])
@role_required(Role.COMPANY)
def create_drive():
    if request.method == "POST":
        data = request.form
        company_id = session['user_id']
        company = Company.query.get_or_404(company_id)
        if company.approval_status != Approvalstatus.APPROVED:
            return "Your company is not approved yet. Cannot create drive.", 403
        drive = PlacementDrive(
            company_id=company_id,
            job_title=data['job_title'],
            job_description=data['job_description'],
            eligibility_criteria=data['eligibility_criteria'],
            application_deadline=datetime.strptime( request.form.get('application_deadline'), "%Y-%m-%dT%H:%M"),
            salary_range=data['salary_range'],
            required_skills=data['required_skills'],
            experience_required=data['experience_required'],
            status=Drivestatus.UPCOMING,
            approval_status=Approvalstatus.PENDING
        )
        db.session.add(drive)
        db.session.commit()
        return redirect(url_for('company_dashboard'))
    return render_template("CreateDrive.html")


@app.route("/company/drive/<int:id>/toggle-status")
@role_required(Role.COMPANY)
def toggle_drive_status(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != session['user_id']:
        return "Unauthorized", 403
    if drive.status == Drivestatus.UPCOMING:
        drive.status = Drivestatus.ONGOING
    elif drive.status == Drivestatus.ONGOING:
        drive.status = Drivestatus.COMPLETED
    db.session.commit()
    return redirect(url_for('company_dashboard'))

#reviewing student's application
@app.route("/company/drive/<int:id>/applications")
@role_required(Role.COMPANY)
def view_applications(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != session['user_id']:
        return "Unauthorized", 403
    applications = drive.applications
    return render_template("ViewApplication.html",drive=drive,applications=applications,ApplicationStatus=Applicationstatus)
    


@app.route("/company/application/<int:id>/update", methods=["POST"])
@role_required(Role.COMPANY)
def update_application_status(id):
    
    application = Application.query.get_or_404(id)
    if application.drive.company_id != session['user_id']:
        abort(403)
    status = request.form.get("status")
    if status == "Shortlisted":
        application.status = Applicationstatus.SHORTLISTED
    elif status == "Accepted":
        application.status = Applicationstatus.ACCEPTED
    elif status == "Rejected":
        application.status = Applicationstatus.REJECTED
    else:
        abort(400)
    db.session.commit()
    return redirect(url_for("view_applications", id=application.drive_id))


@app.route("/admin/drive/<int:id>/approve")
@role_required(Role.ADMIN)
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = Drivestatus.UPCOMING
    drive.approval_status = Approvalstatus.APPROVED
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route("/student/apply/<int:drive_id>")
def apply_drive(drive_id):
    student_id = session['user_id']
    # drive_id = request.view_args['drive_id']
    drive=PlacementDrive.query.get_or_404(drive_id)

    if drive.approval_status != Approvalstatus.APPROVED or drive.status == Drivestatus.COMPLETED:
        return "This drive is not open for applications.", 400

    existing_application = Application.query.filter_by(student_id=student_id, drive_id=drive_id).first()
    if existing_application:
        return "You have already applied for this drive.", 400

    application = Application(student_id=student_id, drive_id=drive_id)
    db.session.add(application)
    db.session.commit()
    return redirect(url_for('student_dashboard')) 


# Application starts from here

if __name__ == "__main__":
    with app.app_context():
        create_db()
        seed_data()

    app.run(debug=True)