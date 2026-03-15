# 🎓 Placement Portal Application (PPA)

A web-based **Placement Portal Application (PPA)** built using **Flask and SQLAlchemy** to manage student placements in a college.
The system enables **students, companies, and administrators** to interact through role-based dashboards for managing placement drives and applications.

---

# 🚀 Project Milestone

**Milestone: PPA Admin Dashboard Management**

This milestone implements the **Admin Dashboard**, allowing administrators to efficiently manage students, companies, and placement drives.

---

# ✨ Features

## 🔐 Authentication System

* Secure login for **Admin, Students, and Companies**
* Password hashing using `Werkzeug`
* Role-based session management

---

## 🎓 Student Module

Students can:

* Register on the portal
* Log in to their dashboard
* View placement drives
* Apply for jobs
* Upload resume
* Track application status

---

## 🏢 Company Module

Companies can:

* Register on the portal
* Wait for admin approval
* Log in after approval
* Post placement drives
* Manage job applications

---

## 👨‍💼 Admin Module

The Admin dashboard provides full control of the system.

### 🏢 Company Management

* Approve registered companies
* Reject company registrations
* Blacklist companies
* View all companies

### 🎓 Student Management

* View all registered students
* Blacklist / unblacklist students

### 📅 Placement Drive Management

* View ongoing placement drives
* Approve company drives

### 📊 Application Monitoring

* View recent student applications

### 📈 Dashboard Statistics

Admin dashboard displays:

* Total Students
* Total Companies
* Total Placement Drives
* Total Applications

---

# 🛠 Tech Stack

**Backend**

* Python
* Flask

**Database**

* SQLite
* SQLAlchemy ORM

**Frontend**

* HTML
* Jinja2 Templates
* CSS

**Security**

* Werkzeug Password Hashing
* Flask Sessions

---

# 📁 Project Structure

```
my-first-repo/
│
├── app.py
├── db.py
├── config/
│   └── config.py
│
├── models/
│   └── models.py
│
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── StudentRegister.html
│   ├── CompanyRegister.html
│   ├── AdminDashboard.html
│   ├── StudentDashboard.html
│   └── CompanyDashboard.html
│
├── static/
│
└── venv/
```

---

# 🗄 Database Models

Main database entities include:

* **Admin**
* **Student**
* **Company**
* **PlacementDrive**
* **Application**

Relationships:

* Companies create placement drives
* Students apply for placement drives
* Applications link students and drives

---

# ⚙️ Setup Instructions

## 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/my-first-repo.git
cd my-first-repo
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```
pip install flask
pip install flask_sqlalchemy
```

---

## 4️⃣ Run the Application

```
python app.py
```

Server will start at:

```
http://127.0.0.1:5000
```

---

# 🔑 Default Admin Login

Admin account is automatically created when the application starts.

Email:

```
admin@college.local
```

Password:

```
admin123
```

---

# 🔮 Future Improvements

Possible enhancements:

* Resume upload system
* Email notifications for placement updates
* Advanced filtering and search
* Placement statistics visualization
* REST API integration
* Deployment using Docker or Cloud platforms

---

# 👩‍💻 Author

**Anisha Bhargava**

Developed as part of the **Placement Portal Application (PPA)** project.

---

# 📜 License

This project is intended for **educational and academic purposes**.
