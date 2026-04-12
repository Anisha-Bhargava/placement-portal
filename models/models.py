from db import db
from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash

#Enum

class Role(Enum):
    STUDENT = 'student'
    COMPANY = 'company'
    ADMIN = 'admin'

class Approvalstatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    BLACKLISTED = 'blacklisted'

class Drivestatus(Enum):
    UPCOMING = 'upcoming'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'

class Applicationstatus(Enum):
    APPLIED = 'applied'
    SHORTLISTED = 'shortlisted'
    REJECTED = 'rejected'
    ACCEPTED = 'accepted'
    INTERVIEW = 'interview'
    PLACED = 'placed'

class Usercommon(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column("password",db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):   
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)
    
class Admin(Usercommon):
    __tablename__ = 'admins'

    role = db.Column(db.Enum(Role), default=Role.ADMIN, nullable=False)

    def __repr__(self):
        return f"<Admin {self.name} ({self.email})>"
    
class Company(Usercommon):
    __tablename__ = 'companies'
    
    role = db.Column(db.Enum(Role), default=Role.COMPANY, nullable=False)
    company_name = db.Column(db.String(150), unique=True,nullable=False)
    hr_contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    approval_status = db.Column(db.Enum(Approvalstatus), default=Approvalstatus.PENDING, nullable=False)
    drives = db.relationship('PlacementDrive', backref='company', lazy=True,cascade="all, delete-orphan")
    def is_approved(self):
        return self.approval_status == Approvalstatus.APPROVED

    def __repr__(self):
        return f"<Company {self.name} ({self.email}) - {self.approval_status.value}>"  
    

class Student(Usercommon):
    __tablename__ = 'students'
    
    role = db.Column(db.Enum(Role), default=Role.STUDENT, nullable=False)

    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(200), nullable=True)
    resume_path = db.Column(db.String(200), nullable=True)

    blacklist = db.Column(db.Boolean, default=False, nullable=False)

    department = db.Column(db.String(50), nullable=False)
    year_of_study = db.Column(db.Integer, nullable=False)

    applications = db.relationship('Application', backref='student', lazy=True,cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.name} ({self.email}) - Roll: {self.roll_number}>"
    

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.String(200), nullable=True)
    application_deadline = db.Column(db.DateTime, nullable=False)
    salary_range = db.Column(db.String(100), nullable=True)
    required_skills = db.Column(db.String(200), nullable=True)
    experience_required = db.Column(db.String(100), nullable=True)

    status = db.Column(db.Enum(Drivestatus), default=Drivestatus.UPCOMING, nullable=False)
    approval_status = db.Column(db.Enum(Approvalstatus), default=Approvalstatus.PENDING, nullable=False)

    applications = db.relationship('Application', backref='drive', lazy=True, cascade="all, delete-orphan")

    approval_status = db.Column(db.Enum(Approvalstatus), default=Approvalstatus.PENDING)
    def __repr__(self):
        return f"<PlacementDrive {self.job_title} - {self.status}>"
    


class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id', ondelete='CASCADE'), nullable=False)

    status = db.Column(db.Enum(Applicationstatus), default=Applicationstatus.APPLIED, nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    remarks = db.Column(db.String(200), nullable=True)


#student will not be able to apply twice in the same drive
    __table_args__= (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),        )


    def __repr__(self):
        return f"<Application {self.student.name} for {self.drive.job_title} at {self.drive.company.company_name} - {self.status}>"
    


class Placement(db.Model):
    __tablename__ = 'placements'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id', ondelete='CASCADE'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)

    offer_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    joining_date = db.Column(db.DateTime, nullable=True)
    package_lpa = db.Column(db.String(200), nullable=True)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# relationship enabling
    application = db.relationship('Application', backref=db.backref('placement', uselist=False), lazy=True)
    def __repr__(self):
        return f"<Placement {self.student.name} at {self.drive.company.company_name} - Package: {self.package_lpa}>"
    





