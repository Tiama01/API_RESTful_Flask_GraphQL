"""
Script Python fonctionnel qui simule une transformation Pentaho Data Integration
Synchronise les articles entre deux bases de données via l'API REST Flask

Ce script peut être utilisé comme alternative à Pentaho PDI ou comme wrapper
pour exécuter des transformations Pentaho si l'outil est installé.
"""
import requests
import sqlite3
import os
import json
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configuration
SOURCE_DB = os.getenv('PENTAHO_SOURCE_DB', 'source_articles.db')
DESTINATION_DB = os.getenv('PENTAHO_DESTINATION_DB', 'destination_articles.db')
REST_API_URL = os.getenv('REST_API_URL', 'http://localhost:5000')
SOURCE_DB_TYPE = os.getenv('SOURCE_DB_TYPE', 'sqlite')  # sqlite, mysql, postgresql
DEST_DB_TYPE = os.getenv('DEST_DB_TYPE', 'sqlite')  # sqlite, mysql, postgresql


def get_connection(db_path: str, db_type: str = 'sqlite'):
    """
    Obtient une connexion à la base de données selon le type
    
    Args:
        db_path: Chemin ou URL de la base de données
        db_type: Type de base (sqlite, mysql, postgresql)
    
    Returns:
        Connexion à la base de données
    """
    if db_type == 'sqlite':
        return sqlite3.connect(db_path)
    elif db_type == 'mysql':
        import pymysql
        # Format attendu: mysql://user:password@host:port/database
        # Pour simplifier, on utilise des variables d'environnement
        return pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'source_db')
        )
    elif db_type == 'postgresql':
        import psycopg2
        # Format attendu: postgresql://user:password@host:port/database
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            database=os.getenv('POSTGRES_DATABASE', 'destination_db')
        )
    else:
        raise ValueError(f"Type de base de données non supporté: {db_type}")


def read_from_source_db() -> List[Dict[str, Any]]:
    """
    Étape 1: Lecture depuis la base de données source (Base A)
    Simule l'étape "Table Input" de Pentaho
    
    Returns:
        Liste des articles à synchroniser
    """
    try:
        conn = get_connection(SOURCE_DB, SOURCE_DB_TYPE)
        conn.row_factory = sqlite3.Row if SOURCE_DB_TYPE == 'sqlite' else None
        cursor = conn.cursor()
        
        # Récupère les articles modifiés récemment (simule WHERE updated_at > ?)
        if SOURCE_DB_TYPE == 'sqlite':
            cursor.execute("""
                SELECT id, title, content, updated_at
                FROM articles
                WHERE updated_at > datetime('now', '-1 hour')
                ORDER BY updated_at DESC
            """)
        else:
            # Pour MySQL/PostgreSQL
            cursor.execute("""
                SELECT id, title, content, updated_at
                FROM articles
                WHERE updated_at > NOW() - INTERVAL 1 HOUR
                ORDER BY updated_at DESC
            """)
        
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
        print(f"[OK] {len(articles)} article(s) lu(s) depuis la base source")
        return articles
    
    except Exception as e:
        print(f"[ERROR] Erreur lors de la lecture de la base source: {str(e)}")
        return []


