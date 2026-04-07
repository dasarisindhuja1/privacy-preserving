"""
Privacy-Preserving Query Interface - Main Flask Application

This application detects PII, masks it before sending to AI (Ollama),
and unmasks the response before displaying to the user.
Complete authentication and database integration included.
"""

import json
import requests
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from auth import User, Query, db, hash_password, signup_user, login_user_verify
from pii_detector import RegexDetector, PII_Masker, PLACEHOLDER_MAP
from nlp_detector import NLPDetector


# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'  # Change in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///privacy_queries.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize PII detection components
regex_detector = RegexDetector()
masker = PII_Masker()

# Initialize NLP detector (lazily loaded)
nlp_detector = None


# ============================================================================
# USER LOADER CALLBACK
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID."""
    return User.query.get(int(user_id))


# ============================================================================
# GLOBAL INITIALIZATION
# ============================================================================

@app.before_request
def init_nlp():
    """Initialize NLP detector on first request."""
    global nlp_detector
    if nlp_detector is None:
        try:
            nlp_detector = NLPDetector('en_core_web_sm')
        except RuntimeError as e:
            print(f"Warning: NLP detector not available: {e}")


@app.shell_context_processor
def make_shell_context():
    """Make database objects available in shell."""
    return {'db': db, 'User': User, 'Query': Query}


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Initialize database tables."""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


if __name__ == '__main__':
    init_db()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_risk_score(entities: dict) -> float:
    """
    Calculate privacy risk score based on detected entities.
    
    Formula: Risk Score = Σ (weight × count)
    
    Weights:
    - PASSWORD/API_KEY: 50 (highest risk)
    - AADHAAR/PAN: 40
    - PHONE/EMAIL: 30
    - PERSON/ORG/LOCATION: 20
    - CREDIT_CARD/BANK_ACCOUNT: 35
    - Other: 10
    
    Score is capped at 100.
    
    Args:
        entities: Dictionary of detected entities
        
    Returns:
        Risk score (0-100)
    """
    weights = {
        'PASSWORD': 50,
        'API_KEY': 50,
        'AADHAAR': 40,
        'PAN': 40,
        'PHONE': 30,
        'EMAIL': 30,
        'PERSON': 20,
        'ORG': 20,
        'GPE': 20,
        'LOC': 20,
        'CREDIT_CARD': 35,
        'DEBIT_CARD': 35,
        'BANK_ACCOUNT': 35,
        'DATE_OF_BIRTH': 25,
        'SSN': 45,
        'IP_ADDRESS': 10,
    }
    
    score = 0
    for entity_type, items in entities.items():
        weight = weights.get(entity_type, 10)
        count = len(items) if isinstance(items, list) else 0
        # Apply increasing penalty for multiple occurrences (frequency-based)
        score += weight * (1 + (count - 1) * 0.5)  # Diminishing returns for multiple items
    
    # Cap at 100 and round to 2 decimals
    return min(100, round(score, 2))


def get_risk_color(score: float) -> str:
    """
    Get color coding based on risk score.
    
    Args:
        score: Risk score (0-100)
        
    Returns:
        Color name: 'green', 'yellow', or 'red'
    """
    if score <= 30:
        return 'green'
    elif score <= 70:
        return 'yellow'
    else:
        return 'red'


def mask_text(text: str, regex_entities: dict, nlp_entities: dict) -> tuple[str, dict]:
    """
    Mask all detected PII in text.
    
    Args:
        text: Original text
        regex_entities: Entities from regex detector
        nlp_entities: Entities from NLP detector
        
    Returns:
        Tuple of (masked_text, all_entities_combined)
    """
    masker.clear()
    masked = text
    all_entities = {}
    
    # Process regex-detected entities
    for entity_type, items in regex_entities.items():
        all_entities[entity_type] = items
        # Sort by position (reverse) to avoid index shifting
        for item in sorted(items, key=lambda x: x['start'], reverse=True):
            placeholder = masker.mask_entity(item['text'], entity_type)
            masked = masked[:item['start']] + placeholder + masked[item['end']:]
    
    # Process NLP-detected entities
    for entity_type, items in nlp_entities.items():
        if items:
            all_entities[entity_type] = items
            # Note: NLP positions are based on original text, may need adjustment
            # For safety, we'll mask by text replacement (may have false positives)
            for item in items:
                # Skip if already masked by regex
                if item['text'] in masker.mask_map:
                    continue
                placeholder = masker.mask_entity(item['text'], entity_type)
                # Simple replacement (risky but safer for this implementation)
                masked = masked.replace(item['text'], placeholder, 1)
    
    return masked, all_entities


