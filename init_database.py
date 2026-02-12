#!/usr/bin/env python3
"""
Improved database initialization script
"""

from app import app, db, User, Question, Tag, Answer
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    with app.app_context():
        print("=== Database Initialization ===")
        
        # Drop all tables and recreate
        db.drop_all()
        print("✅ Dropped all existing tables")
        
        db.create_all()
        print("✅ Created new database tables")
        
        # Create users with known credentials
        users = [
            {
                'username': 'admin',
                'email': 'admin@qa.com',
                'password': 'admin123'
            },
            {
                'username': 'john_doe',
                'email': 'john@example.com', 
                'password': 'password123'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'password123'
            },
            {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        ]
        
        for user_data in users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password'])
            )
            db.session.add(user)
            print(f"✅ Created user: {user_data['username']} / {user_data['password']}")
        
        db.session.commit()
        
        # Create basic tags
        tags = ['python', 'javascript', 'flask', 'database', 'web-development', 'api']
        for tag_name in tags:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        
        db.session.commit()
        print(f"✅ Created {len(tags)} basic tags")
        
        print("\n=== Database Ready ===")
        print("Test credentials:")
        print("admin / admin123")
        print("john_doe / password123") 
        print("jane_smith / password123")
        print("testuser / testpass123")

if __name__ == '__main__':
    init_database()
