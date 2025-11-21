# Guide d'Installation et Configuration Pentaho Data Integration

## Vue d'ensemble

Pentaho Data Integration (PDI) est un outil ETL (Extract, Transform, Load) qui permet de synchroniser les données entre différentes bases de données. Ce guide vous aidera à installer et configurer Pentaho PDI pour utiliser le fichier `integration/pentaho_example.ktr` du projet.

## Installation

### Option 1 : Installation via le site officiel (Recommandé)

1. **Télécharger Pentaho Data Integration**
   - Allez sur https://sourceforge.net/projects/pentaho/files/
   - Téléchargez la dernière version de Pentaho Data Integration (Spoon)
   - Version recommandée : 9.x ou supérieure

2. **Extraire l'archive**
   ```bash
   # Linux/macOS
   unzip pdi-ce-9.x.x.zip
   cd data-integration
   
   # Windows
   # Extraire avec WinRAR ou 7-Zip
   ```

3. **Définir les variables d'environnement** (optionnel mais recommandé)
   ```bash
   # Linux/macOS - Ajouter à ~/.bashrc ou ~/.zshrc
   export PENTAHO_HOME=/chemin/vers/data-integration
   export PATH=$PATH:$PENTAHO_HOME
   
   # Windows - Variables d'environnement système
   PENTAHO_HOME=C:\chemin\vers\data-integration
   PATH=%PATH%;%PENTAHO_HOME%
   ```

### Option 2 : Installation via package manager (Linux)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install pentaho-data-integration

# Ou télécharger depuis le site officiel
```

### Option 3 : Utiliser Docker (Alternative)

```bash
# Image Docker officielle
docker pull hiromuhota/websphere-base
# Ou utiliser une image Pentaho personnalisée
```

## Configuration

### 1. Configuration de base

1. **Lancer Spoon** (interface graphique de Pentaho)
   ```bash
   # Linux/macOS
   cd $PENTAHO_HOME
   ./spoon.sh
   
   # Windows
   cd %PENTAHO_HOME%
   spoon.bat
   ```

2. **Vérifier l'installation**
   - Spoon devrait s'ouvrir avec l'interface graphique
   - Si des erreurs Java apparaissent, installer Java 8 ou 11

### 2. Configuration des connexions de base de données

#### Pour utiliser le fichier `pentaho_example.ktr` :

1. **Ouvrir le fichier de transformation**
   - Dans Spoon : File → Open → Sélectionner `integration/pentaho_example.ktr`

2. **Configurer la connexion source (Base A)**
   - Clic droit sur "Table Input - Source DB" → Edit
   - Cliquer sur "New" pour créer une nouvelle connexion
   - Type : MySQL, PostgreSQL, ou SQLite selon votre configuration
   - Remplir les informations de connexion :
     - Host: localhost
     - Port: 3306 (MySQL) ou 5432 (PostgreSQL)
     - Database: source_db
     - Username: votre_utilisateur
     - Password: votre_mot_de_passe

3. **Configurer la connexion destination (Base B)**
   - Clic droit sur "Table Output - Destination DB" → Edit
   - Créer ou sélectionner la connexion destination
   - Configurer les mêmes paramètres pour la base de destination

### 3. Configuration pour SQLite

Si vous utilisez SQLite (comme dans le projet) :

1. **Télécharger le driver JDBC SQLite**
   ```bash
   # Télécharger depuis https://github.com/xerial/sqlite-jdbc/releases
   # Copier sqlite-jdbc-x.x.x.jar dans $PENTAHO_HOME/lib
   ```

2. **Créer la connexion SQLite dans Spoon**
   - Type de connexion : Generic database
   - Driver : org.sqlite.JDBC
   - URL : jdbc:sqlite:/chemin/vers/source_articles.db

## Utilisation avec le projet

### Méthode 1 : Utiliser le fichier .ktr dans Pentaho

1. **Préparer les bases de données**
   ```bash
   # Créer les bases de données source et destination
   # Les bases doivent avoir une table 'articles' avec les colonnes :
   # id, title, content, updated_at
   ```

2. **Ouvrir la transformation dans Spoon**
   ```bash
   # Lancer Spoon
   ./spoon.sh
   
   # File → Open → integration/pentaho_example.ktr
   ```

3. **Configurer les connexions**
   - Modifier les connexions source et destination selon votre environnement

4. **Exécuter la transformation**
   - Cliquer sur le bouton "Play" (▶) ou F9
   - Vérifier les logs pour voir le résultat

### Méthode 2 : Utiliser le script Python (Alternative)

Si vous ne voulez pas installer Pentaho, utilisez le script Python :

```bash
# Le script pentaho_sync.py reproduit le comportement de Pentaho
python integration/pentaho_sync.py
```

## Configuration avancée

### Variables d'environnement pour le script Python

```bash
# Bases de données
export PENTAHO_SOURCE_DB=source_articles.db
export PENTAHO_DESTINATION_DB=destination_articles.db
export SOURCE_DB_TYPE=sqlite  # sqlite, mysql, postgresql
export DEST_DB_TYPE=sqlite

# API REST
export REST_API_URL=http://localhost:5000

# Pour MySQL
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=password
export MYSQL_DATABASE=source_db

# Pour PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_DATABASE=destination_db
```

### Exécution programmatique

```bash
# Exécuter la transformation via ligne de commande
cd $PENTAHO_HOME
./kitchen.sh -file=/chemin/vers/pentaho_example.ktr
```

## Dépannage

### Erreur : Java non trouvé

```bash
# Installer Java 8 ou 11
# macOS
brew install openjdk@11

# Linux
sudo apt-get install openjdk-11-jdk

# Vérifier
java -version
```

### Erreur : Driver JDBC non trouvé

- Vérifier que les drivers JDBC sont dans `$PENTAHO_HOME/lib`
- Pour SQLite : télécharger sqlite-jdbc.jar
- Pour MySQL : télécharger mysql-connector-java.jar
- Pour PostgreSQL : télécharger postgresql-jdbc.jar

### Erreur : Connexion à la base de données échoue

- Vérifier que les bases de données sont accessibles
- Vérifier les credentials (username/password)
- Vérifier que les ports sont ouverts
- Tester la connexion avec un client SQL

### Erreur : API REST non accessible

- Vérifier que l'API REST Flask est démarrée : `python app.py`
- Vérifier l'URL dans la transformation : `http://localhost:5000`
- Tester avec curl : `curl http://localhost:5000/health`

## Intégration avec le script start.sh

Pour démarrer Pentaho automatiquement avec les autres services :

```bash
# Ajouter dans start.sh (optionnel)
# Démarrer Pentaho en mode serveur si nécessaire
```

## Ressources

- Documentation officielle : https://help.pentaho.com/
- Forum communautaire : https://forums.pentaho.com/
- GitHub : https://github.com/pentaho/pentaho-kettle

## Notes

- Pentaho PDI nécessite Java 8 ou 11
- L'interface graphique (Spoon) nécessite un environnement graphique
- Pour l'exécution en ligne de commande, utiliser Kitchen (pour les jobs) ou Pan (pour les transformations)
- Le script Python `pentaho_sync.py` est une alternative fonctionnelle qui ne nécessite pas Pentaho

