# 🏋️ Gym Management System

A web-based Gym Management System built with Python, Flask, SQLite, HTML, CSS, and JavaScript. It helps gym staff manage members, memberships, attendance, workout plans, and fitness progress through a dashboard.

## ✨ Features

- **Member Management:** Register, view, update, and delete gym members.
- **Membership Management:** Manage monthly, quarterly, and yearly membership plans.
- **Attendance Tracking:** Record and view gym check-ins.
- **Workout Management:** Assign and manage workout plans for members.
- **Workout Progress Tracking:** Record completed workouts and monitor progress.
- **Analytics Dashboard:** View total members, membership revenue, active memberships, attendance statistics, and workout completion rates.
- **Responsive Dashboard:** Access gym statistics and member information through a web interface.

## 🛠️ Technologies Used

- **Backend:** Python, Flask
- **Database:** SQLite
- **Data Analysis:** Pandas
- **Frontend:** HTML, CSS, JavaScript
- **API Testing:** Postman
- **Version Control:** Git and GitHub

## 📁 Project Structure

```text
gym-management-system/
├── app.py
├── db.py
├── schema.sql
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── models/
├── routes/
├── services/
├── static/
├── templates/
├── data/
└── postman/
```

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Rupsa-Karmakar/gym-management-system.git
cd gym-management-system
```

### 2. Install dependencies

```bash
py -m pip install -r requirements.txt
```

### 3. Start the application

```bash
py app.py
```

The application initializes the database schema when the Flask app starts, provided its database configuration and schema file are set up correctly.

### 4. Open the dashboard

Visit:

http://127.0.0.1:5000/dashboard

## 🔌 API Endpoints

The application provides endpoints for members, memberships, attendance, workouts, workout progress, and analytics.

- **Health Check:** `GET /api/health`
- **Analytics Summary:** `GET /api/analytics/summary`

## 🔒 Security Notes

- Keep environment variables and credentials in `.env`.
- Never commit `.env`, private credentials, or sensitive database files to GitHub.
- Keep `.env.example` limited to placeholder values.
- Configure persistent database storage before deploying the application online.

## 📌 Project Status

The core API endpoints and dashboard have been implemented. Deployment and further improvements are in progress.

## 👩‍💻 Author

**Rupsa Karmakar**

GitHub: https://github.com/Rupsa-Karmakar
