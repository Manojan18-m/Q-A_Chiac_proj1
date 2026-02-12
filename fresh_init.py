#!/usr/bin/env python3
"""
Fresh database initialization with all enhanced features
"""

import os
from app import app, db, User, Question, Tag, Answer, Badge, UserBadge, Notification
from werkzeug.security import generate_password_hash
from init_badges import init_badges, award_badges_to_all_users

def fresh_init():
    with app.app_context():
        print("=== Fresh Database Initialization ===")
        
        # Drop and recreate database
        db.drop_all()
        print("✅ Dropped all existing tables")
        
        db.create_all()
        print("✅ Created fresh database tables")
        
        # Initialize badges
        init_badges()
        
        # Create enhanced users
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
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                reputation=user_data['reputation'],
                badge_level=user_data['badge_level']
            )
            db.session.add(user)
            print(f"✅ Created user: {user_data['username']} ({user_data['badge_level']})")
        
        db.session.commit()
        
        # Award badges
        award_badges_to_all_users()
        
        # Add sample questions
        from add_sample_questions import create_sample_questions
        create_sample_questions()
        
        print("\n=== Enhanced Q&A Platform Ready! ===")
        print("✅ AI-powered recommendations")
        print("✅ Smart search with ranking")
        print("✅ User reputation system")
        print("✅ Badge and achievements")
        print("✅ Real-time notifications")
        print("✅ Modern UI with dark mode")
        print("✅ Advanced analytics")
        print("✅ 100+ sample questions")
        
        print("\n🎯 Prize-Winning Features:")
        print("🤖 AI-powered question recommendations")
        print("🔍 Smart search with relevance ranking")
        print("🏆 Gamification with badges and reputation")
        print("🌙 Dark mode and modern UI")
        print("📊 Real-time analytics dashboard")
        print("🔔 Live notifications system")
        print("💬 Real-time chat and typing indicators")
        print("📱 Responsive design for all devices")
        print("🔒 Enhanced security and authentication")
        
        print("\n🔑 Test Credentials:")
        print("admin / admin123 (Expert - 1500 rep)")
        print("john_doe / password123 (Intermediate - 250 rep)") 
        print("jane_smith / password123 (Apprentice - 180 rep)")
        print("expert_user / expert123 (Advanced - 800 rep)")

if __name__ == '__main__':
    fresh_init()
