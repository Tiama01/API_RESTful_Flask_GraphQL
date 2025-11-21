# Architecture du Projet

## Vue d'ensemble

Ce projet implémente une architecture complète avec plusieurs composants interconnectés :

```
                   ┌────────────────────────┐
                   │        Utilisateur      │
                   │    (App / Frontend)     │
                   └─────────────┬───────────┘
                                 │ GraphQL Queries
                                 ▼
                     ┌────────────────────────┐
                     │      Serveur GraphQL    │
                     │  (Resolvers → REST API) │
                     └─────────────┬───────────┘
                                   │ Appels REST
                                   ▼
                     ┌────────────────────────┐
                     │     API Flask REST     │
                     │ CRUD Articles / Metrics│
                     └─────────────┬───────────┘
       ┌───────────────────────────┼──────────────────────────────┐
       │                           │                              │
       ▼                           ▼                              ▼

┌─────────────────┐     ┌───────────────────────┐      ┌────────────────────┐
│  WSO2 API        │     │   Apache Kafka        │      │   Prometheus        │
│  Gateway         │     │ (Event Streaming)     │      │ (Monitoring Metrics)│
└────────┬─────────┘     └──────────┬────────────┘      └─────────┬──────────┘
         │ Sécurité / Auth /         │ Publie/consomme événements   │ Scrape /metrics
         │ Throttling / Routing      │ (création, modif, delete)    │ pour dashboards
         ▼                           ▼                              ▼

┌──────────────────────────────┐       ┌──────────────────────────┐
│ Base de données Source (A)   │ <---> │   Pentaho ETL / Kettle   │
└──────────────────────────────┘       └──────────────────────────┘
                                            │ Transformations ETL
                                            ▼
                                ┌──────────────────────────────┐
                                │ Base de données Cible (B)    │
                                └──────────────────────────────┘
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

### 3. WSO2 API Gateway

**Rôle**: Point d'entrée sécurisé et gestion des API

**Fonctionnalités**:
- Sécurité et authentification
- Throttling et limitation de débit
- Routing et load balancing
- Transformation de requêtes/réponses
- Gestion des API Proxies

**Configuration**: `integration/wso2_example.xml` ou `integration/wso2_sync.py`

**Port**: 8280 (HTTP) / 9443 (HTTPS)

### 4. Apache Kafka

**Rôle**: Plateforme de streaming d'événements pour l'intégration

**Fonctionnalités**:
- Publication d'événements (création, modification, suppression d'articles)
- Consommation d'événements pour synchronisation
- Découplage entre producteurs et consommateurs
- Persistance des messages

**Topic**: `articles-sync`

**Script**: `integration/kafka_consumer.py`

**Port**: 9092

### 5. Pentaho ETL / Kettle

**Rôle**: Transformation et synchronisation des données (ETL)

**Fonctionnalités**:
- Extraction depuis la base source (Base A)
- Transformation des données
- Chargement vers la base cible (Base B)
- Pipeline ETL complet

**Configuration**: `integration/pentaho_example.ktr` ou `integration/pentaho_sync.py`

### 6. Module d'Intégration (`integration/`)

**Rôle**: Synchronisation des données entre bases de données

#### 6.1 Kafka Consumer (`kafka_consumer.py`)
- Écoute les messages sur un topic Kafka
- Synchronise les articles vers l'API REST Flask

#### 6.2 Pentaho (`pentaho_example.ktr` / `pentaho_sync.py`)
- Transformation Pentaho Data Integration
- Pipeline: Base A → API REST → Base B
- Script Python fonctionnel disponible

#### 6.3 WSO2 (`wso2_example.xml` / `wso2_sync.py`)
- Configuration WSO2 Enterprise Integrator
- API Proxy pour la synchronisation
- Script Python fonctionnel disponible

#### 6.4 Script Python (`sync_script.py`)
- Alternative générique aux outils ci-dessus
- Synchronisation programmée ou continue

### 7. Monitoring Prometheus

**Rôle**: Collecte et stockage des métriques

**Configuration**: `prometheus.yml`

**Métriques collectées**:
- Nombre total de requêtes HTTP
- Temps de réponse par endpoint
- Erreurs 4xx et 5xx
- Métriques personnalisées

## Flux de données

### Flux de requête utilisateur (via GraphQL)

1. **Utilisateur/Frontend** → Envoie une requête GraphQL
2. **Serveur GraphQL** → Traite la requête et appelle le resolver approprié
3. **Resolver** → Appelle l'API REST Flask via HTTP
4. **API REST** → Interroge la base de données et retourne les données
5. **GraphQL** → Formate et retourne la réponse au client

### Flux de synchronisation via WSO2 Gateway

1. **Base Source (A)** → Les données sont récupérées
2. **WSO2 API Gateway** → Applique sécurité, authentification, throttling
3. **API REST Flask** → Reçoit les requêtes via le gateway
4. **Traitement** → CRUD des articles
5. **Base Cible (B)** → Les données sont sauvegardées

### Flux de streaming d'événements (Kafka)

1. **Événements** → Publication d'événements (création, modification, suppression)
2. **Kafka** → Stockage et distribution des événements
3. **Consumer** → Consommation des événements depuis Kafka
4. **API REST** → Synchronisation via l'API REST Flask
5. **Base Cible (B)** → Mise à jour de la base de destination

### Flux ETL (Pentaho)

1. **Base Source (A)** → Extraction des données
2. **Pentaho ETL** → Transformation des données (ETL)
3. **API REST** → Appel de l'API REST Flask pour validation
4. **Base Cible (B)** → Chargement des données transformées

### Flux de monitoring

1. **API REST** → Expose les métriques sur `/metrics`
2. **Prometheus** → Scrape les métriques toutes les 10 secondes
3. **Stockage** → Les métriques sont stockées dans Prometheus
4. **Visualisation** → Dashboards via Prometheus UI ou Grafana

## Technologies utilisées

- **Backend**: Python 3.8+
- **Framework Web**: Flask
- **GraphQL**: Ariadne
- **Base de données**: SQLite (via SQLAlchemy), support MySQL/PostgreSQL
- **API Gateway**: WSO2 Enterprise Integrator
- **Event Streaming**: Apache Kafka
- **ETL**: Pentaho Data Integration (Kettle)
- **Monitoring**: Prometheus
- **HTTP Client**: requests

## Points d'intégration

### Entre Utilisateur et GraphQL
- Interface GraphQL Playground pour les requêtes
- Endpoint: `http://localhost:8000/graphql`
- Support des queries et mutations

