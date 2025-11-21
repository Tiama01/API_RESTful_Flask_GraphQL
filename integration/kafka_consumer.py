"""
Consumer Kafka pour la synchronisation des articles
Récupère les messages depuis Kafka et synchronise avec l'API REST Flask
"""
from kafka import KafkaConsumer
import requests
import json
import os
import time

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'http://localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'articles-sync')
REST_API_URL = os.getenv('REST_API_URL', 'http://localhost:5000')
GROUP_ID = 'articles-sync-consumer'


def sync_article_to_rest_api(article_data: dict):
    """
    Synchronise un article vers l'API REST Flask
    
    Args:
        article_data: Données de l'article à synchroniser
    """
    try:
        # Vérifier si l'article existe déjà
        article_id = article_data.get('id')
        if article_id:
            # Mise à jour si l'article existe
            response = requests.get(f"{REST_API_URL}/articles/{article_id}", timeout=5)
            if response.status_code == 200:
                # Article existe, on le met à jour
                response = requests.put(
                    f"{REST_API_URL}/articles/{article_id}",
                    json=article_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                if response.status_code == 200:
                    print(f"[OK] Article {article_id} mis a jour avec succes")
                else:
                    print(f"[ERROR] Erreur lors de la mise a jour de l'article {article_id}: {response.status_code}")
            else:
                # Article n'existe pas, on le crée
                response = requests.post(
                    f"{REST_API_URL}/articles",
                    json=article_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                if response.status_code == 201:
                    print(f"[OK] Nouvel article cree avec succes")
                else:
                    print(f"[ERROR] Erreur lors de la creation de l'article: {response.status_code}")
        else:
            # Création d'un nouvel article sans ID
            response = requests.post(
                f"{REST_API_URL}/articles",
                json=article_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code == 201:
                if response.status_code == 201:
                    print(f"[OK] Nouvel article cree avec succes")
                else:
                    print(f"[ERROR] Erreur lors de la creation de l'article: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Erreur lors de la synchronisation: {str(e)}")


def start_kafka_consumer():
    """
    Démarre le consumer Kafka et écoute les messages
    """
    print(f"Demarrage du consumer Kafka...")
    print(f"Serveur Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"Topic: {KAFKA_TOPIC}")
    print(f"API REST: {REST_API_URL}")
    
    try:
        # Création du consumer
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',  # Commence depuis le début si pas de commit
            enable_auto_commit=True,
            consumer_timeout_ms=1000  # Timeout pour permettre l'interruption
        )
        
        print("[OK] Consumer Kafka connecte avec succes")
        print("En attente de messages...\n")
        
        # Écoute des messages
        for message in consumer:
            try:
                article_data = message.value
                print(f"Message recu: {json.dumps(article_data, indent=2)}")
                
                # Synchronisation vers l'API REST
                sync_article_to_rest_api(article_data)
                
            except json.JSONDecodeError as e:
                print(f"[ERROR] Erreur de decodage JSON: {str(e)}")
            except Exception as e:
                print(f"[ERROR] Erreur lors du traitement du message: {str(e)}")
    
    except Exception as e:
        print(f"[ERROR] Erreur de connexion a Kafka: {str(e)}")
        print("[INFO] Assurez-vous que Kafka est demarre et accessible")


def produce_test_message():
    """
    Fonction utilitaire pour produire un message de test
    Nécessite un producer Kafka
    """
    from kafka import KafkaProducer
    
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    test_article = {
        'title': 'Article depuis Kafka',
        'content': 'Ceci est un article synchronisé depuis Kafka'
    }
    
    producer.send(KAFKA_TOPIC, test_article)
    producer.flush()
    print(f"[OK] Message de test envoye sur le topic {KAFKA_TOPIC}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Mode test: envoie un message de test
        produce_test_message()
    else:
        # Mode normal: démarre le consumer
        try:
            start_kafka_consumer()
        except KeyboardInterrupt:
            print("\nArret du consumer Kafka")

