# 🚀 Deployment & Setup Guide

Complete step-by-step setup instructions for the Privacy Query Interface.

## Pre-Flight Checklist

Before starting, ensure you have:
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Git installed (for cloning)
- [ ] 8GB+ RAM (for Ollama)
- [ ] 10GB+ free disk space (for models)
- [ ] Administrator access (for installations)

---

## Installation Guide (Windows, macOS, Linux)

### Step 1: Install Python & Git

#### Windows
```bash
# Download from python.org or use Windows Package Manager
winget install Python.Python.3.11
winget install Git.Git

# Verify installation
python --version
git --version
```

#### macOS
```bash
# Using Homebrew
brew install python git

# Verify
python3 --version
git --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Verify
python3 --version
git --version
```

### Step 2: Clone or Download Project

```bash
# Option A: Clone from Git
git clone https://github.com/your-repo/privacy-query-app.git
cd privacy-query-app

# Option B: Download as ZIP
# Extract the ZIP file and navigate to the directory
cd privacy-query-app
```

### Step 3: Setup Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment

# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Verify activation (you should see (venv) in your terminal)
```

### Step 4: Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify installation
pip list
```

Expected packages:
- Flask==2.3.0
- Flask-Login==0.6.2
- Flask-SQLAlchemy==3.0.5
- bcrypt==4.0.1
- spacy==3.5.0
- requests==2.31.0
- SQLAlchemy==2.0.19

### Step 5: Download SpaCy Model

```bash
# Download English language model (~40MB)
python -m spacy download en_core_web_sm

# Verify (should show the model details)
python -m spacy validate

# Test the download
python -c "import spacy; nlp=spacy.load('en_core_web_sm'); print('SpaCy ready!')"
```

### Step 6: Install and Run Ollama

#### Windows
1. Download from https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically
4. Verify in terminal:
```bash
ollama version
curl http://localhost:11434/api/tags
```

#### macOS
```bash
# Using Homebrew
brew install ollama

# Start Ollama
brew services start ollama

# Or run manually
ollama serve
```

#### Linux
```bash
# Download and install
curl https://ollama.ai/install.sh | sh

# Start service
sudo systemctl start ollama

# Or run manually
ollama serve
```

### Step 7: Download Llama 3 Model

**Important:** This downloads a ~4GB model. Ensure you have:
- Good internet connection (30+ minutes)
- 8GB+ free disk space
- 8GB+ system RAM

```bash
# Pull the Llama 3 model (in a separate terminal)
# This will take 10-30 minutes depending on connection

ollama pull llama3

# Test the model
ollama run llama3 "Hello, how are you?"

# List downloaded models
ollama list
```

**Expected output:**
```
NAME            ID              SIZE      MODIFIED
llama3          36298c087b2f    4.7GB     5 minutes ago
```

---

## Running the Application

### Terminal 1: Start Ollama Service

```bash
# Keep this terminal open
ollama serve
```

**Expected output:**
```
time=2024-04-02T10:00:00.000Z level=INFO msg="Listening on 127.0.0.1:11434"
```

### Terminal 2: Run Flask Application

```bash
# Make sure virtual environment is activated
# (venv) should appear at the start of your prompt

# Navigate to project directory
cd privacy-query-app

# Activate venv if not already
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Run the application
python app.py
```

**Expected output:**
```
╔════════════════════════════════════════════════════════════╗
║   Privacy-Preserving Query Interface                        ║
║   Starting Flask Application...                             ║
║                                                             ║
║   URL: http://localhost:5000                              ║
║                                                             ║
║   Make sure Ollama is running: ollama serve               ║
║   And Llama 3 model is installed: ollama run llama3       ║
╚════════════════════════════════════════════════════════════╝

 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
```

### Terminal 3: Test the API (Optional)

```bash
# Verify Ollama API is working
curl http://localhost:11434/api/tags

# Verify Flask app is running
curl http://localhost:5000/

# You should get a redirect to /login
```

---

## First Run Walkthrough

### 1. Open Browser

Navigate to: **http://localhost:5000**

You should see the login page with:
- Purple gradient background
- Shield icon (🛡️)
- "Privacy Query" title
- Login form

### 2. Create Account

1. Click **"Sign up here"** link
2. Fill in signup form:
   - Username: `testuser` (min 3 chars)
   - Password: `TestPass123` (min 6 chars)
   - Confirm: `TestPass123`
3. Click **"Create Account"**
4. Redirected back to login

### 3. Login

1. Enter your credentials
2. Click **"Login"**
3. Logged in! Now on dashboard

### 4. Try a Query

Try example query:
```
My name is John Smith, my email is john.smith@company.com, 
and I work at Google. What is machine learning?
```

Click **"Submit Query"**

You should see:
- Original Query (top section)
- Masked Query (with [NAME], [EMAIL], [ORG])
- Risk Score (circular gauge)
- Detected Entities (list of found PII)
- AI Response (from Llama 3)
- Final Response (unmasked version)

---

## Docker Deployment (Advanced)

