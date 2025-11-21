# Vérification de Kafka

## Important : Kafka n'a pas d'interface web HTTP

Kafka fonctionne sur le port **9092**, mais ce n'est **pas une URL HTTP**. C'est le port du broker Kafka pour les connexions client utilisant le protocole binaire Kafka.

**Vous ne pouvez pas accéder à Kafka via un navigateur web sur `http://localhost:9092`**

## Comment vérifier que Kafka fonctionne

### 1. Vérifier que Kafka écoute sur le port 9092

```bash
# Vérifier que le port est ouvert
lsof -i :9092

# Ou avec netstat
netstat -an | grep 9092
```

### 2. Lister les topics Kafka

```bash
# Lister tous les topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Devrait afficher au moins : articles-sync (si créé)
```

### 3. Créer le topic pour le projet (si pas déjà fait)

```bash
# Créer le topic "articles-sync"
kafka-topics.sh --create \
  --bootstrap-server localhost:9092 \
  --replication-factor 1 \
  --partitions 1 \
  --topic articles-sync

# Vérifier que le topic existe
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### 4. Tester avec un producer et consumer

**Terminal 1 - Producer :**
```bash
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic articles-sync
# Taper un message et appuyer sur Entrée
```

**Terminal 2 - Consumer :**
```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic articles-sync --from-beginning
# Devrait afficher les messages envoyés par le producer
```

### 5. Vérifier via le script du projet

Le script `start.sh` démarre automatiquement le Kafka Consumer qui écoute les messages :

```bash
# Vérifier les logs du consumer
tail -f logs/kafka_consumer.log
```

## Outils pour gérer Kafka

### Kafka CLI (ligne de commande)

```bash
# Lister les topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Décrire un topic
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic articles-sync

# Créer un topic
kafka-topics.sh --create --bootstrap-server localhost:9092 --topic mon-topic --partitions 1 --replication-factor 1

# Supprimer un topic
kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic mon-topic
```

### Outils graphiques (optionnels)

Si vous voulez une interface graphique pour Kafka, vous pouvez installer :

- **Kafka UI** : https://github.com/provectus/kafka-ui
- **Kafdrop** : https://github.com/obsidiandynamics/kafdrop
- **Kafka Manager** : https://github.com/yahoo/kafka-manager

Ces outils fournissent une interface web pour gérer Kafka.

## Vérification rapide

Pour vérifier rapidement que Kafka fonctionne :

```bash
# 1. Vérifier que le processus Kafka tourne
ps aux | grep kafka

# 2. Vérifier le port
lsof -i :9092

# 3. Lister les topics (doit fonctionner sans erreur)
kafka-topics.sh --list --bootstrap-server localhost:9092
```

Si toutes ces commandes fonctionnent, Kafka est opérationnel !

## Notes

- Le port 9092 est pour les connexions client Kafka (protocole binaire)
- Il n'y a pas d'interface HTTP/Web par défaut
- Utilisez les outils CLI Kafka pour interagir avec Kafka
- Le script `start.sh` démarre automatiquement le consumer qui écoute les messages

