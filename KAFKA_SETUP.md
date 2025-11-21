# Guide d'Installation et Configuration Kafka

## Vue d'ensemble

Kafka est utilisé dans ce projet pour la synchronisation des articles entre différentes bases de données. Ce guide vous aidera à installer et configurer Kafka pour le projet.

## Installation

### macOS (avec Homebrew)

```bash
# Installer Kafka via Homebrew
brew install kafka

# Kafka sera installé dans /opt/homebrew/opt/kafka (Apple Silicon)
# ou /usr/local/opt/kafka (Intel)
```

### Linux (Ubuntu/Debian)

```bash
# Télécharger Kafka
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz

# Extraire
tar -xzf kafka_2.13-3.6.0.tgz

# Déplacer vers un emplacement permanent
sudo mv kafka_2.13-3.6.0 /opt/kafka

# Créer un lien symbolique
sudo ln -s /opt/kafka /usr/local/kafka
```

### Installation manuelle

1. **Télécharger Kafka** depuis [https://kafka.apache.org/downloads](https://kafka.apache.org/downloads)

2. **Extraire l'archive** :
```bash
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0
```

3. **Définir la variable d'environnement** (recommandé) :
```bash
# Ajouter à ~/.bashrc ou ~/.zshrc
export KAFKA_HOME=/chemin/vers/kafka
export PATH=$PATH:$KAFKA_HOME/bin
```

## Configuration

### 1. Configuration Zookeeper

Le fichier de configuration se trouve généralement dans `$KAFKA_HOME/config/zookeeper.properties`.

Configuration minimale (déjà présente par défaut) :
```properties
dataDir=/tmp/zookeeper
clientPort=2181
maxClientCnxns=0
```

### 2. Configuration Kafka

Le fichier de configuration se trouve généralement dans `$KAFKA_HOME/config/server.properties`.

Configuration minimale pour le développement local :
```properties
broker.id=0
listeners=PLAINTEXT://localhost:9092
log.dirs=/tmp/kafka-logs
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
log.retention.hours=168
zookeeper.connect=localhost:2181
zookeeper.connection.timeout.ms=18000
```

### 3. Créer le topic pour le projet

```bash
# Créer le topic "articles-sync"
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic articles-sync

# Vérifier que le topic a été créé
kafka-topics.sh --list --bootstrap-server localhost:9092
```

## Démarrage manuel

### Option 1 : Démarrage séparé

```bash
# Terminal 1 : Démarrer Zookeeper
zookeeper-server-start.sh config/zookeeper.properties

# Terminal 2 : Démarrer Kafka
kafka-server-start.sh config/server.properties

# Terminal 3 : Démarrer le consumer (depuis le projet)
cd /Users/azizabdoul/Documents/API_RESTful_Flask_GraphQL
source venv/bin/activate
python integration/kafka_consumer.py
```

### Option 2 : Utiliser le script start.sh

```bash
# Démarrer uniquement Kafka
./start.sh kafka

# Démarrer tous les services (incluant Kafka si disponible)
./start.sh all
```

## Vérification

### Vérifier que Zookeeper fonctionne

```bash
# Vérifier le port
lsof -i :2181

# Ou tester la connexion
telnet localhost 2181
```

### Vérifier que Kafka fonctionne

```bash
# Vérifier le port
lsof -i :9092

# Lister les topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Consulter les messages d'un topic
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic articles-sync \
  --from-beginning
```

## Envoyer un message de test

### Via le script Python

```bash
cd /Users/azizabdoul/Documents/API_RESTful_Flask_GraphQL
source venv/bin/activate
python integration/kafka_consumer.py test
```

### Via la ligne de commande Kafka

```bash
# Terminal 1 : Consumer
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic articles-sync

# Terminal 2 : Producer
kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic articles-sync

# Puis taper un message JSON, par exemple :
{"title": "Article de test", "content": "Contenu de test"}
```

### Via Python (script de test)

Créer un fichier `test_kafka_producer.py` :

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

test_article = {
    'title': 'Article depuis Kafka',
    'content': 'Ceci est un article synchronisé depuis Kafka'
}

producer.send('articles-sync', test_article)
producer.flush()
print("Message envoyé avec succès")
```

## Arrêt

### Arrêt manuel

```bash
# Arrêter Kafka
kafka-server-stop.sh

# Arrêter Zookeeper
zookeeper-server-stop.sh
```

### Via le script stop.sh

```bash
./stop.sh
```

## Dépannage

### Kafka n'est pas trouvé par le script

1. **Vérifier l'installation** :
```bash
which kafka-server-start.sh
```

2. **Définir KAFKA_HOME** :
```bash
export KAFKA_HOME=/chemin/vers/kafka
```

3. **Ajouter au PATH** :
```bash
export PATH=$PATH:$KAFKA_HOME/bin
```

### Port déjà utilisé

Si le port 2181 (Zookeeper) ou 9092 (Kafka) est déjà utilisé :

```bash
# Trouver le processus
lsof -i :2181
lsof -i :9092

# Arrêter le processus
kill -9 <PID>
```

### Erreur de connexion au consumer

1. Vérifier que Kafka est démarré : `lsof -i :9092`
2. Vérifier que le topic existe : `kafka-topics.sh --list --bootstrap-server localhost:9092`
3. Vérifier les logs : `tail -f logs/kafka_consumer.log`

### Erreur "Connection refused"

- Vérifier que Zookeeper est démarré avant Kafka
- Vérifier les ports dans la configuration
- Vérifier les logs : `tail -f logs/zookeeper.log` et `tail -f logs/kafka.log`

## Configuration pour le projet

Le projet utilise les variables d'environnement suivantes (optionnelles) :

```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
export KAFKA_TOPIC=articles-sync
export REST_API_URL=http://localhost:5000
```

Ces valeurs sont utilisées par défaut si non définies.

## Alternative : Docker (optionnel)

Si vous préférez utiliser Docker pour Kafka :

```bash
# Démarrer Zookeeper et Kafka avec Docker Compose
docker-compose up -d

# Créer le topic
docker exec -it kafka kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic articles-sync
```

Créer un fichier `docker-compose.yml` :

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

## Ressources

- [Documentation officielle Kafka](https://kafka.apache.org/documentation/)
- [Guide de démarrage rapide](https://kafka.apache.org/quickstart)
- [Configuration Kafka](https://kafka.apache.org/documentation/#configuration)

## Checklist d'installation

- [ ] Kafka téléchargé et extrait
- [ ] Variable `KAFKA_HOME` définie (optionnel mais recommandé)
- [ ] Zookeeper peut démarrer sur le port 2181
- [ ] Kafka peut démarrer sur le port 9092
- [ ] Topic `articles-sync` créé
- [ ] Consumer peut se connecter et recevoir des messages
- [ ] Le script `start.sh` détecte Kafka

