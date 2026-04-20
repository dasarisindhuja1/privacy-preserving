"""
Authentication module for user management and password handling.
Handles user registration, login, and password hashing using bcrypt.
"""

import bcrypt
from flask import current_app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for storing user information.
    
    Attributes:
        id: Unique user identifier (Primary Key)
        username: Unique username for login
        password_hash: Bcrypt hashed password (never store plain passwords)
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationship to queries
    queries = db.relationship('Query', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Query(db.Model):
    """
    Query model for storing user query history with PII detection results.
    
    Attributes:
        id: Unique query identifier (Primary Key)
        user_id: Foreign key reference to user
        original_query: The original query text from user
        masked_query: Query with PII replaced by placeholders
        risk_score: Calculated privacy risk score (0-100)
        detected_entities: JSON-encoded detected PII entities
        ai_response: Response from Ollama API
        unmasked_response: Response with original values restored
        timestamp: When the query was submitted
    """
    __tablename__ = 'queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_query = db.Column(db.Text, nullable=False)
    masked_query = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Float, default=0.0)
    detected_entities = db.Column(db.Text, default='{}')  # JSON string
    ai_response = db.Column(db.Text, nullable=True)
    unmasked_response = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<Query {self.id} by User {self.user_id}>'


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Bcrypt hashed password as string
    """
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    
    # Generate salt and hash password
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good security/performance balance
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain text password against its hash.
    
    Args:
        password: Plain text password to verify
        password_hash: Bcrypt hash to compare against
        
    Returns:
        True if password matches hash, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def signup_user(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user with username and password.
    
    Args:
        username: Desired username
        password: Desired password
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validate inputs
    if not username or not password:
        return False, "Username and password cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Check if user exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return False, "Username already exists"
    
    try:
        # Hash password and create user
        password_hash = hash_password(password)
        new_user = User(username=username, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        return True, "User registered successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"Registration error: {str(e)}"


def login_user_verify(username: str, password: str) -> tuple:
    """
    Verify user credentials for login.
    
    Args:
        username: Username to log in
        password: Password to verify
        
    Returns:
        Tuple of (success: bool, user: User or None)
    """
    if not username or not password:
        return False, None
    
    user = User.query.filter_by(username=username).first()
    
    if user and verify_password(password, user.password_hash):
        return True, user
    
    return False, None
