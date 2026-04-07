# 🛡️ Privacy-Preserving Query Interface

A production-quality, full-stack web application that detects and masks Personally Identifiable Information (PII) before sending queries to AI models. Built with Flask, SpaCy, and Ollama for secure, privacy-respecting AI interactions.

## 🎯 Overview

This system acts as a **privacy layer between users and AI models**, preventing sensitive data leakage while maintaining query functionality. Key features:

- ✅ **Automatic PII Detection** - SpaCy NER + Regex pattern matching
- ✅ **Intelligent Masking** - All sensitive data replaced before AI processing
- ✅ **Risk Scoring** - Weighted calculation of privacy risk
- ✅ **Response Unmasking** - Original values restored in AI responses
- ✅ **User Authentication** - Secure signup/login with bcrypt
- ✅ **Query History** - Track all interactions with risk scores
- ✅ **Modern UI/UX** - Bootstrap interface with dark mode support
- ✅ **Ollama Integration** - Local Llama 3 AI processing

## 🏗️ Tech Stack

### Backend
- **Python 3.9+**
- **Flask 2.3** - Web framework
- **Flask-Login** - Session management
- **Flask-SQLAlchemy** - ORM
- **bcrypt** - Password hashing
- **SQLite** - Database

### NLP & Detection
- **SpaCy 3.5** - Named Entity Recognition (NER)
- **Regex** - Pattern matching for structured data

### Frontend
- **HTML5** - Semantic markup
- **Bootstrap 5** - Responsive UI framework
- **CSS3** - Modern styling with dark mode
- **Vanilla JavaScript** - Client-side interactivity

### AI Integration
- **Ollama** - Local LLM serving
- **Llama 3** - Language model

## 📁 Project Structure

```
privacy-query-app/
├── app.py                 # Main Flask application
├── auth.py                # Authentication & database models
├── pii_detector.py        # Regex-based PII detection
├── nlp_detector.py        # SpaCy-based NER
├── requirements.txt       # Python dependencies
├── privacy_queries.db     # SQLite database (auto-created)
├── templates/
│   ├── login.html         # Login form
│   ├── signup.html        # Registration form
│   └── dashboard.html     # Main application interface
└── static/
    ├── styles.css         # CSS styling
    └── script.js          # JavaScript functionality
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Ollama installed and running (https://ollama.ai)
- Llama 3 model (~4GB)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd privacy-query-app

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Download SpaCy Model

```bash
python -m spacy download en_core_web_sm
```

This downloads the English NLP model (~40MB) for named entity recognition.

### Step 3: Setup & Run Ollama

```bash
# Start Ollama service (in a separate terminal)
ollama serve

