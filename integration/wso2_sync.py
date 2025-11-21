"""
Script Python fonctionnel qui simule un API Proxy WSO2 Enterprise Integrator
Synchronise les articles entre deux bases de données via l'API REST Flask

Ce script peut être utilisé comme alternative à WSO2 EI ou comme wrapper
pour interagir avec WSO2 si l'outil est installé.
"""
import requests
import sqlite3
import os
import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configuration
SOURCE_DB = os.getenv('WSO2_SOURCE_DB', 'source_articles.db')
DESTINATION_DB = os.getenv('WSO2_DESTINATION_DB', 'destination_articles.db')
REST_API_URL = os.getenv('REST_API_URL', 'http://localhost:5000')
WSO2_PORT = int(os.getenv('WSO2_PROXY_PORT', 8280))
SOURCE_DB_TYPE = os.getenv('SOURCE_DB_TYPE', 'sqlite')
DEST_DB_TYPE = os.getenv('DEST_DB_TYPE', 'sqlite')

app = Flask(__name__)
CORS(app)


def get_connection(db_path: str, db_type: str = 'sqlite'):
    """Obtient une connexion à la base de données"""
    if db_type == 'sqlite':
        return sqlite3.connect(db_path)
    elif db_type == 'mysql':
        import pymysql
        return pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'source_db')
        )
    elif db_type == 'postgresql':
        import psycopg2
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            database=os.getenv('POSTGRES_DATABASE', 'destination_db')
        )
    else:
        raise ValueError(f"Type de base de données non supporté: {db_type}")


