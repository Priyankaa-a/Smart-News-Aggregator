from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def vectorize_articles(articles):
    """Convert article headlines to TF-IDF vectors."""
    headlines = [a.get('headline', '') for a in articles if a.get('headline')]
    
    if len(headlines) < 2:
        return None, None
    
    try:
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            min_df=1,
            max_df=0.95,
            ngram_range=(1, 2)
        )
        
        X = vectorizer.fit_transform(headlines)
        return X, vectorizer
    except Exception as e:
        print(f"❌ Error vectorizing: {e}")
        return None, None

def cluster_articles(articles, n_clusters=None):
    """Cluster similar articles together using K-Means."""
    if len(articles) < 2:
        return {0: articles}
    
    # Auto-decide number of clusters
    if n_clusters is None:
        n_clusters = min(5, max(2, len(articles) // 4))
    
    X, vectorizer = vectorize_articles(articles)
    
    if X is None:
        return {0: articles}
    
    try:
        kmeans = KMeans(
            n_clusters=min(n_clusters, len(articles)),
            random_state=42,
            n_init=10,
            max_iter=300
        )
        clusters = kmeans.fit_predict(X)
        
        # Group articles by cluster
        grouped = {}
        for idx, cluster_id in enumerate(clusters):
            cluster_id = int(cluster_id)
            if cluster_id not in grouped:
                grouped[cluster_id] = []
            grouped[cluster_id].append({**articles[idx], 'cluster_id': cluster_id})
        
        return grouped
    except Exception as e:
        print(f"❌ Error clustering: {e}")
        return {0: articles}

def get_top_article_per_cluster(grouped_articles):
    """Select the longest (most detailed) article from each cluster."""
    top_articles = {}
    for cluster_id, articles in grouped_articles.items():
        # Pick article with longest content
        top_article = max(
            articles,
            key=lambda a: len(a.get('content', ''))
        )
        top_articles[cluster_id] = top_article
    
    return top_articles

def similarity_score(text1, text2):
    """Calculate cosine similarity between two texts."""
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        vectors = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return similarity
    except:
        return 0