# In another terminal, download Llama 3 model
ollama pull llama3
```

**On Windows:** Download Ollama from https://ollama.ai, install, and run from the Start menu.

**Verify Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

### Step 4: Run Flask Application

```bash
# From the project directory with venv activated
python app.py
```

You should see:
```
╔════════════════════════════════════════════════════════════╗
║   Privacy-Preserving Query Interface                        ║
║   Starting Flask Application...                             ║
║                                                             ║
║   URL: http://localhost:5000                              ║
║   Default Login: test / test1234 (after first signup)      ║
║                                                             ║
║   Make sure Ollama is running:                             ║
║   ollama serve                                             ║
║                                                             ║
║   And Llama 3 model is installed:                          ║
║   ollama run llama3                                        ║
╚════════════════════════════════════════════════════════════╝
```

### Step 5: Access Application

Open your browser and navigate to: **http://localhost:5000**

## 📝 Usage Guide

### First Time Setup

1. **Create Account**
   - Click "Sign up here" on the login page
   - Enter username (min. 3 characters) and password (min. 6 characters)
   - Password is hashed with bcrypt before storage

2. **Login**
   - Use your credentials to login
   - Session managed securely with Flask-Login

### Submit a Query

1. Enter your query in the text area
   - Can include personal information without worry
   - Example: "My name is John Doe, born 01/15/1995, email john@example.com. What is AI?"

2. Click **"Submit Query"**
   - System automatically detects PII
   - Calculates privacy risk score
   - Masks sensitive data
   - Sends masked version to Llama 3 via Ollama

3. View Results
   - **Original Query**: Your input (reference only)
   - **Masked Query**: What was sent to AI models
   - **Risk Score**: Privacy risk calculation (0-100)
   - **Detected Entities**: What was found and masked
   - **AI Response**: Response from Llama 3
   - **Final Response**: Same as AI response with PII restored (if any)

### Query History

- Click **"Query History"** in sidebar
- View all past queries with timestamps
- Click **"View"** to see full query details
- Risk scores color-coded (Green/Yellow/Red)

### How It Works

Click **"How It Works"** in sidebar for:
- Step-by-step process explanation
- Risk score calculation details
- Why privacy matters
- Data types detected

## 🔍 PII Detection Details

### SpaCy Named Entity Recognition (NER)

Detects person names, organizations, locations using pre-trained models:

- **PERSON**: John Doe, Sarah Johnson, etc.
- **ORG**: Apple, Google, Microsoft, etc.
- **GPE**: USA, France, California (geo-political entities)
- **LOC**: Mount Everest, Amazon River (locations)

### Regex Pattern Matching

Detects structured data patterns:

| Pattern | Example | Weight |
|---------|---------|--------|
| Email | john@example.com | 30 |
| Phone (India) | +91 9876543210 | 30 |
| Phone (US) | (555) 123-4567 | 30 |
| Aadhaar | 1234 5678 9012 | 40 |
| PAN | AAAAA0000A | 40 |
| SSN | 123-45-6789 | 45 |
| Credit Card | 4532 1234 5678 9010 | 35 |
| IP Address | 192.168.1.1 | 10 |
| Bank Account | 12-digit+ number | 35 |
| Date of Birth | 01/15/1995 | 25 |

### Password Detection

Keyword-based detection for passwords and secrets:

- "password is", "pwd =", "pass:"
- "api_key =", "token =", "secret ="
- Weight: **50** (highest priority)

## 📊 Risk Score Calculation

### Formula
```
Risk Score = Σ (weight × frequency) capped at 100
```

### Weights (by data type)
- **PASSWORD/API_KEY**: 50 (highest risk)
- **AADHAAR/PAN/SSN**: 40-45 (government IDs)
- **CREDIT/DEBIT CARD**: 35 (financial)
- **PHONE/EMAIL**: 30 (contact info)
- **NAME/ORG/LOCATION**: 20 (identity info)
- **IP_ADDRESS**: 10 (lowest priority)

### Frequency Impact
Multiple occurrences increase risk with diminishing returns:
- 1st item: weight × 1.0
- 2nd item: weight × 1.5
- 3rd item: weight × 2.0
- etc.

### Risk Levels
- 🟢 **Green (0-30)**: Low risk - safe to share
- 🟡 **Yellow (31-70)**: Medium risk - some caution
- 🔴 **Red (71-100)**: High risk - significant PII detected

## 🔐 Security Features

### Password Security
- Bcrypt hashing with 12 rounds (computational cost)
- Passwords never stored in plain text
- Passwords never transmitted to AI

### Session Management
- Flask-Login for secure session handling
- User isolation - can only see own queries
- Logout clears session

### Data Masking
- PII replaced with generic placeholders
- Original-to-masked mapping maintained in-memory
- Mapping cleared after response unmasking

### Input Validation
- Username: 3+ characters, unique
- Password: 6+ characters
- Query: 3+ characters, no SQL injection possible (SQLAlchemy ORM)

### Database Security
- SQLite with SQLAlchemy ORM
- No direct SQL queries (prevents injection)
- User_id foreign key ensures data isolation

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
)
```

### Queries Table
```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    original_query TEXT NOT NULL,
    masked_query TEXT NOT NULL,
    risk_score FLOAT DEFAULT 0.0,
    detected_entities TEXT,  -- JSON string
    ai_response TEXT,
    unmasked_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## 🧪 Testing & Sample Inputs

### Test Case 1: Basic Information
```
My name is Alice Johnson. Can you help me with my projects?
```
Expected detections: PERSON

### Test Case 2: Complete Personal Info
```
Hi, I'm John Doe. My email is john.doe@company.com, and my phone is +1-555-123-4567. 
I live in San Francisco, California. 
My Aadhaar is 1234 5678 9012. 
What's the weather today?
```
Expected detections: PERSON, ORG, EMAIL, PHONE, GPE, LOC, AADHAAR
Expected risk score: ~100 (high)

### Test Case 3: Card Information
```
I need to report a transaction. 
My credit card is 4532-1234-5678-9010 
and the transaction happened on 03/15/2024.
My SSN for verification is 123-45-6789.
```
Expected detections: CREDIT_CARD, DATE_OF_BIRTH, SSN
Expected risk score: ~120 (capped at 100)

### Test Case 4: Passwords & Secrets
```
My API key is sk_live_51234567890abcdef 
and my database password is MySecurePass123!
Please don't share these with anyone.
```
Expected detections: PASSWORD, API_KEY
Expected risk score: ~100

### Test Case 5: Safe Query (No PII)
```
What are the benefits of machine learning in healthcare?
How can AI improve hospital operations?
```
Expected detections: None
Expected risk score: 0 (green)

## 🛠️ Troubleshooting

### Issue: "Cannot connect to Ollama API"
```
Error: Cannot connect to Ollama API at http://localhost:11434
```

**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Check Ollama is accessible: `curl http://localhost:11434/api/tags`
3. Verify port 11434 is not blocked by firewall

