# Module d'Intégration

Ce module contient les exemples et scripts pour la synchronisation des données entre deux bases de données via l'API REST Flask.

## Fichiers

### 1. `kafka_consumer.py`
Consumer Kafka qui écoute les messages sur un topic et synchronise les articles vers l'API REST Flask.

**Utilisation:**
```bash
# Démarrer le consumer
python integration/kafka_consumer.py

# Envoyer un message de test
python integration/kafka_consumer.py test
```

**Configuration:**
- `KAFKA_BOOTSTRAP_SERVERS`: Serveurs Kafka (défaut: localhost:9092)
- `KAFKA_TOPIC`: Topic Kafka (défaut: articles-sync)
- `REST_API_URL`: URL de l'API REST Flask

### 2. `pentaho_example.ktr` et `pentaho_sync.py`

**pentaho_example.ktr** : Fichier de configuration Pentaho Data Integration (PDI)
- Template XML pour Pentaho PDI
- Nécessite Pentaho Data Integration installé séparément
- Ouvrir dans Pentaho PDI, configurer les connexions, exécuter

**pentaho_sync.py** : Script Python fonctionnel qui simule Pentaho PDI
- Alternative fonctionnelle qui reproduit le comportement de Pentaho
- Exécutable directement sans installation de Pentaho
- Supporte SQLite, MySQL et PostgreSQL

**Utilisation du script Python:**
```bash
# Utilisation basique (SQLite)
python integration/pentaho_sync.py

# Avec variables d'environnement
export PENTAHO_SOURCE_DB=source.db
export PENTAHO_DESTINATION_DB=dest.db
export REST_API_URL=http://localhost:5000
python integration/pentaho_sync.py

# Pour MySQL/PostgreSQL, configurer les variables d'environnement
export SOURCE_DB_TYPE=mysql
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=password
export MYSQL_DATABASE=source_db
python integration/pentaho_sync.py
```

### 3. `wso2_example.xml` et `wso2_sync.py`

**wso2_example.xml** : Configuration WSO2 Enterprise Integrator (EI)
- Template XML pour WSO2 EI
- Nécessite WSO2 Enterprise Integrator installé séparément
- Déployer dans WSO2 EI, configurer les Data Sources, appeler l'API

**wso2_sync.py** : Script Python fonctionnel qui simule WSO2 EI
- Alternative fonctionnelle qui reproduit le comportement de WSO2
- Crée un serveur Flask qui agit comme un API Proxy
- Supporte SQLite, MySQL et PostgreSQL

**Utilisation du script Python:**
```bash
# Démarrer le proxy WSO2 (simulation)
python integration/wso2_sync.py

# Le proxy sera accessible sur http://localhost:8280/articles-sync

# Appeler l'API de synchronisation
curl http://localhost:8280/articles-sync

# Avec paramètre de dernière synchronisation
curl "http://localhost:8280/articles-sync?lastSyncTime=2024-01-01T00:00:00"

# Health check
curl http://localhost:8280/health
```

### 4. `sync_script.py`
Script Python générique de synchronisation qui peut être utilisé comme alternative aux outils ci-dessus.

**Utilisation:**
```bash
# Synchronisation unique
python integration/sync_script.py

# Synchronisation continue (toutes les 60 secondes)
python integration/sync_script.py --continuous
```

**Configuration:**
- `SOURCE_DB`: Base de données source (défaut: source_articles.db)
- `DESTINATION_DB`: Base de données destination (défaut: destination_articles.db)
- `REST_API_URL`: URL de l'API REST Flask
- `SYNC_INTERVAL`: Intervalle de synchronisation en secondes (défaut: 60)

## Flux de synchronisation

```
Base A (Source) → [Kafka/Pentaho/WSO2/Script] → API REST Flask → Base B (Destination)
```

1. **Récupération**: Les données sont récupérées depuis la base de données source (Base A)
2. **Transformation**: Les données sont transformées au format attendu par l'API REST
3. **API REST**: Les données sont envoyées à l'API REST Flask (POST/PUT)
4. **Sauvegarde**: Les données sont sauvegardées dans la base de données de destination (Base B)

## Notes

- Tous les outils nécessitent que l'API REST Flask soit démarrée et accessible
- Les configurations de connexion aux bases de données doivent être adaptées selon votre environnement
- **Kafka** : Fonctionnel avec `kafka_consumer.py` (nécessite Kafka installé)
- **Pentaho** : Deux options disponibles :
  - `pentaho_example.ktr` : Template pour Pentaho PDI (nécessite Pentaho installé)
  - `pentaho_sync.py` : Script Python fonctionnel (alternative sans Pentaho)
- **WSO2** : Deux options disponibles :
  - `wso2_example.xml` : Template pour WSO2 EI (nécessite WSO2 installé)
  - `wso2_sync.py` : Script Python fonctionnel (alternative sans WSO2)
- **sync_script.py** : Alternative générique Python pour la synchronisation

