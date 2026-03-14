from datetime import datetime
import hashlib

def get_timestamp():
    """Get current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def hash_password(password):
    """Hash password using SHA256 (for future enhancement)."""
    return hashlib.sha256(password.encode()).hexdigest()

def truncate_text(text, max_length=100):
    """Truncate text to max length."""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def format_url(url):
    """Format URL for display."""
    if not url:
        return "No URL"
    if len(url) > 50:
        return url[:50] + "..."
    return url

def count_sentences(text):
    """Count sentences in text."""
    return len(text.split('.'))

def estimate_read_time(text):
    """Estimate reading time in minutes."""
    words = len(text.split())
    return max(1, words // 200)  # Assuming 200 words per minute