#!/usr/bin/env python3
"""
Initialize badge system for Q&A Platform
"""

from app import app, db, Badge, UserBadge, User
from datetime import datetime

def init_badges():
    """Initialize the badge system with predefined badges"""
    with app.app_context():
        print("=== Initializing Badge System ===")
        
        # Create badges
        badges_data = [
            {
                'name': 'First Question',
                'description': 'Asked your first question',
                'icon': '❓',
                'requirement_type': 'questions',
                'requirement_value': 1
            },
            {
                'name': 'Question Master',
                'description': 'Asked 10 questions',
                'icon': '🎯',
                'requirement_type': 'questions',
                'requirement_value': 10
            },
            {
                'name': 'First Answer',
                'description': 'Provided your first answer',
                'icon': '💬',
                'requirement_type': 'answers',
                'requirement_value': 1
            },
            {
                'name': 'Helpful',
                'description': 'Provided 10 answers',
                'icon': '🤝',
                'requirement_type': 'answers',
                'requirement_value': 10
            },
            {
                'name': 'Problem Solver',
                'description': 'Had 5 answers accepted',
                'icon': '✅',
                'requirement_type': 'accepted_answers',
                'requirement_value': 5
            },
            {
                'name': 'Expert',
                'description': 'Reached 1000 reputation',
                'icon': '👑',
                'requirement_type': 'reputation',
                'requirement_value': 1000
            },
            {
                'name': 'Popular',
                'description': 'Reached 500 reputation',
                'icon': '⭐',
                'requirement_type': 'reputation',
                'requirement_value': 500
            },
            {
                'name': 'Rising Star',
                'description': 'Reached 100 reputation',
                'icon': '🌟',
                'requirement_type': 'reputation',
                'requirement_value': 100
            },
            {
                'name': 'Good Citizen',
                'description': 'Reached 50 reputation',
                'icon': '🌱',
                'requirement_type': 'reputation',
                'requirement_value': 50
            },
            {
                'name': 'Voter',
                'description': 'Cast 25 votes',
                'icon': '🗳️',
                'requirement_type': 'votes',
                'requirement_value': 25
            },
            {
                'name': 'Critic',
                'description': 'Cast 100 votes',
                'icon': '⚖️',
                'requirement_type': 'votes',
                'requirement_value': 100
            },
            {
                'name': 'Early Adopter',
                'description': 'Joined in the first month',
                'icon': '🚀',
                'requirement_type': 'early_adopter',
                'requirement_value': 1
            }
        ]
        
        for badge_data in badges_data:
            # Check if badge already exists
            existing_badge = Badge.query.filter_by(name=badge_data['name']).first()
            if not existing_badge:
                badge = Badge(**badge_data)
                db.session.add(badge)
                print(f"✅ Created badge: {badge_data['name']}")
            else:
                print(f"⚠️ Badge already exists: {badge_data['name']}")
        
        db.session.commit()
        print(f"✅ Badge system initialized with {len(badges_data)} badges")

def check_and_award_badges(user_id):
    """Check if user has earned any new badges and award them"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return
        
        # Update user stats
        user.reputation = user.calculate_reputation()
        user.update_badge_level()
        
        # Calculate user statistics
        stats = {
            'questions': len(user.questions),
            'answers': len(user.answers),
            'accepted_answers': len([a for a in user.answers if a.is_accepted]),
            'reputation': user.reputation,
            'votes': len(user.votes),
            'early_adopter': 1 if (datetime.utcnow() - user.created_at).days <= 30 else 0
        }
        
        # Check each badge
        badges = Badge.query.all()
        newly_earned = []
        
        for badge in badges:
            # Check if user already has this badge
            existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
            if existing:
                continue
            
            # Check if user meets requirements
            requirement_type = badge.requirement_type
            requirement_value = badge.requirement_value
            
            if requirement_type in stats and stats[requirement_type] >= requirement_value:
                # Award badge
                user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
                db.session.add(user_badge)
                newly_earned.append(badge.name)
                print(f"🏆 {user.username} earned badge: {badge.name}")
        
        if newly_earned:
            db.session.commit()
            
            # Trigger notifications for new badges
            try:
                from realtime import trigger_badge_notification
                for badge_name in newly_earned:
                    trigger_badge_notification(user_id, badge_name)
            except ImportError:
                pass  # Real-time not available
        
        return newly_earned

def award_badges_to_all_users():
    """Check and award badges to all existing users"""
    with app.app_context():
        users = User.query.all()
        print(f"Checking badges for {len(users)} users...")
        
        total_badges_awarded = 0
        for user in users:
            badges = check_and_award_badges(user.id)
            total_badges_awarded += len(badges)
        
        print(f"✅ Awarded {total_badges_awarded} badges total")

if __name__ == '__main__':
    init_badges()
    award_badges_to_all_users()