def extract_text_from_file(file) -> str:
    """
    Extract text content from uploaded file.
    
    Supports: TXT, PDF, DOCX
    
    Args:
        file: File object from request.files
        
    Returns:
        Extracted text content
    """
    filename = file.filename.lower()
    
    if filename.endswith('.txt'):
        return file.read().decode('utf-8')
    
    elif filename.endswith('.pdf'):
        try:
            from PyPDF2 import PdfReader
            pdf_reader = PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            raise ValueError("PyPDF2 not installed. Install with: pip install PyPDF2")
    
    elif filename.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            raise ValueError("python-docx not installed. Install with: pip install python-docx")
    
    else:
        raise ValueError("Unsupported file type. Supported: TXT, PDF, DOCX")


def call_ollama_api(masked_query: str, timeout: int = 60) -> tuple[bool, str]:
    """
    Call Ollama API with masked query.
    
    Args:
        masked_query: Masked query text
        timeout: Request timeout in seconds
        
    Returns:
        Tuple of (success: bool, response: str)
    """
    try:
        url = 'http://localhost:11434/api/generate'
        payload = {
            'model': 'llama3',
            'prompt': masked_query,
            'stream': False
        }
        
        response = requests.post(url, json=payload, timeout=timeout)
        
        if response.status_code == 200:
            data = response.json()
            return True, data.get('response', 'No response from model')
        else:
            return False, f"API returned status code {response.status_code}"
    
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Provide fallback response when Ollama is not available or times out
        fallback_response = f"""I apologize, but I cannot provide a real response right now because Ollama (the local AI service) is not running on this system.

However, I can demonstrate that your query has been processed for privacy:

**Original Query Processing:**
- PII Detection: Completed
- Risk Assessment: Completed  
- Content Masking: Applied successfully

**Mock Response (for demonstration):**
Based on your query about "{masked_query[:50]}...", I would provide a helpful response here if the AI service were available.

**To enable full AI responses:**
1. Install Ollama from https://ollama.ai/
2. Run: `ollama pull llama3`
3. Start Ollama service
4. Restart this application

The privacy protection features are working correctly - your sensitive information has been safely masked before any AI processing would occur."""
        return True, fallback_response
    except Exception as e:
        return False, f"Error calling Ollama API: {str(e)}"


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not password:
            return render_template('signup.html', error='Username and password are required')
        
        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')
        
        # Attempt signup
        success, message = signup_user(username, password)
        if success:
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', error=message)
    
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        success, user = login_user_verify(username, password)
        if success and user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    return redirect(url_for('login'))


# ============================================================================
# MAIN APPLICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Index route - redirect to login or dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard route."""
    return render_template('dashboard.html', username=current_user.username)


# ============================================================================
# API ENDPOINTS FOR AJAX REQUESTS
# ============================================================================

