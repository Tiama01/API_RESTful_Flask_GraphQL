# Configuration rapide de KAFKA_HOME pour Homebrew

## Pour votre installation actuelle

Vous avez Kafka installé via Homebrew dans `/usr/local/opt/kafka`. Voici comment configurer correctement les variables d'environnement :

### Configuration pour zsh (macOS par défaut)

```bash
# Ajouter à ~/.zshrc
echo 'export KAFKA_HOME=$(brew --prefix kafka)' >> ~/.zshrc
echo 'export PATH=$PATH:$KAFKA_HOME/libexec/bin' >> ~/.zshrc

# Recharger la configuration
source ~/.zshrc
```

### Configuration pour bash

```bash
# Ajouter à ~/.bash_profile ou ~/.bashrc
echo 'export KAFKA_HOME=$(brew --prefix kafka)' >> ~/.bash_profile
echo 'export PATH=$PATH:$KAFKA_HOME/libexec/bin' >> ~/.bash_profile

# Recharger la configuration
source ~/.bash_profile
```

### Vérification

```bash
# Vérifier que KAFKA_HOME est défini
echo $KAFKA_HOME
# Devrait afficher: /usr/local/opt/kafka

# Vérifier que les scripts sont accessibles
kafka-server-start.sh --version
kafka-topics.sh --version
```

## Démarrage de Kafka

### Option 1 : Service Homebrew (recommandé)

```bash
# Démarrer Kafka comme service
brew services start kafka

# Vérifier le statut
brew services list | grep kafka

# Arrêter le service
brew services stop kafka
```

### Option 2 : Démarrage manuel

```bash
# Démarrer Zookeeper (nécessaire pour Kafka)
zookeeper-server-start.sh /usr/local/etc/kafka/zookeeper.properties

# Dans un autre terminal, démarrer Kafka
kafka-server-start.sh /usr/local/etc/kafka/server.properties
```

### Option 3 : Utiliser le script start.sh du projet

```bash
# Le script détecte automatiquement Kafka installé via Homebrew
./start.sh kafka

# Ou démarrer tous les services
./start.sh all
```

## Emplacements des fichiers avec Homebrew

- **Scripts Kafka** : `/usr/local/opt/kafka/libexec/bin/`
- **Configuration Kafka** : `/usr/local/etc/kafka/server.properties`
- **Configuration Zookeeper** : `/usr/local/etc/kafka/zookeeper.properties`
- **KAFKA_HOME** : `/usr/local/opt/kafka` (ou utilisez `$(brew --prefix kafka)`)

## Créer le topic pour le projet

Une fois Kafka démarré :

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

## Notes importantes

- Avec Homebrew, les scripts sont dans `libexec/bin` et non `bin`
- Les fichiers de configuration sont dans `/usr/local/etc/kafka/` (ou `/opt/homebrew/etc/kafka/` sur Apple Silicon)
- Le script `start.sh` du projet détecte automatiquement Kafka installé via Homebrew
- Si vous utilisez `brew services`, Zookeeper est géré automatiquement

