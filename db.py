import sqlite3
import os
from datetime import datetime

DB_PATH = "data/news.db"

def init_db():
    """Initialize database with required tables."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # News articles table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            summary TEXT,
            content TEXT,
            url TEXT UNIQUE,
            source TEXT,
            category TEXT,
            cluster_id INTEGER,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User preferences table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            category TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, password):
    """Add a new user to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def validate_user(username, password):
    """Validate user credentials."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    user = cur.fetchone()
    conn.close()
    return user is not None

def store_articles(articles):
    """Store scraped articles in database."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for article in articles:
        try:
            cur.execute('''
                INSERT INTO articles (headline, content, url, source, category)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                article.get('headline'),
                article.get('content'),
                article.get('url'),
                article.get('source'),
                article.get('category')
            ))
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
    conn.commit()
    conn.close()

def get_articles_by_category(category, limit=50):
    """Retrieve articles by category."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM articles WHERE category=? ORDER BY scraped_at DESC LIMIT ?",
        (category, limit)
    )
    articles = cur.fetchall()
    conn.close()
    return articles

def update_article_summary(article_id, summary, cluster_id):
    """Update article with AI summary and cluster ID."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE articles SET summary=?, cluster_id=? WHERE id=?",
        (summary, cluster_id, article_id)
    )
    conn.commit()
    conn.close()

def clear_old_articles(days=7):
    """Delete articles older than specified days."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM articles WHERE datetime(scraped_at) < datetime('now', '-' || ? || ' days')",
        (days,)
    )
    conn.commit()
    conn.close()