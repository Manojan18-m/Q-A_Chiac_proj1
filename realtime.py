#!/usr/bin/env python3
"""
Real-time features for Q&A Platform
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from app import app, db, User, Question, Answer, Notification
from datetime import datetime
import json

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

class NotificationManager:
    def __init__(self):
        self.active_users = set()
    
    def create_notification(self, user_id, content, notification_type='info'):
        """Create and send notification"""
        with app.app_context():
            notification = Notification(
                user_id=user_id,
                content=content,
                notification_type=notification_type
            )
            db.session.add(notification)
            db.session.commit()
            
            # Send real-time notification
            socketio.emit('notification', {
                'id': notification.id,
                'content': content,
                'type': notification_type,
                'created_at': notification.created_at.isoformat()
            }, room=f'user_{user_id}')
            
            return notification
    
    def notify_new_question(self, question):
        """Notify users about new question in their interested tags"""
        with app.app_context():
            # Get users who might be interested in this question
            interested_users = set()
            
            for tag in question.tags:
                # Find users who have answered questions with similar tags
                for answer in Answer.query.join(Answer.question).join(Question.tags).filter(Tag.id == tag.id).all():
                    interested_users.add(answer.user_id)
            
            # Notify interested users
            for user_id in interested_users:
                if user_id != question.user_id:  # Don't notify the author
                    self.create_notification(
                        user_id,
                        f'New question: "{question.title}" in tags you follow',
                        'info'
                    )
    
    def notify_new_answer(self, answer):
        """Notify question author about new answer"""
        self.create_notification(
            answer.question.user_id,
            f'New answer to your question: "{answer.question.title}"',
            'success'
        )
    
    def notify_accepted_answer(self, answer):
        """Notify answer author about accepted answer"""
        self.create_notification(
            answer.user_id,
            f'Your answer to "{answer.question.title}" was accepted!',
            'achievement'
        )
    
    def notify_badge_earned(self, user_id, badge_name):
        """Notify user about earned badge"""
        self.create_notification(
            user_id,
            f'Congratulations! You earned the "{badge_name}" badge!',
            'achievement'
        )

# Initialize notification manager
notification_manager = NotificationManager()

# SocketIO event handlers
@socketio.on('connect')
def on_connect():
    print(f'Client connected: {request.sid}')
    
    # Join user-specific room if authenticated
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        notification_manager.active_users.add(current_user.id)
        
        # Send unread notifications count
        unread_count = Notification.query.filter_by(
            user_id=current_user.id, 
            is_read=False
        ).count()
        
        emit('unread_count', {'count': unread_count})

@socketio.on('disconnect')
def on_disconnect():
    print(f'Client disconnected: {request.sid}')
    
    if current_user.is_authenticated:
        notification_manager.active_users.discard(current_user.id)

@socketio.on('mark_notifications_read')
def on_mark_notifications_read():
    """Mark all notifications as read for current user"""
    if current_user.is_authenticated:
        with app.app_context():
            Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
            db.session.commit()
            
            emit('notifications_marked_read')

@socketio.on('typing_start')
def on_typing_start(data):
    """Handle typing indicators"""
    room = data.get('room')
    if room:
        emit('user_typing', {
            'user': current_user.username,
            'action': 'started'
        }, room=room, include_self=False)

@socketio.on('typing_stop')
def on_typing_stop(data):
    """Handle typing indicators"""
    room = data.get('room')
    if room:
        emit('user_typing', {
            'user': current_user.username,
            'action': 'stopped'
        }, room=room, include_self=False)

# Room management for question pages
@socketio.on('join_question')
def on_join_question(data):
    """Join a question room for real-time updates"""
    question_id = data.get('question_id')
    if question_id:
        join_room(f'question_{question_id}')
        emit('joined_question', {'question_id': question_id})

@socketio.on('leave_question')
def on_leave_question(data):
    """Leave a question room"""
    question_id = data.get('question_id')
    if question_id:
        leave_room(f'question_{question_id}')
        emit('left_question', {'question_id': question_id})

# Live user count
@socketio.on('request_online_count')
def on_request_online_count():
    emit('online_count', {'count': len(notification_manager.active_users)})

# Helper functions to trigger notifications
def trigger_new_question_notification(question):
    """Trigger notification for new question"""
    notification_manager.notify_new_question(question)

def trigger_new_answer_notification(answer):
    """Trigger notification for new answer"""
    notification_manager.notify_new_answer(answer)

def trigger_accepted_answer_notification(answer):
    """Trigger notification for accepted answer"""
    notification_manager.notify_accepted_answer(answer)

def trigger_badge_notification(user_id, badge_name):
    """Trigger notification for earned badge"""
    notification_manager.notify_badge_earned(user_id, badge_name)