### Entre GraphQL et REST
- GraphQL appelle REST via HTTP (bibliothèque `requests`)
- URL configurable via variable d'environnement `REST_API_URL`
- Découplage entre interface GraphQL et implémentation REST

### Entre WSO2 Gateway et REST
- WSO2 Gateway route les requêtes vers l'API REST Flask
- Applique sécurité, authentification, throttling
- Port: 8280 (HTTP) / 9443 (HTTPS)

### Entre Kafka et REST
- Kafka publie des événements d'articles
- Consumer Kafka appelle REST via HTTP
- Endpoints utilisés: `POST /articles`, `PUT /articles/{id}`, `DELETE /articles/{id}`
- Topic: `articles-sync`

### Entre Pentaho ETL et REST
- Pentaho extrait depuis Base A, transforme, appelle REST, charge dans Base B
- Appels HTTP vers l'API REST pour validation
- Support SQLite, MySQL, PostgreSQL

### Entre Prometheus et REST
- Prometheus scrape les métriques depuis `/metrics`
- Configuration dans `prometheus.yml`
- Intervalle de scraping: 10 secondes

## Déploiement

### Développement local

**Option 1 : Script automatique (recommandé)**
```bash
./start.sh all
```

**Option 2 : Démarrage manuel**
1. Démarrer l'API REST: `python app.py`
2. Démarrer GraphQL: `python graphql_server.py`
3. Démarrer Prometheus: `prometheus --config.file=prometheus.yml`
4. Démarrer Kafka (optionnel): `./start.sh kafka`
5. Démarrer WSO2 (optionnel): `python integration/wso2_sync.py`
6. Démarrer Pentaho (optionnel): `python integration/pentaho_sync.py`

### Production
- Utiliser un serveur WSGI (Gunicorn, uWSGI) pour Flask
- Configurer WSO2 API Gateway pour la sécurité et le routing
- Utiliser Kafka en cluster pour la haute disponibilité
- Utiliser une base de données PostgreSQL/MySQL au lieu de SQLite
- Configurer Prometheus avec stockage persistant
- Utiliser Docker Compose pour orchestrer tous les services
- Configurer Grafana pour la visualisation des métriques

## Notes importantes

- **Ordre de démarrage** : L'API REST doit être démarrée avant le serveur GraphQL
- **WSO2 Gateway** : Peut être utilisé comme point d'entrée unique pour toutes les API
- **Kafka** : Nécessite Zookeeper pour fonctionner
- **Pentaho** : Peut être utilisé avec les fichiers `.ktr` ou le script Python `pentaho_sync.py`
- **WSO2** : Peut être utilisé avec les fichiers `.xml` ou le script Python `wso2_sync.py`
- **Monitoring** : Les métriques Prometheus sont exposées automatiquement sur `/metrics`
- **Bases de données** : Pour la production, remplacer SQLite par PostgreSQL ou MySQL
- **Sécurité** : Configurer l'authentification et l'autorisation via WSO2 Gateway en production
- **Haute disponibilité** : Utiliser des clusters pour Kafka, WSO2 et les bases de données en production