### Issue: "Model 'en_core_web_sm' not found"
```
Error: Model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm
```

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue: "Database locked" error
**Solution:**
1. Ensure only one Flask instance is running
2. Delete `privacy_queries.db` and restart
3. Check no other processes are accessing the database

### Issue: Port 5000 already in use
```
Error: Address already in use
```

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process or use different port
python app.py --port 5001
```

### Issue: Slow response from Ollama
**Solution:**
- First API call loads the model (~2-3 minutes)
- Ensure Ollama has enough system RAM (minimum 8GB)
- Check system resources: CPU, memory, disk

## 📚 Code Structure Overview

### app.py (500+ lines)
Main Flask application with:
- Authentication routes (signup, login, logout)
- Dashboard route
- API endpoints (/api/query, /api/history, /api/query/<id>)
- Risk score calculation
- Database integration
- Error handling

### auth.py (200+ lines)
Authentication and database models:
- `User` model (SQLAlchemy)
- `Query` model (SQLAlchemy)
- Password hashing (bcrypt)
- User registration and login verification

### pii_detector.py (300+ lines)
Regex-based PII detection:
- `RegexDetector` class with 11 pattern types
- `PII_Masker` class for bidirectional mapping
- Placeholder constants
- Password detection with context awareness

### nlp_detector.py (100+ lines)
SpaCy-based NER:
- `NLPDetector` class
- PERSON, ORG, GPE, LOC detection
- Entity extraction and summarization

### Templates (400+ lines)
HTML templates with Jinja2:
- `login.html` - Modern login interface
- `signup.html` - Registration form
- `dashboard.html` - Main application with tabs

### Static Files (600+ lines)
- `styles.css` - Comprehensive styling, dark mode support
- `script.js` - AJAX, DOM manipulation, UI updates

## 🎓 Learning Value

This project demonstrates:

1. **Full-Stack Development**
   - Backend: Python/Flask architecture
   - Frontend: HTML/CSS/JavaScript with AJAX
   - Real-time API integration

2. **Security Best Practices**
   - Password hashing (bcrypt)
   - SQL injection prevention (ORM)
   - Session management
   - Input validation

3. **NLP/ML Integration**
   - Transformer-based models (SpaCy)
   - Pattern matching algorithms
   - Entity recognition workflow

4. **Web Architecture**
   - RESTful API design
   - Database modeling
   - Authentication flows
   - Error handling

5. **UI/UX Design**
   - Responsive Bootstrap layout
   - Modern CSS styling
   - Accessibility considerations
   - Dark mode support

## 📈 Performance Notes

- **First SpaCy model load**: ~2 seconds
- **First Ollama request**: ~30-60 seconds (loads model)
- **Subsequent requests**: ~5-15 seconds depending on query length
- **Database queries**: <100ms
- **Regex pattern matching**: <50ms

## 🔄 Future Enhancements

Potential improvements for production:

1. **MultiModel Support**
   - Support for other LLMs (GPT-4, Claude)
   - Model selection in UI

2. **Advanced Features**
   - Custom masking rules per user
   - PII whitelist/blacklist
   - Batch query processing
   - Export query history as PDF

3. **Performance**
   - Redis caching for repeated queries
   - Async Ollama requests
   - Database indexing

4. **Security**
   - 2FA authentication
   - API key management
   - Audit logging
   - Encryption at rest

5. **Analytics**
   - Dashboard with statistics
   - PII frequency analysis
   - User activity tracking

## 📄 License

This project is for educational purposes. Use responsibly.

## 👨‍💻 Author Notes

Built for:
- Academic submissions
- Resume portfolio
- Technical interviews
- Production learning

The code is:
- ✅ Fully functional
- ✅ Well-commented
- ✅ Modular and maintainable
- ✅ Security-conscious
- ✅ Production-quality ready

## ❓ FAQ

**Q: Is my data safe?**
A: Yes. Your original data stays on your machine. Only masked versions are sent to AI.

**Q: Can I run this without internet?**
A: Yes! Everything runs locally (Flask + Ollama). No cloud calls.

**Q: What if masking fails?**
A: System defaults to showing error. No data is sent to AI if masking has issues.

**Q: Can I use other LLM models?**
A: Yes, modify the `call_ollama_api()` function in `app.py` to point to different Ollama models.

**Q: How do I change the secret key?**
A: Edit `app.py` line: `app.config['SECRET_KEY'] = 'your-new-secret-key'`

---

**Happy coding! 🚀**
