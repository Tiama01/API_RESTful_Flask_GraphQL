"""
Script Python de synchronisation générique
Peut être utilisé comme alternative à Pentaho/WSO2/Kafka
Synchronise les données entre deux bases de données via l'API REST Flask
"""
import requests
import sqlite3
import os
import time
from typing import List, Dict, Any

# Configuration
SOURCE_DB = os.getenv('SOURCE_DB', 'source_articles.db')
DESTINATION_DB = os.getenv('DESTINATION_DB', 'destination_articles.db')
REST_API_URL = os.getenv('REST_API_URL', 'http://localhost:5000')
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', 60))  # secondes


def get_articles_from_source() -> List[Dict[str, Any]]:
    """
    Récupère les articles depuis la base de données source (Base A)
    
    Returns:
        Liste des articles à synchroniser
    """
    try:
        conn = sqlite3.connect(SOURCE_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupère les articles modifiés récemment
        cursor.execute("""
            SELECT id, title, content, updated_at
            FROM articles
            WHERE updated_at > datetime('now', '-1 hour')
            ORDER BY updated_at DESC
        """)
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row['id'],
                'title': row['title'],
                'content': row['content'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        return articles
    
    except sqlite3.Error as e:
        print(f"[ERROR] Erreur lors de la lecture de la base source: {str(e)}")
        return []


def sync_article_to_rest_api(article: Dict[str, Any]) -> bool:
    """
    Synchronise un article vers l'API REST Flask
    
    Args:
        article: Données de l'article
    
    Returns:
        True si la synchronisation a réussi, False sinon
    """
    try:
        article_id = article.get('id')
        payload = {
            'title': article['title'],
            'content': article['content']
        }
        
        # Vérifie si l'article existe déjà
        response = requests.get(f"{REST_API_URL}/articles/{article_id}", timeout=5)
        
        if response.status_code == 200:
            # Mise à jour
            response = requests.put(
                f"{REST_API_URL}/articles/{article_id}",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code == 200:
                print(f"[OK] Article {article_id} mis a jour")
                return True
        elif response.status_code == 404:
            # Création
            response = requests.post(
                f"{REST_API_URL}/articles",
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code == 201:
                print(f"[OK] Nouvel article cree (ID: {article_id})")
                return True
        
        print(f"[ERROR] Erreur lors de la synchronisation de l'article {article_id}")
        return False
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Erreur de communication avec l'API REST: {str(e)}")
        return False


def save_to_destination_db(article: Dict[str, Any]) -> bool:
    """
    Sauvegarde l'article dans la base de données de destination (Base B)
    
    Args:
        article: Données de l'article
    
    Returns:
        True si la sauvegarde a réussi, False sinon
    """
    try:
        conn = sqlite3.connect(DESTINATION_DB)
        cursor = conn.cursor()
        
        # Crée la table si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles_synced (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insère ou met à jour l'article
        cursor.execute("""
            INSERT OR REPLACE INTO articles_synced (id, title, content, synced_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (article['id'], article['title'], article['content']))
        
        conn.commit()
        conn.close()
        return True
    
    except sqlite3.Error as e:
        print(f"[ERROR] Erreur lors de l'ecriture dans la base destination: {str(e)}")
        return False


def sync_articles():
    """
    Fonction principale de synchronisation
    Récupère les articles depuis la base A, les envoie à l'API REST,
    puis les sauvegarde dans la base B
    """
    print(f"Demarrage de la synchronisation...")
    print(f"Base source: {SOURCE_DB}")
    print(f"Base destination: {DESTINATION_DB}")
    print(f"API REST: {REST_API_URL}\n")
    
    # Récupération des articles depuis la base source
    articles = get_articles_from_source()
    
    if not articles:
        print("[INFO] Aucun article a synchroniser")
        return
    
    print(f"{len(articles)} article(s) a synchroniser\n")
    
    success_count = 0
    error_count = 0
    
    for article in articles:
        print(f"Synchronisation de l'article {article['id']}: {article['title']}")
        
        # Synchronisation vers l'API REST
        if sync_article_to_rest_api(article):
            # Sauvegarde dans la base de destination
            if save_to_destination_db(article):
                success_count += 1
            else:
                error_count += 1
        else:
            error_count += 1
        
        print()  # Ligne vide pour la lisibilité
    
    print(f"[OK] Synchronisation terminee: {success_count} succes, {error_count} erreurs")


def run_continuous_sync():
    """
    Lance la synchronisation en mode continu
    Synchronise toutes les X secondes (défini par SYNC_INTERVAL)
    """
    print(f"Mode synchronisation continue (intervalle: {SYNC_INTERVAL}s)")
    print("Appuyez sur Ctrl+C pour arreter\n")
    
    try:
        while True:
            sync_articles()
            print(f"Prochaine synchronisation dans {SYNC_INTERVAL} secondes...\n")
            time.sleep(SYNC_INTERVAL)
    
    except KeyboardInterrupt:
        print("\nArret de la synchronisation")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # Mode continu
        run_continuous_sync()
    else:
        # Mode unique
        sync_articles()

