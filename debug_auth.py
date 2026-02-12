#!/usr/bin/env python3
"""
Debug script to test authentication and fix database issues
"""

from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

def test_authentication():
    with app.app_context():
        print("=== Authentication Debug ===")
        
        # Test existing users
        users = User.query.all()
        print(f"Found {len(users)} users in database")
        
        for user in users:
            print(f"\nUser: {user.username}")
            print(f"Email: {user.email}")
            print(f"Password hash: {user.password_hash[:50]}...")
            
            # Test password verification
            test_passwords = ['password123', 'Password123', 'password', '123456']
            for pwd in test_passwords:
                if check_password_hash(user.password_hash, pwd):
                    print(f"✅ Password '{pwd}' works for {user.username}")
                    break
            else:
                print(f"❌ No common passwords work for {user.username}")
        
        # Create a test user with known credentials
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('testpass123')
            )
            db.session.add(test_user)
            db.session.commit()
            print(f"\n✅ Created test user: testuser / testpass123")
        else:
            print(f"\n✅ Test user already exists: testuser / testpass123")
        
        # Test the test user
        test_user = User.query.filter_by(username='testuser').first()
        if check_password_hash(test_user.password_hash, 'testpass123'):
            print("✅ Test user authentication works!")
        else:
            print("❌ Test user authentication failed!")

def fix_database_issues():
    with app.app_context():
        print("\n=== Database Configuration ===")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Check if database file exists
        import os
        db_path = 'qa_platform.db'
        if os.path.exists(db_path):
            print(f"✅ Database file exists: {db_path}")
            print(f"File size: {os.path.getsize(db_path)} bytes")
        else:
            print(f"❌ Database file not found: {db_path}")
        
        # Test database connection
        try:
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

def reset_sample_users():
    with app.app_context():
        print("\n=== Reset Sample Users ===")
        
        # Delete existing sample users
        User.query.filter(User.username.in_(['john_doe', 'jane_smith'])).delete(synchronize_session=False)
        db.session.commit()
        
        # Create fresh sample users with known passwords
        users = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'password123'
            },
            {
                'username': 'jane_smith', 
                'email': 'jane@example.com',
                'password': 'password123'
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
        print("✅ Sample users reset successfully!")

if __name__ == '__main__':
    fix_database_issues()
    test_authentication()
    reset_sample_users()
    print("\n=== Test Credentials ===")
    print("john_doe / password123")
    print("jane_smith / password123") 
    print("testuser / testpass123")