If you want to run in Docker:

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download SpaCy model
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Create database
RUN python -c "from app import init_db; init_db()"

# Expose port
EXPOSE 5000

# Set environment
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run application
CMD ["python", "app.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434

  app:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - ollama
    environment:
      - OLLAMA_API_URL=http://ollama:11434
    volumes:
      - ./privacy_queries.db:/app/privacy_queries.db

volumes:
  ollama_data:
```

### Run with Docker Compose

```bash
docker-compose up --build

# Access at http://localhost:5000
```

---

## Production Deployment

### Changes for Production

Edit `app.py`:

```python
# BEFORE (debug/development)
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)

# AFTER (production)
if __name__ == '__main__':
    init_db()
    # Use gunicorn in production
    # gunicorn -w 4 -b 0.0.0.0:5000 app:app
    app.run(debug=False, port=5000)
```

### Install Gunicorn

```bash
pip install gunicorn
```

### Change Secret Key

```python
# In app.py, change:
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# To a secure random string:
app.config['SECRET_KEY'] = 'generate-secure-key-with-secrets-module'
```

### Run with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### SSL/HTTPS

For production HTTPS, use reverse proxy (nginx):

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring & Logging

### Enable Debug Logging

Edit `app.py` to add logging:

```python
import logging

# Add logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add to routes
@app.route('/api/query', methods=['POST'])
@login_required
def api_query():
    logger.info(f"Query submitted by user {current_user.id}")
    # ... rest of code
```

### Database Backup

```bash
# Backup database
cp privacy_queries.db privacy_queries.db.backup

# Restore from backup
cp privacy_queries.db.backup privacy_queries.db
```

### Check Database

```bash
python -c "
from app import db, User, Query, app
with app.app_context():
    users = User.query.all()
    queries = Query.query.all()
    print(f'Users: {len(users)}')
    print(f'Queries: {len(queries)}')
"
```

---

## Troubleshooting Guide

### Issue: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Make sure venv is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: No module named '_sqlite3'

**Solution (macOS):**
```bash
brew install sqlite3
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Ollama timeout

```
Error calling Ollama API: Ollama API request timed out
```

**Solutions:**
1. Check Ollama is running: `ollama serve` in separate terminal
2. First request takes longer: Wait 30-60 seconds
3. Increase timeout in `app.py`:
```python
def call_ollama_api(masked_query: str, timeout: int = 120) -> tuple[bool, str]:
    # Changed timeout to 120 seconds
```

### Issue: Port already in use

```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5000
kill -9 <PID>

# Or use different port:
python app.py --port 5001
```

### Issue: Slow Ollama responses

**Solutions:**
1. First request loads model (2-3 minutes) - this is normal
2. Ensure 8GB+ RAM available
3. Close other applications
4. Check internet connection for slow model loading
5. Consider using a smaller model:
```bash
ollama pull mistral
# Then edit app.py: model = "mistral"
```

### Issue: Database errors

**Solution:**
```bash
# Reset database
rm privacy_queries.db

# Restart app - database will be recreated
python app.py
```

---

## Performance Tuning

### Increase Ollama RAM allocation

Edit Ollama config:

```bash
# macOS
defaults write com.ollama OllamaMemory 8  # 8GB

# Linux - edit /etc/systemd/system/ollama.service:
[Service]
Environment="OLLAMA_NUM_GPU=1"
```

### Optimize Flask for production

```python
# In app.py
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_SORT_KEYS'] = False
```

### Database indexing

```python
# In auth.py, add to User model:
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Index for faster queries
    __table_args__ = (
        db.Index('idx_username', 'username'),
    )
```

---

## Health Check

Create `health_check.py`:

```python
import requests
import time

def check_health():
    checks = {
        'flask': False,
        'ollama': False,
        'database': False
    }
    
    # Check Flask
    try:
        resp = requests.get('http://localhost:5000/', timeout=5)
        checks['flask'] = resp.status_code in [200, 302]
    except:
        pass
    
    # Check Ollama
    try:
        resp = requests.get('http://localhost:11434/api/tags', timeout=5)
        checks['ollama'] = resp.status_code == 200
    except:
        pass
    
    # Check Database
    try:
        from app import db, User, app
        with app.app_context():
            User.query.first()
            checks['database'] = True
    except:
        pass
    
    print("\nHealth Check Results:")
    for service, status in checks.items():
        print(f"  {service}: {'✓ OK' if status else '✗ FAIL'}")
    
    return all(checks.values())

if __name__ == '__main__':
    check_health()
```

Run with:
```bash
python health_check.py
```

---

## Next Steps

1. **Try some test queries** (see README.md for examples)
2. **Explore the code** - read comments in each file
3. **Customize** - adjust weights, add more PII types
4. **Deploy** - follow production deployment section
5. **Share** - showcase in portfolio/interviews

---

## Support

For issues:
1. Check Troubleshooting section above
2. Review README.md FAQ
3. Check Flask/Ollama logs for detailed errors
4. Verify all services are running (Flask + Ollama)

---

**Happy deploying! 🚀**
