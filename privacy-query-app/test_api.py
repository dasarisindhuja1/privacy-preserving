#!/usr/bin/env python3
"""
Test script for the Privacy Query API.
Creates a test user and tests the API endpoints.
"""

import requests
import json
from auth import User, db, signup_user
from app import app

def create_test_user():
    """Create test user if it doesn't exist."""
    with app.app_context():
        db.create_all()
        success, message = signup_user('test', 'test1234')
        print(f"User creation: {message}")
        return success

def test_api():
    """Test the API with authentication."""
    # First, create test user
    if not create_test_user():
        print("Failed to create test user")
        return

    # Start a session for authentication
    session = requests.Session()

    # Login
    login_data = {
        'username': 'test',
        'password': 'test1234'
    }

    login_response = session.post('http://localhost:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")

    if login_response.status_code != 200:
        print("Login failed")
        return

    # Test API query
    query_data = {
        'query': 'What is John Doe\'s email address and phone number?'
    }

    api_response = session.post(
        'http://localhost:5000/api/query',
        json=query_data,
        headers={'Content-Type': 'application/json'}
    )

    print(f"API status: {api_response.status_code}")
    print(f"API response: {api_response.json()}")

if __name__ == '__main__':
    test_api()