def transform_data(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Étape 2: Transformation des données
    Simule l'étape "ScriptValueMod" de Pentaho
    Convertit les données au format JSON pour l'API REST
    
    Args:
        articles: Liste des articles bruts
    
    Returns:
        Liste des articles transformés
    """
    transformed = []
    for article in articles:
        # Transformation: prépare les données pour l'API REST
        transformed_article = {
            'title': article.get('title', ''),
            'content': article.get('content', ''),
        }
        # Si l'article a un ID, on l'inclut pour la mise à jour
        if article.get('id'):
            transformed_article['id'] = article['id']
        
        transformed.append(transformed_article)
    
    print(f"[OK] {len(transformed)} article(s) transforme(s)")
    return transformed


def call_rest_api(article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Étape 3: Appel HTTP vers l'API REST Flask
    Simule l'étape "REST Client" de Pentaho
    
    Args:
        article: Données de l'article à synchroniser
    
    Returns:
        Réponse de l'API REST ou None en cas d'erreur
    """
    try:
        article_id = article.get('id')
        
        if article_id:
            # Mise à jour si l'article existe
            response = requests.get(f"{REST_API_URL}/articles/{article_id}", timeout=5)
            if response.status_code == 200:
                # L'article existe, on le met à jour
                response = requests.put(
                    f"{REST_API_URL}/articles/{article_id}",
                    json={'title': article['title'], 'content': article['content']},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
            else:
                # L'article n'existe pas, on le crée
                response = requests.post(
                    f"{REST_API_URL}/articles",
                    json={'title': article['title'], 'content': article['content']},
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
        else:
            # Création d'un nouvel article
            response = requests.post(
                f"{REST_API_URL}/articles",
                json={'title': article['title'], 'content': article['content']},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"[OK] Article synchronise via API REST: {result.get('id', 'N/A')}")
            return result
        else:
            print(f"[ERROR] Erreur API REST: {response.status_code} - {response.text}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Erreur de communication avec l'API REST: {str(e)}")
        return None


def write_to_destination_db(article: Dict[str, Any], api_response: Dict[str, Any]):
    """
    Étape 4: Écriture dans la base de destination (Base B)
    Simule l'étape "Table Output" de Pentaho
    
    Args:
        article: Données de l'article original
        api_response: Réponse de l'API REST
    """
    try:
        conn = get_connection(DESTINATION_DB, DEST_DB_TYPE)
        cursor = conn.cursor()
        
        article_id = api_response.get('id') or article.get('id')
        title = article.get('title', '')
        content = article.get('content', '')
        
        if DEST_DB_TYPE == 'sqlite':
            # Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles_synced (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insérer ou mettre à jour
            cursor.execute("""
                INSERT OR REPLACE INTO articles_synced (id, title, content, synced_at)
                VALUES (?, ?, ?, ?)
            """, (article_id, title, content, datetime.now()))
        
        elif DEST_DB_TYPE == 'postgresql':
            # Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles_synced (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    synced_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Insérer ou mettre à jour
            cursor.execute("""
                INSERT INTO articles_synced (id, title, content, synced_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    synced_at = EXCLUDED.synced_at
            """, (article_id, title, content, datetime.now()))
        
        elif DEST_DB_TYPE == 'mysql':
            # Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles_synced (
                    id INT PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content TEXT NOT NULL,
                    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insérer ou mettre à jour
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
        print(f"[OK] Article ecrit dans la base destination: ID {article_id}")
    
    except Exception as e:
        print(f"[ERROR] Erreur lors de l'ecriture dans la base destination: {str(e)}")


def run_pentaho_transformation():
    """
    Exécute la transformation complète (simule l'exécution d'un fichier .ktr Pentaho)
    """
    print("=" * 60)
    print("Transformation Pentaho (simulation Python)")
    print("=" * 60)
    print(f"Base source: {SOURCE_DB} ({SOURCE_DB_TYPE})")
    print(f"Base destination: {DESTINATION_DB} ({DEST_DB_TYPE})")
    print(f"API REST: {REST_API_URL}")
    print()
    
    # Étape 1: Lecture depuis la base source
    articles = read_from_source_db()
    
    if not articles:
        print("[INFO] Aucun article a synchroniser")
        return
    
    # Étape 2: Transformation des données
    transformed_articles = transform_data(articles)
    
    # Étape 3 et 4: Pour chaque article, appeler l'API REST et écrire dans la destination
    success_count = 0
    error_count = 0
    
    for article in transformed_articles:
        print(f"\nTraitement de l'article: {article.get('title', 'N/A')}")
        
        # Étape 3: Appel API REST
        api_response = call_rest_api(article)
        
        if api_response:
            # Étape 4: Écriture dans la base destination
            write_to_destination_db(article, api_response)
            success_count += 1
        else:
            error_count += 1
    
    print()
    print("=" * 60)
    print(f"Transformation terminee: {success_count} succes, {error_count} erreurs")
    print("=" * 60)


if __name__ == '__main__':
    try:
        run_pentaho_transformation()
    except KeyboardInterrupt:
        print("\nTransformation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n[ERROR] Erreur fatale: {str(e)}")
        sys.exit(1)