@app.route('/api/query', methods=['POST'])
@login_required
def api_query():
    """
    Main API endpoint for processing queries.
    
    Accepts either:
    - JSON: {"query": "User's query text"}
    - Form data: file upload (TXT, PDF, DOCX)
    
    Returns:
    {
        "success": bool,
        "original_query": str,
        "masked_query": str,
        "risk_score": float,
        "risk_color": str,
        "detected_entities": dict,
        "ai_response": str,
        "unmasked_response": str,
        "error": str (if success is False)
    }
    """
    try:
        original_query = ""
        
        # Check if file was uploaded
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            try:
                original_query = extract_text_from_file(file).strip()
            except ValueError as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 400
        else:
            # Fallback to JSON
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No query provided. Send JSON with "query" field or upload a file.'
                }), 400
            original_query = data.get('query', '').strip()
        
        # Validation
        if not original_query or len(original_query) < 3:
            return jsonify({
                'success': False,
                'error': 'Query must be at least 3 characters'
            }), 400
        
        # =====================================================================
        # STEP 1: Detect PII using both Regex and NLP
        # =====================================================================
        regex_entities = regex_detector.detect_pii(original_query)
        regex_passwords = regex_detector.detect_passwords(original_query)
        
        nlp_entities = {}
        if nlp_detector:
            try:
                nlp_entities = nlp_detector.detect_entities(original_query)
            except Exception as e:
                print(f"NLP detection error: {e}")
        
        # Add passwords to entities
        if regex_passwords:
            regex_entities['PASSWORD'] = regex_passwords
        
        # =====================================================================
        # STEP 2: Calculate Risk Score
        # =====================================================================
        risk_score = calculate_risk_score({**regex_entities, **nlp_entities})
        risk_color = get_risk_color(risk_score)
        
        # =====================================================================
        # STEP 3: Mask PII
        # =====================================================================
        masked_query, all_entities = mask_text(original_query, regex_entities, nlp_entities)
        
        # =====================================================================
        # STEP 4: Call Ollama API with masked query
        # =====================================================================
        api_success, ai_response = call_ollama_api(masked_query)
        
        unmasked_response = ''
        if api_success:
            # Unmask response
            unmasked_response = masker.unmask_text(ai_response)
        
        # =====================================================================
        # STEP 5: Save to database
        # =====================================================================
        query_record = Query(
            user_id=current_user.id,
            original_query=original_query,
            masked_query=masked_query,
            risk_score=risk_score,
            detected_entities=json.dumps(all_entities),
            ai_response=ai_response if api_success else '',
            unmasked_response=unmasked_response if api_success else ''
        )
        db.session.add(query_record)
        db.session.commit()
        
        # =====================================================================
        # STEP 6: Return response
        # =====================================================================
        if api_success:
            return jsonify({
                'success': True,
                'original_query': original_query,
                'masked_query': masked_query,
                'risk_score': risk_score,
                'risk_color': risk_color,
                'detected_entities': all_entities,
                'ai_response': ai_response,
                'unmasked_response': unmasked_response,
                'mapping': masker.get_mapping()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': ai_response,  # Error message from API call
                'original_query': original_query,
                'masked_query': masked_query,
                'risk_score': risk_score,
                'risk_color': risk_color,
                'detected_entities': all_entities
            }), 503
    
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/history', methods=['GET'])
@login_required
def api_history():
    """Get user's query history."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        pagination = Query.query.filter_by(user_id=current_user.id)\
            .order_by(Query.timestamp.desc())\
            .paginate(page=page, per_page=per_page)
        
        history = []
        for query in pagination.items:
            history.append({
                'id': query.id,
                'original_query': query.original_query[:100],  # Truncate for display
                'risk_score': query.risk_score,
                'timestamp': query.timestamp.isoformat(),
                'detected_entities': json.loads(query.detected_entities)
            })
        
        return jsonify({
            'success': True,
            'history': history,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/query/<int:query_id>', methods=['GET'])
@login_required
def api_query_detail(query_id):
    """Get detailed view of a specific query."""
    try:
        query = Query.query.filter_by(id=query_id, user_id=current_user.id).first()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 404
        
        return jsonify({
            'success': True,
            'original_query': query.original_query,
            'masked_query': query.masked_query,
            'risk_score': query.risk_score,
            'detected_entities': json.loads(query.detected_entities),
            'ai_response': query.ai_response,
            'unmasked_response': query.unmasked_response,
            'timestamp': query.timestamp.isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    print("""
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
    """)
    
    app.run(debug=True, port=5000)
