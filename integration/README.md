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

### 2. `pentaho_example.ktr`
Fichier de transformation Pentaho Data Integration (PDI) qui :
1. Lit les articles depuis la base de données source (Base A)
2. Transforme les données au format JSON
3. Appelle l'API REST Flask pour créer/mettre à jour les articles
4. Écrit les articles synchronisés dans la base de destination (Base B)

**Utilisation:**
- Ouvrir le fichier dans Pentaho Data Integration
- Configurer les connexions aux bases de données
- Exécuter la transformation

### 3. `wso2_example.xml`
Configuration WSO2 Enterprise Integrator (EI) qui définit une API Proxy pour :
1. Récupérer les données depuis la base source
2. Appeler l'API REST Flask
3. Sauvegarder dans la base de destination

**Utilisation:**
- Déployer le fichier dans WSO2 EI
- Configurer les Data Sources (SourceDB et DestinationDB)
- Appeler l'API via `/articles-sync`

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
- Les exemples Pentaho et WSO2 sont des templates à personnaliser selon vos besoins

