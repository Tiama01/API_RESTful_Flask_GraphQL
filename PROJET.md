# Projet : API RESTful Flask + Client GraphQL + Intégration + Monitoring

## Sujet du Projet

**Création d'une API RESTful avec Flask et Consommation avec GraphQL**

### Objectif
Apprendre à créer une API RESTful avec Flask et à consommer cette API avec GraphQL. Via Pentaho Data Integration/WSO2/Kafka pour se connecter/synchroniser entre deux bases de données.

### Tâches

1. **Créer une API RESTful pour gérer des articles de blog avec Flask**
   - Configurer un projet Flask pour l'API RESTful
   - Implémenter les endpoints REST pour les articles de blog (CRUD)

2. **Créer une application client GraphQL pour consommer l'API RESTful**
   - Afficher les articles via GraphQL
   - Consommer l'API RESTful Flask

3. **Intégration pour la synchronisation entre bases de données**
   - Utiliser Pentaho Data Integration / WSO2 / Kafka
   - Se connecter et synchroniser entre deux bases de données

4. **Monitoring avec Prometheus**
   - Surveiller les performances du service
   - Exposer les métriques de l'API

## Réalisation du Projet

### 1. API RESTful Flask

**Fichiers principaux :**
- `app.py` : Application Flask principale avec tous les endpoints REST
- `models.py` : Modèles de données (Article) avec SQLAlchemy
- `requirements.txt` : Dépendances Python

**Endpoints implémentés :**
- `GET /articles` - Liste tous les articles
- `GET /articles/{id}` - Récupère un article par ID
- `POST /articles` - Crée un nouvel article
- `PUT /articles/{id}` - Met à jour un article
- `DELETE /articles/{id}` - Supprime un article
- `GET /health` - Health check
- `GET /metrics` - Métriques Prometheus

**Base de données :**
- SQLite (fichier `articles.db`)
- Modèle `Article` avec champs : `id`, `title`, `content`

### 2. Client GraphQL

**Fichiers principaux :**
- `graphql_server.py` : Serveur GraphQL utilisant Ariadne
- `graphql_schema.py` : Définition du schéma GraphQL
- `graphql_resolvers.py` : Resolvers qui appellent l'API REST Flask

**Fonctionnalités :**
- GraphQL Playground accessible sur `http://localhost:8000/graphql`
- Queries : `getArticles`, `getArticle(id)`
- Mutations : `createArticle`, `updateArticle`, `deleteArticle`
- Chaque resolver fait un appel HTTP à l'API REST Flask

**Schéma GraphQL :**
```graphql
type Article {
    id: Int!
    title: String!
    content: String!
}

type Query {
    getArticles: ArticlesResponse!
    getArticle(id: Int!): ArticleResponse!
}

type Mutation {
    createArticle(title: String!, content: String!): ArticleResponse!
    updateArticle(id: Int!, title: String, content: String): ArticleResponse!
    deleteArticle(id: Int!): DeleteResponse!
}
```

### 3. Intégration pour Synchronisation

**Module d'intégration :** `integration/`

**Fichiers implémentés :**

1. **Kafka** (`kafka_consumer.py`)
   - Consumer Kafka qui écoute les messages
   - Synchronise les articles vers l'API REST Flask
   - Topic : `articles-sync`

2. **Pentaho Data Integration** (`pentaho_example.ktr`)
   - Fichier de transformation Pentaho
   - Pipeline : Base A → API REST → Base B
   - Exemple de configuration pour synchronisation

3. **WSO2 Enterprise Integrator** (`wso2_example.xml`)
   - Configuration WSO2 API Proxy
   - Synchronisation entre bases de données via l'API REST

4. **Script Python générique** (`sync_script.py`)
   - Alternative aux outils d'intégration
   - Synchronise les données entre deux bases SQLite via l'API REST

**Flux de synchronisation :**
```
Base de données A → [Kafka/Pentaho/WSO2] → API REST Flask → Base de données B
```

### 4. Monitoring avec Prometheus

**Configuration :**
- `prometheus.yml` : Configuration Prometheus pour scraper les métriques
- Endpoint `/metrics` dans l'API Flask
- Utilisation de `prometheus-flask-exporter`

**Métriques exposées :**
- `flask_http_request_total` - Nombre total de requêtes HTTP
- `flask_http_request_duration_seconds` - Temps de réponse par endpoint
- `flask_http_request_exceptions_total` - Erreurs (4xx, 5xx)
- Métriques par méthode HTTP (GET, POST, PUT, DELETE)
- Métriques par endpoint et code de statut

**Accès :**
- Prometheus UI : `http://localhost:9090`
- Métriques Flask : `http://localhost:5000/metrics`

## Architecture du Projet

```
┌─────────────────┐
│   Base A        │
│  (Source)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Kafka/Pentaho  │
│     /WSO2       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  API REST Flask │◄─────┤  GraphQL Server  │
│   (Port 5000)   │      │   (Port 8000)     │
└────────┬────────┘      └──────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   Base B        │      │   Prometheus      │
│ (Destination)   │      │   (Port 9090)     │
└─────────────────┘      └──────────────────┘
```

## Technologies Utilisées

- **Flask** : Framework web Python pour l'API REST
- **SQLAlchemy** : ORM pour la gestion de la base de données
- **Ariadne** : Bibliothèque GraphQL pour Python
- **Prometheus** : Système de monitoring et métriques
- **Kafka** : Plateforme de streaming pour l'intégration
- **Pentaho Data Integration** : Outil ETL pour la synchronisation
- **WSO2 Enterprise Integrator** : Plateforme d'intégration

## Installation et Exécution

Voir le fichier `README.md` pour les instructions détaillées d'installation et d'exécution.

## Résultats et Apprentissages

Ce projet permet d'apprendre :

1. ✅ Création d'une API RESTful complète avec Flask
2. ✅ Implémentation des opérations CRUD
3. ✅ Consommation d'une API REST via GraphQL
4. ✅ Configuration et utilisation de Prometheus pour le monitoring
5. ✅ Intégration de données avec Kafka, Pentaho et WSO2
6. ✅ Synchronisation entre bases de données via une API REST
7. ✅ Architecture microservices et communication entre services

## Structure du Projet

```
.
├── app.py                    # API REST Flask
├── models.py                 # Modèles de données
├── graphql_server.py          # Serveur GraphQL
├── graphql_schema.py          # Schéma GraphQL
├── graphql_resolvers.py       # Resolvers GraphQL
├── prometheus.yml             # Configuration Prometheus
├── requirements.txt           # Dépendances Python
├── setup.sh / setup.bat       # Scripts de configuration
├── start.sh                   # Script de démarrage
├── integration/              # Module d'intégration
│   ├── kafka_consumer.py
│   ├── pentaho_example.ktr
│   ├── wso2_example.xml
│   └── sync_script.py
└── README.md                  # Documentation principale
```

