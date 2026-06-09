# Sports Day & Finance Management Dashboard System
## ระบบแดชบอร์ดจัดการการเงินและกิจกรรมกีฬาสี

This project is a Full-Stack Web Application for managing color sports day event finances, sports, athletes/staff, and match results.

### Features
1. **Public Dashboard (`index.html`)**: Interactive financial widgets (Donut Chart & Bar Chart via Chart.js), latest sports results, and athlete rosters.
2. **Admin Panel (`admin.html`)**: Secure panel to record transactions, register participants, and post match results (with JWT Authentication).

---

### Tech Stack
- **Backend**: Python 3.12+ / FastAPI / SQLAlchemy / PyMySQL
- **Database**: MySQL
- **Frontend**: HTML5 / Tailwind CSS (CDN) / Chart.js (CDN) / Vanilla JS

---

### Setup Instructions

#### 1. Database Setup
1. Start your MySQL Server (e.g. via XAMPP, Docker, or native installer).
2. Create a new database named `sport_color_db`:
   ```sql
   CREATE DATABASE sport_color_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. (Optional) You can run the `schema.sql` file in your MySQL environment to manually create the tables, though the FastAPI server will automatically generate them on startup if they don't exist.

#### 2. Backend Setup
1. Open terminal inside the project root directory.
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file by copying `.env.example`:
   ```bash
   copy .env.example .env
   ```
5. Edit `.env` to configure your MySQL connection:
   - `DB_HOST`: default `localhost`
   - `DB_PORT`: default `3306`
   - `DB_USER`: default `root`
   - `DB_PASSWORD`: your MySQL password (empty by default in XAMPP)
   - `DB_NAME`: default `sport_color_db`

#### 3. Running the Backend Server
Run the FastAPI application via Uvicorn:
```bash
python -m uvicorn backend.app.main:app --reload
```
The backend will run on `http://127.0.0.1:8000`.

*Note: On first startup, the database tables will be generated automatically and a default administrator account will be created:*
- **Username**: `admin`
- **Password**: `Prtc2026`

#### 4. Frontend Usage
Since the frontend communicates with the FastAPI API via AJAX fetches (with CORS enabled), you can open the frontend files directly in your web browser:
1. Double-click `frontend/index.html` to view the public dashboard.
2. Go to `frontend/login.html` (or click "Admin Login" from index.html) and log in using the credentials above.
3. Once logged in, you will be redirected to `frontend/admin.html` where you can input data.
