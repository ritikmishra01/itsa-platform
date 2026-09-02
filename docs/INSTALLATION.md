# ITSA Platform: Installation & Setup Guide

## 1. System Requirements
- **Operating System**: Windows 10/11, macOS 12+, or Ubuntu 20.04+ Linux
- **Python**: Version 3.11, 3.12, or 3.13
- **Git**: Latest release
- **Memory**: Minimum 2 GB RAM (4 GB recommended)
- **Disk Space**: 500 MB free space

---

## 2. Installation Steps

### Step 1: Clone the Repository
```bash
git clone https://github.com/ritikmishra01/itsa-platform.git
cd itsa-platform
```

### Step 2: Set Up Python Virtual Environment

**Windows (CMD / PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the template configuration:
```bash
cp .env.example .env
```
*(On Windows CMD/PowerShell, use `copy .env.example .env`)*

Configure your `.env` settings:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secure-random-secret-key
PORT=5000
DATABASE_URL=sqlite:///itsa_platform.db
ADMIN_EMAIL=admin@itsa.edu
ADMIN_PASSWORD=Admin#2026
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 5: Seed Demo Data
Initialize the database with 5 faculty coordinators and 5 realistic college events:
```bash
python scripts/seed_demo_data.py
```

### Step 6: Start the Development Server
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```