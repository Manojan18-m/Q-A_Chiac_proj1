#!/usr/bin/env python3
"""
Enhanced database initialization with all features
"""

from app import app, db, User, Question, Tag, Answer, Badge, UserBadge, Notification
from werkzeug.security import generate_password_hash
from init_badges import init_badges, award_badges_to_all_users

def init_enhanced_database():
    with app.app_context():
        print("=== Enhanced Database Initialization ===")
        
        # Create all tables
        db.create_all()
        print("✅ Created all database tables")
        
        # Initialize badges
        init_badges()
        
        # Create enhanced users with reputation
        users = [
            {
                'username': 'admin',
                'email': 'admin@qa.com',
                'password': 'admin123',
                'reputation': 1500,
                'badge_level': 'Expert'
            },
            {
                'username': 'john_doe',
                'email': 'john@example.com', 
                'password': 'password123',
                'reputation': 250,
                'badge_level': 'Intermediate'
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'password': 'password123',
                'reputation': 180,
                'badge_level': 'Apprentice'
            },
            {
                'username': 'expert_user',
                'email': 'expert@example.com',
                'password': 'expert123',
                'reputation': 800,
                'badge_level': 'Advanced'
            }
        ]
        
        for user_data in users:
            # Check if user exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    reputation=user_data['reputation'],
                    badge_level=user_data['badge_level']
                )
                db.session.add(user)
                print(f"✅ Created enhanced user: {user_data['username']} ({user_data['badge_level']})")
        
        db.session.commit()
        
        # Award badges to all users
        award_badges_to_all_users()
        
        print("\n=== Enhanced Database Ready ===")
        print("Features enabled:")
        print("✅ AI-powered recommendations")
        print("✅ Smart search with ranking")
        print("✅ User reputation system")
        print("✅ Badge and achievements")
        print("✅ Real-time notifications")
        print("✅ Modern UI with dark mode")
        print("✅ Advanced analytics")
        
        print("\nTest credentials:")
        print("admin / admin123 (Expert)")
        print("john_doe / password123 (Intermediate)") 
        print("jane_smith / password123 (Apprentice)")
        print("expert_user / expert123 (Advanced)")

if __name__ == '__main__':
    init_enhanced_database()
