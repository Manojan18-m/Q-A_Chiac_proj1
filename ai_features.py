#!/usr/bin/env python3
"""
AI-powered features for Q&A Platform
"""

import re
from collections import Counter
from difflib import SequenceMatcher
import random
from datetime import datetime, timedelta

class AIRecommendationEngine:
    def __init__(self):
        self.stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'can', 'could', 'should', 'may', 'might', 'must', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where',
            'why', 'how', 'this', 'that', 'these', 'those', 'am', 'is', 'are'
        ])
    
    def extract_keywords(self, text):
        """Extract keywords from text"""
        # Remove HTML tags and special characters
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words and filter stop words
        words = [word for word in text.split() if word not in self.stop_words and len(word) > 2]
        
        return Counter(words)
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        keywords1 = self.extract_keywords(text1)
        keywords2 = self.extract_keywords(text2)
        
        # Find common keywords
        common_keywords = set(keywords1.keys()) & set(keywords2.keys())
        
        if not common_keywords:
            return 0.0
        
        # Calculate Jaccard similarity
        similarity = len(common_keywords) / len(set(keywords1.keys()) | set(keywords2.keys()))
        
        return similarity
    
    def get_similar_questions(self, question_id, limit=5):
        """Get similar questions based on content"""
        from flask import current_app
        from app import Question
        
        # Get the database session from the current app context
        db = current_app.extensions['sqlalchemy'].db
        
        current_question = db.session.query(Question).get(question_id)
        if not current_question:
            return []
        
        all_questions = db.session.query(Question).filter(Question.id != question_id).all()
        
        similarities = []
        for q in all_questions:
            similarity = self.calculate_similarity(
                current_question.title + ' ' + current_question.content,
                q.title + ' ' + q.content
            )
            if similarity > 0.1:  # Only include questions with some similarity
                similarities.append((q, similarity))
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [q[0] for q in similarities[:limit]]
    
    def recommend_questions_for_user(self, user_id, limit=10):
        """Recommend questions based on user's interests and activity"""
        from flask import current_app
        from app import User, Question
        
        # Get the database session from the current app context
        db = current_app.extensions['sqlalchemy'].db
        
        user = db.session.query(User).get(user_id)
        if not user:
            return []
        
        # Get user's question tags
        user_tags = set()
        for question in user.questions:
            for tag in question.tags:
                user_tags.add(tag.name)
        
        # Get user's answered questions tags
        for answer in user.answers:
            for tag in answer.question.tags:
                user_tags.add(tag.name)
        
        # Find questions with similar tags that user hasn't interacted with
        user_question_ids = [q.id for q in user.questions]
        user_answer_ids = [a.question_id for a in user.answers]
        interacted_ids = set(user_question_ids + user_answer_ids)
        
        recommended_questions = []
        all_questions = db.session.query(Question).filter(~Question.id.in_(interacted_ids)).all()
        
        for question in all_questions:
            question_tags = set(tag.name for tag in question.tags)
            tag_similarity = len(user_tags & question_tags) / max(len(user_tags), len(question_tags), 1)
            
            # Consider question popularity (views, answers, votes)
            popularity_score = len(question.answers) * 0.1 + len(question.votes) * 0.05
            
            # Calculate recommendation score
            score = tag_similarity * 0.7 + popularity_score * 0.3
            
            if score > 0.1:  # Only include questions with meaningful score
                recommended_questions.append((question, score))
        
        # Sort by recommendation score
        recommended_questions.sort(key=lambda x: x[1], reverse=True)
        return [q[0] for q in recommended_questions[:limit]]

