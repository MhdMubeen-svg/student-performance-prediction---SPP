# Mubeen — Student Performance System

## 🚀 How to Run Locally

1. **Install Python** (3.8+) from https://python.org

2. **Open terminal** in the `mubeen_project` folder

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   python app.py
   ```

5. **Open browser** and go to:
   ```
   http://localhost:5000
   ```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main page |
| POST | `/api/login` | Sign in |
| POST | `/api/signup` | Create account |
| POST | `/api/logout` | Sign out |
| GET | `/api/me` | Get current user |
| GET | `/api/check-username?u=xxx` | Check username availability |
| GET | `/api/students` | Get all students |
| POST | `/api/students` | Add new student |
| DELETE | `/api/students/<id>` | Delete student |
| DELETE | `/api/students/clear` | Clear all students |

## 🗄️ Database

Uses SQLite (`mubeen.db`) — auto-created on first run. Two tables:
- `users` — accounts (username, email, hashed password)
- `students` — student records linked to users

## ⚠️ Fixing the "Cannot reach server" Error

This error shows when the browser cannot connect to Flask.
**Make sure `python app.py` is running** before opening the browser.
