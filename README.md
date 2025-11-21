# API RESTful Flask + Client GraphQL + Intégration + Monitoring Prometheus

## Description

**Sujet du projet :** Création d'une API RESTful avec Flask et Consommation avec GraphQL

**Objectif :** Apprendre à créer une API RESTful avec Flask et à consommer cette API avec GraphQL. Via Pentaho Data Integration/WSO2/Kafka pour se connecter/synchroniser entre deux bases de données.

Projet complet incluant :
- API RESTful Flask pour la gestion d'articles de blog (CRUD)
- Serveur GraphQL consommant l'API REST
- Module d'intégration (Kafka/Pentaho/WSO2) pour synchronisation entre bases de données
- Monitoring avec Prometheus pour surveiller les performances du service

## Installation

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

1. Cloner ou télécharger le projet

2. Créer et configurer l'environnement virtuel :
```bash
# Option 1: Utiliser le script de configuration (recommandé)
chmod +x setup.sh
./setup.sh

# Option 2: Configuration manuelle
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. Activer l'environnement virtuel (si pas déjà fait) :
```bash
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

4. Configurer les variables d'environnement (optionnel) :
```bash
cp .env.example .env
```

**Note**: N'oubliez pas d'activer l'environnement virtuel avant d'exécuter les scripts Python !

## Exécution

### Option 1 : Script de démarrage automatique (Recommandé)

Le script `start.sh` permet de démarrer tous les services automatiquement :

```bash
# Démarrer tous les services
./start.sh all

# Ou simplement (all est la valeur par défaut)
./start.sh
```

**Options disponibles :**
- `./start.sh rest` - Démarrer uniquement l'API REST Flask
- `./start.sh graphql` - Démarrer uniquement le serveur GraphQL
- `./start.sh prometheus` - Démarrer uniquement Prometheus
- `./start.sh kafka` - Démarrer Zookeeper et Kafka
- `./start.sh consumer` - Démarrer le Kafka Consumer
- `./start.sh all` - Démarrer tous les services (défaut)

Le script :
- Active automatiquement l'environnement virtuel
- Détecte et démarre Prometheus si installé
- Détecte et démarre Kafka/Zookeeper si installés
- Vérifie que les ports sont disponibles
- Attend que les services soient prêts
- Gère proprement l'arrêt de tous les services (Ctrl+C)
- Enregistre les logs dans le dossier `logs/`

**Pour arrêter tous les services :**
Appuyez sur `Ctrl+C` dans le terminal où `start.sh` est lancé.

### Option 2 : Démarrage manuel

**Important**: Assurez-vous que l'environnement virtuel est activé :
```bash
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

#### 1. Démarrer l'API REST Flask

```bash
python app.py
```

L'API sera accessible sur `http://localhost:5000`

#### 2. Démarrer le serveur GraphQL

Dans un autre terminal (avec l'environnement virtuel activé) :
```bash
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
python graphql_server.py
```

Le serveur GraphQL sera accessible sur `http://localhost:8000/graphql`

#### 3. Démarrer Prometheus (optionnel)

```bash
prometheus --config.file=prometheus.yml
```

Prometheus sera accessible sur `http://localhost:9090`

#### 4. Démarrer Kafka (optionnel, pour l'intégration)

**Option 1 : Utiliser le script automatique**
```bash
# Démarrer Kafka (Zookeeper + Kafka)
./start.sh kafka

# Démarrer le consumer
./start.sh consumer
```

**Option 2 : Démarrage manuel**
```bash
# Démarrer Zookeeper
zookeeper-server-start.sh config/zookeeper.properties

# Démarrer Kafka
kafka-server-start.sh config/server.properties

# Lancer le consumer d'intégration
python integration/kafka_consumer.py
```

**Guides d'installation :**
- **Kafka** : Consultez [KAFKA_SETUP.md](KAFKA_SETUP.md) pour les instructions détaillées
- **Pentaho** : Consultez [PENTAHO_SETUP.md](PENTAHO_SETUP.md) pour l'installation de Pentaho Data Integration
- **WSO2** : Consultez [WSO2_SETUP.md](WSO2_SETUP.md) pour l'installation de WSO2 Enterprise Integrator

## Endpoints API REST

### Articles

- `GET /articles` - Liste tous les articles
- `GET /articles/{id}` - Récupère un article par ID
- `POST /articles` - Crée un nouvel article
  ```json
  {
    "title": "Mon article",
    "content": "Contenu de l'article"
  }
  ```
- `PUT /articles/{id}` - Met à jour un article
- `DELETE /articles/{id}` - Supprime un article

### Monitoring

- `GET /metrics` - Métriques Prometheus

## Requêtes GraphQL

### Query

```graphql
query {
  getArticles {
    id
    title
    content
  }
}

query {
  getArticle(id: 1) {
    id
    title
    content
  }
}
```

### Mutation

```graphql
mutation {
  createArticle(title: "Nouvel article", content: "Contenu") {
    id
    title
    content
  }
}

mutation {
  updateArticle(id: 1, title: "Titre modifié", content: "Contenu modifié") {
    id
    title
    content
  }
}

mutation {
  deleteArticle(id: 1) {
    success
    message
  }
}
```

## Monitoring Prometheus

Les métriques sont exposées sur `/metrics` et incluent :
- `http_requests_total` - Nombre total de requêtes
- `http_request_duration_seconds` - Temps de réponse par endpoint
- `http_requests_4xx_total` - Erreurs 4xx
- `http_requests_5xx_total` - Erreurs 5xx

## Intégration

Le dossier `integration/` contient :
- `kafka_consumer.py` - Consumer Kafka pour synchronisation
- `pentaho_example.ktr` - Exemple de transformation Pentaho
- `wso2_example.xml` - Exemple de configuration WSO2
- `sync_script.py` - Script Python de synchronisation

## Structure du projet

```
.
├── app.py                 # Application Flask principale
├── models.py              # Modèles de données
├── graphql_server.py      # Serveur GraphQL
├── graphql_schema.py      # Schéma GraphQL
├── graphql_resolvers.py   # Resolvers GraphQL
├── prometheus.yml         # Configuration Prometheus
├── requirements.txt       # Dépendances Python
├── setup.sh               # Script de configuration (Linux/macOS)
├── setup.bat              # Script de configuration (Windows)
├── start.sh               # Script de démarrage des services
├── integration/           # Module d'intégration
│   ├── kafka_consumer.py
│   ├── pentaho_example.ktr
│   ├── wso2_example.xml
│   ├── sync_script.py
│   └── README.md
├── README.md              # Documentation principale
├── ARCHITECTURE.md        # Documentation de l'architecture
├── KAFKA_SETUP.md         # Guide d'installation Kafka
└── prometheus_guide.md     # Guide Prometheus
```

## Tests

Pour tester l'API REST :
```bash
curl http://localhost:5000/articles
```

Pour tester GraphQL :
```bash
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ getArticles { id title content } }"}'
```

## Notes

- La base de données utilise SQLite par défaut (fichier `articles.db`)
- Les métriques Prometheus sont collectées automatiquement
- L'intégration Kafka nécessite un serveur Kafka en cours d'exécution

