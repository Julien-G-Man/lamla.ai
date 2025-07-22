#!/usr/bin/env python3
"""
Performance optimization script for Django application
"""
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtech_project.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def create_database_indexes():
    """Create performance indexes"""
    cursor = connection.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_quiz_session_user_created ON slides_analyzer_quizsession(user_id, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_exam_analysis_user_created ON slides_analyzer_examanalysis(user_id, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_question_cache_hash ON slides_analyzer_questioncache(question_content_hash);",
        "CREATE INDEX IF NOT EXISTS idx_question_cache_used ON slides_analyzer_questioncache(last_used DESC);",
        "CREATE INDEX IF NOT EXISTS idx_contact_created ON slides_analyzer_contact(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_subscription_active ON slides_analyzer_subscription(is_active, created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_userprofile_user ON slides_analyzer_userprofile(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_chat_message_session ON slides_analyzer_chatmessage(session_id, created_at);",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            print(f"✓ Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
        except Exception as e:
            print(f"✗ Failed to create index: {e}")
    
    connection.commit()

def create_cache_table():
    """Create cache table for database caching"""
    try:
        execute_from_command_line(['manage.py', 'createcachetable'])
        print("✓ Cache table created")
    except Exception as e:
        print(f"Cache table creation: {e}")

def collect_static_files():
    """Collect and compress static files"""
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✓ Static files collected and compressed")
    except Exception as e:
        print(f"Static files collection: {e}")

if __name__ == "__main__":
    print("Running performance optimizations...")
    
    print("\n1. Creating database indexes...")
    create_database_indexes()
    
    print("\n2. Creating cache table...")
    create_cache_table()
    
    print("\n3. Collecting static files...")
    collect_static_files()
    
    print("\n✓ Performance optimization complete!")