class SmartSearchEngine:
    def __init__(self):
        self.ai_engine = AIRecommendationEngine()
    
    def search_questions(self, query, user_id=None, limit=20):
        """Advanced search with AI-powered ranking"""
        from flask import current_app
        from app import Question, Tag
        
        # Get the database session from the current app context
        db = current_app.extensions['sqlalchemy'].db
        
        # Basic text search
        basic_results = db.session.query(Question).filter(
            Question.title.contains(query) | 
            Question.content.contains(query)
        ).all()
        
        # Tag-based search
        tag_results = []
        if query.lower() in [tag.name.lower() for tag in db.session.query(Tag).all()]:
            tag = db.session.query(Tag).filter(Tag.name.ilike(f'%{query}%')).first()
            if tag:
                tag_results = tag.questions
        
        # Combine and deduplicate results
        all_results = list(set(basic_results + tag_results))
        
        # Rank results by relevance
        ranked_results = []
        for question in all_results:
            # Calculate relevance score
            title_similarity = self.ai_engine.calculate_similarity(query, question.title)
            content_similarity = self.ai_engine.calculate_similarity(query, question.content)
            
            # Boost score for exact matches
            if query.lower() in question.title.lower():
                title_similarity *= 2.0
            if query.lower() in question.content.lower():
                content_similarity *= 1.5
            
            # Consider popularity and recency
            popularity_score = len(question.answers) * 0.1 + len(question.votes) * 0.05
            recency_score = max(0, 1 - (datetime.utcnow() - question.created_at).days / 365)
            
            # Calculate final score
            relevance_score = (title_similarity * 0.5 + content_similarity * 0.3 + 
                             popularity_score * 0.1 + recency_score * 0.1)
            
            ranked_results.append((question, relevance_score))
        
        # Sort by relevance score
        ranked_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return just the questions (they're still attached to the session)
        return [q[0] for q in ranked_results[:limit]]
    
    def get_trending_topics(self, days=7, limit=10):
        """Get trending topics based on recent activity"""
        from flask import current_app
        from app import Question, Tag
        
        # Get the database session from the current app context
        db = current_app.extensions['sqlalchemy'].db
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get recent questions
        recent_questions = db.session.query(Question).filter(Question.created_at >= cutoff_date).all()
        
        # Count tag frequencies
        tag_counts = Counter()
        for question in recent_questions:
            for tag in question.tags:
                tag_counts[tag.name] += len(question.answers) + 1  # Weight by engagement
        
        # Get top trending tags
        trending_tags = tag_counts.most_common(limit)
        
        # Get sample questions for each trending tag
        trending_topics = []
        for tag_name, count in trending_tags:
            tag = db.session.query(Tag).filter_by(name=tag_name).first()
            if tag:
                # Use a proper query instead of the relationship
                sample_questions = db.session.query(Question).join(Question.tags).filter(
                    Tag.id == tag.id
                ).order_by(Question.created_at.desc()).limit(3).all()
                trending_topics.append({
                    'tag': tag,
                    'activity_count': count,
                    'sample_questions': sample_questions
                })
        
        return trending_topics

class ContentAnalyzer:
    def analyze_question_quality(self, question):
        """Analyze question quality for moderation and ranking"""
        quality_score = 0.0
        
        # Length analysis
        title_length = len(question.title.split())
        content_length = len(question.content.split())
        
        if 5 <= title_length <= 15:
            quality_score += 0.2
        if content_length >= 20:
            quality_score += 0.2
        
        # Code presence (good for technical questions)
        if '```' in question.content or '<code>' in question.content:
            quality_score += 0.1
        
        # Question marks (indicates actual question)
        if '?' in question.title:
            quality_score += 0.1
        
        # Tag relevance
        if len(question.tags) >= 2:
            quality_score += 0.1
        
        # Engagement potential
        if len(question.content) > 100:
            quality_score += 0.1
        
        # Grammar check (simplified)
        if question.title[0].isupper() and question.title[-1] in ['?', '.']:
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def suggest_tags(self, title, content, limit=5):
        """Suggest relevant tags based on content"""
        from flask import current_app
        from app import Tag
        
        # Get the database session from the current app context
        db = current_app.extensions['sqlalchemy'].db
        
        combined_text = (title + ' ' + content).lower()
        
        # Common tech keywords and their associated tags
        tech_keywords = {
            'python': ['python', 'programming'],
            'javascript': ['javascript', 'web-development', 'frontend'],
            'react': ['react', 'javascript', 'frontend'],
            'flask': ['flask', 'python', 'web-development'],
            'django': ['django', 'python', 'web-development'],
            'sql': ['sql', 'database'],
            'database': ['database', 'sql'],
            'api': ['api', 'rest', 'backend'],
            'html': ['html', 'frontend', 'web-development'],
            'css': ['css', 'frontend', 'web-development'],
            'docker': ['docker', 'devops', 'containers'],
            'git': ['git', 'version-control'],
            'machine learning': ['machine-learning', 'ai', 'python'],
            'ai': ['ai', 'machine-learning'],
            'security': ['security', 'authentication'],
            'testing': ['testing', 'unit-testing'],
            'performance': ['performance', 'optimization']
        }
        
        suggested_tags = []
        for keyword, tags in tech_keywords.items():
            if keyword in combined_text:
                suggested_tags.extend(tags)
        
        # Remove duplicates and limit
        suggested_tags = list(set(suggested_tags))[:limit]
        
        # Verify tags exist in database
        valid_tags = []
        for tag_name in suggested_tags:
            tag = db.session.query(Tag).filter_by(name=tag_name).first()
            if tag:
                valid_tags.append(tag)
        
        return valid_tags