def read_from_source_db(last_sync_time: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Récupère les données depuis la base source (Base A)
    Simule la séquence <dbreport> de WSO2
    """
    try:
        conn = get_connection(SOURCE_DB, SOURCE_DB_TYPE)
        conn.row_factory = sqlite3.Row if SOURCE_DB_TYPE == 'sqlite' else None
        cursor = conn.cursor()
        
        if last_sync_time:
            if SOURCE_DB_TYPE == 'sqlite':
                cursor.execute("""
                    SELECT id, title, content, updated_at
                    FROM articles
                    WHERE updated_at > ?
                    ORDER BY updated_at DESC
                """, (last_sync_time,))
            else:
                cursor.execute("""
                    SELECT id, title, content, updated_at
                    FROM articles
                    WHERE updated_at > %s
                    ORDER BY updated_at DESC
                """, (last_sync_time,))
        else:
            cursor.execute("SELECT id, title, content, updated_at FROM articles ORDER BY updated_at DESC")
        
        articles = []
        for row in cursor.fetchall():
            if SOURCE_DB_TYPE == 'sqlite':
                articles.append({
                    'id': row['id'],
                    'title': row['title'],
                    'content': row['content'],
                    'updated_at': row['updated_at']
                })
            else:
                articles.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'updated_at': str(row[3]) if row[3] else None
                })
        
        conn.close()
        return articles
    
    except Exception as e:
        print(f"[ERROR] Erreur lors de la lecture de la base source: {str(e)}")
        return []


def transform_to_json(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforme les données au format JSON
    Simule la séquence <payloadFactory> de WSO2
    """
    transformed = []
    for article in articles:
        transformed.append({
            'title': article.get('title', ''),
            'content': article.get('content', ''),
            'id': article.get('id')
        })
    return transformed


def call_rest_api(article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Appelle l'API REST Flask
    Simule la séquence <call><endpoint> de WSO2
    """
    try:
        article_id = article.get('id')
        
        if article_id:
            # Vérifier si l'article existe
            response = requests.get(f"{REST_API_URL}/articles/{article_id}", timeout=5)
            if response.status_code == 200:
                # Mise à jour
                response = requests.put(
                    f"{REST_API_URL}/articles/{article_id}",
                    json={'title': article['title'], 'content': article['content']},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
            else:
                # Création
                response = requests.post(
                    f"{REST_API_URL}/articles",
                    json={'title': article['title'], 'content': article['content']},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
        else:
            # Création
            response = requests.post(
                f"{REST_API_URL}/articles",
                json={'title': article['title'], 'content': article['content']},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            return None
    
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'appel API REST: {str(e)}")
        return None


def write_to_destination_db(article: Dict[str, Any], api_response: Dict[str, Any]):
    """
    Écrit dans la base de destination (Base B)
    Simule la séquence <dbreport> de WSO2 pour la destination
    """
    try:
        conn = get_connection(DESTINATION_DB, DEST_DB_TYPE)
        cursor = conn.cursor()
        
        article_id = api_response.get('id') or article.get('id')
        title = article.get('title', '')
        content = article.get('content', '')
        
        if DEST_DB_TYPE == 'sqlite':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles_synced (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT OR REPLACE INTO articles_synced (id, title, content, synced_at)
                VALUES (?, ?, ?, ?)
            """, (article_id, title, content, datetime.now()))
        
        elif DEST_DB_TYPE == 'postgresql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles_synced (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    synced_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            cursor.execute("""
                INSERT INTO articles_synced (id, title, content, synced_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    synced_at = EXCLUDED.synced_at
            """, (article_id, title, content, datetime.now()))
        
        elif DEST_DB_TYPE == 'mysql':
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles_synced (
                    id INT PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO articles_synced (id, title, content, synced_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    content = VALUES(content),
                    synced_at = VALUES(synced_at)
            """, (article_id, title, content, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'ecriture dans la base destination: {str(e)}")
        return False


@app.route('/articles-sync', methods=['GET', 'POST'])
def articles_sync():
    """
    API Proxy pour la synchronisation des articles
    Simule l'API Proxy WSO2 définie dans wso2_example.xml
    """
    try:
        # Log de la requête (simule <log> de WSO2)
        print(f"[INFO] Requete recue pour synchronisation: {request.method}")
        
        # Récupération du dernier temps de synchronisation
        last_sync_time = request.args.get('lastSyncTime') or request.json.get('lastSyncTime') if request.is_json else None
        
        # Récupération des données depuis la base source
        articles = read_from_source_db(last_sync_time)
        
        if not articles:
            return jsonify({
                'success': True,
                'message': 'Aucun article a synchroniser',
                'count': 0
            }), 200
        
        # Transformation des données au format JSON
        transformed_articles = transform_to_json(articles)
        
        # Traitement de chaque article
        success_count = 0
        error_count = 0
        results = []
        
        for article in transformed_articles:
            # Appel vers l'API REST Flask
            api_response = call_rest_api(article)
            
            if api_response:
                # Écriture dans la base de destination
                if write_to_destination_db(article, api_response):
                    success_count += 1
                    results.append({
                        'id': api_response.get('id'),
                        'title': article.get('title'),
                        'status': 'synced'
                    })
                else:
                    error_count += 1
            else:
                error_count += 1
        
        # Réponse de succès (simule <respond> de WSO2)
        return jsonify({
            'success': True,
            'message': f'Synchronisation terminee: {success_count} succes, {error_count} erreurs',
            'count': success_count,
            'results': results
        }), 200
    
    except Exception as e:
        # Gestion des erreurs (simule <faultSequence> de WSO2)
        print(f"[ERROR] Erreur lors de la synchronisation: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check pour le proxy WSO2"""
    return jsonify({
        'status': 'healthy',
        'service': 'WSO2 Proxy (simulation)',
        'source_db': SOURCE_DB,
        'destination_db': DESTINATION_DB,
        'rest_api_url': REST_API_URL
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("WSO2 Enterprise Integrator Proxy (simulation Python)")
    print("=" * 60)
    print(f"Base source: {SOURCE_DB} ({SOURCE_DB_TYPE})")
    print(f"Base destination: {DESTINATION_DB} ({DEST_DB_TYPE})")
    print(f"API REST: {REST_API_URL}")
    print(f"Proxy API: http://localhost:{WSO2_PORT}/articles-sync")
    print()
    print("Endpoints disponibles:")
    print(f"  GET/POST http://localhost:{WSO2_PORT}/articles-sync")
    print(f"  GET http://localhost:{WSO2_PORT}/health")
    print()
    print("Exemple d'utilisation:")
    print(f"  curl http://localhost:{WSO2_PORT}/articles-sync")
    print()
    
    app.run(host='0.0.0.0', port=WSO2_PORT, debug=False)

