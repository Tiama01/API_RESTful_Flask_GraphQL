# Architecture du Projet

## 📐 Vue d'ensemble

Ce projet implémente une architecture complète avec plusieurs composants interconnectés :

```
┌─────────────────┐
│   Base A        │
│  (Source DB)    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Intégration                       │
│   (Kafka/Pentaho/WSO2/Script)       │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   API REST Flask                    │
│   - CRUD Articles                   │
│   - Endpoint /metrics (Prometheus)  │
└────────┬────────────────────────────┘
         │
         ├─────────────────┐
         ▼                 ▼
┌─────────────────┐  ┌──────────────┐
│  GraphQL Server │  │  Prometheus  │
│  (Consomme REST)│  │  (Monitoring)│
└─────────────────┘  └──────────────┘
         │
         ▼
┌─────────────────┐
│   Base B        │
│  (Dest DB)      │
└─────────────────┘
```

## Composants

### 1. API REST Flask (`app.py`)

**Rôle**: API principale pour la gestion des articles (CRUD)

**Endpoints**:
- `GET /articles` - Liste tous les articles
- `GET /articles/{id}` - Récupère un article
- `POST /articles` - Crée un article
- `PUT /articles/{id}` - Met à jour un article
- `DELETE /articles/{id}` - Supprime un article
- `GET /metrics` - Métriques Prometheus
- `GET /health` - Health check

**Base de données**: SQLite (`articles.db`)

**Monitoring**: Intégration Prometheus via `prometheus-flask-exporter`

### 2. Serveur GraphQL (`graphql_server.py`)

**Rôle**: Interface GraphQL qui consomme l'API REST

**Schéma GraphQL**:
- **Queries**: `getArticles`, `getArticle(id)`
- **Mutations**: `createArticle`, `updateArticle`, `deleteArticle`

**Communication**: Utilise `requests` pour appeler l'API REST Flask

**Interface**: GraphQL Playground disponible sur `/graphql`

### 3. Module d'Intégration (`integration/`)

**Rôle**: Synchronisation des données entre bases de données

#### 3.1 Kafka Consumer (`kafka_consumer.py`)
- Écoute les messages sur un topic Kafka
- Synchronise les articles vers l'API REST Flask

#### 3.2 Pentaho (`pentaho_example.ktr`)
- Transformation Pentaho Data Integration
- Pipeline: Base A → API REST → Base B

#### 3.3 WSO2 (`wso2_example.xml`)
- Configuration WSO2 Enterprise Integrator
- API Proxy pour la synchronisation

#### 3.4 Script Python (`sync_script.py`)
- Alternative générique aux outils ci-dessus
- Synchronisation programmée ou continue

### 4. Monitoring Prometheus

**Rôle**: Collecte et stockage des métriques

**Configuration**: `prometheus.yml`

**Métriques collectées**:
- Nombre total de requêtes HTTP
- Temps de réponse par endpoint
- Erreurs 4xx et 5xx
- Métriques personnalisées

## Flux de données

### Flux de synchronisation

1. **Source** → Les données sont récupérées depuis la Base A
2. **Transformation** → Les données sont transformées au format JSON
3. **API REST** → Les données sont envoyées à l'API REST Flask (POST/PUT)
4. **GraphQL** → Optionnellement, les données peuvent être consultées via GraphQL
5. **Destination** → Les données sont sauvegardées dans la Base B

### Flux de requête GraphQL

1. **Client GraphQL** → Envoie une requête GraphQL
2. **GraphQL Server** → Traite la requête et appelle le resolver approprié
3. **Resolver** → Appelle l'API REST Flask via HTTP
4. **API REST** → Interroge la base de données SQLite
5. **Réponse** → Retourne les données au client GraphQL

### Flux de monitoring

1. **API REST** → Expose les métriques sur `/metrics`
2. **Prometheus** → Scrape les métriques toutes les 10 secondes
3. **Stockage** → Les métriques sont stockées dans Prometheus
4. **Visualisation** → Optionnellement via Grafana

## Technologies utilisées

- **Backend**: Python 3.8+
- **Framework Web**: Flask
- **GraphQL**: Ariadne
- **Base de données**: SQLite (via SQLAlchemy)
- **Intégration**: Kafka, Pentaho, WSO2
- **Monitoring**: Prometheus
- **HTTP Client**: requests

## Points d'intégration

### Entre GraphQL et REST
- GraphQL appelle REST via HTTP (bibliothèque `requests`)
- URL configurable via variable d'environnement `REST_API_URL`

### Entre Intégration et REST
- Kafka/Pentaho/WSO2/Script appellent REST via HTTP
- Endpoints utilisés: `POST /articles`, `PUT /articles/{id}`

### Entre Prometheus et REST
- Prometheus scrape les métriques depuis `/metrics`
- Configuration dans `prometheus.yml`

## Déploiement

### Développement local
1. Démarrer l'API REST: `python app.py`
2. Démarrer GraphQL: `python graphql_server.py`
3. Démarrer Prometheus: `prometheus --config.file=prometheus.yml`

### Production
- Utiliser un serveur WSGI (Gunicorn, uWSGI) pour Flask
- Configurer un reverse proxy (Nginx)
- Utiliser une base de données PostgreSQL/MySQL au lieu de SQLite
- Configurer Prometheus avec stockage persistant
- Utiliser Docker Compose pour orchestrer les services

## Notes importantes

- L'API REST doit être démarrée avant le serveur GraphQL
- Les métriques Prometheus sont exposées automatiquement
- Les outils d'intégration nécessitent une configuration spécifique selon l'environnement
- Pour la production, remplacer SQLite par une base de données plus robuste

