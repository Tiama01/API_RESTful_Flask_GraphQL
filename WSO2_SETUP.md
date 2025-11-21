# Guide d'Installation et Configuration WSO2 Enterprise Integrator

## Vue d'ensemble

WSO2 Enterprise Integrator (EI) est une plateforme d'intégration open-source qui permet de créer des API Proxies pour synchroniser les données entre différentes bases de données. Ce guide vous aidera à installer et configurer WSO2 EI pour utiliser le fichier `integration/wso2_example.xml` du projet.

## Installation

### Option 1 : Installation via le site officiel (Recommandé)

1. **Télécharger WSO2 Enterprise Integrator**
   - Allez sur https://wso2.com/integration/
   - Téléchargez la dernière version de WSO2 Enterprise Integrator
   - Version recommandée : 7.x ou supérieure
   - Format : ZIP (pour Linux/macOS) ou ZIP (pour Windows)

2. **Extraire l'archive**
   ```bash
   # Linux/macOS
   unzip wso2ei-7.x.x.zip
   cd wso2ei-7.x.x
   
   # Windows
   # Extraire avec WinRAR ou 7-Zip
   ```

3. **Définir les variables d'environnement** (recommandé)
   ```bash
   # Linux/macOS - Ajouter à ~/.bashrc ou ~/.zshrc
   export WSO2_HOME=/chemin/vers/wso2ei-7.x.x
   export PATH=$PATH:$WSO2_HOME/bin
   
   # Windows - Variables d'environnement système
   WSO2_HOME=C:\chemin\vers\wso2ei-7.x.x
   PATH=%PATH%;%WSO2_HOME%\bin
   ```

### Option 2 : Installation via package manager (Linux)

```bash
# Certaines distributions Linux ont WSO2 dans leurs dépôts
# Sinon, télécharger depuis le site officiel
```

### Option 3 : Utiliser Docker (Alternative)

```bash
# Image Docker officielle WSO2
docker pull wso2/wso2ei:7.x.x

# Lancer le conteneur
docker run -it -p 8280:8280 -p 9443:9443 wso2/wso2ei:7.x.x
```

## Configuration

### 1. Configuration de base

1. **Lancer WSO2 EI**
   ```bash
   # Linux/macOS
   cd $WSO2_HOME
   ./bin/integrator.sh
   
   # Windows
   cd %WSO2_HOME%
   bin\integrator.bat
   ```

2. **Vérifier l'installation**
   - WSO2 EI démarre sur le port 9443 (HTTPS)
   - Console d'administration : https://localhost:9443/carbon
   - Identifiants par défaut : admin / admin

### 2. Configuration des Data Sources

#### Pour utiliser le fichier `wso2_example.xml` :

1. **Accéder à la console d'administration**
   - Ouvrir https://localhost:9443/carbon
   - Se connecter avec admin / admin

2. **Créer la Data Source source (Base A)**
   - Menu : Main → Data Sources → Add
   - Nom : SourceDB
   - Type : MySQL, PostgreSQL, ou SQLite selon votre configuration
   - URL : 
     - MySQL : `jdbc:mysql://localhost:3306/source_db`
     - PostgreSQL : `jdbc:postgresql://localhost:5432/source_db`
     - SQLite : `jdbc:sqlite:/chemin/vers/source_articles.db`
   - Username : votre_utilisateur
   - Password : votre_mot_de_passe
   - Cliquer sur "Test Connection" pour vérifier
   - Sauvegarder

3. **Créer la Data Source destination (Base B)**
   - Répéter les étapes pour DestinationDB
   - Configurer selon votre base de destination

### 3. Déploiement de l'API Proxy

1. **Créer l'API Proxy**
   - Menu : Main → APIs → Create → New API
   - Ou utiliser l'éditeur de fichiers

2. **Copier le contenu de `wso2_example.xml`**
   - Créer un nouveau fichier API
   - Copier le contenu de `integration/wso2_example.xml`
   - Adapter les noms de Data Sources si nécessaire

3. **Déployer l'API**
   - Sauvegarder le fichier
   - L'API sera automatiquement déployée
   - Vérifier dans : Main → APIs → List

### 4. Configuration pour SQLite

Si vous utilisez SQLite :

1. **Télécharger le driver JDBC SQLite**
   ```bash
   # Télécharger depuis https://github.com/xerial/sqlite-jdbc/releases
   # Copier sqlite-jdbc-x.x.x.jar dans $WSO2_HOME/lib
   ```

2. **Créer la Data Source SQLite**
   - Type : Generic
   - Driver : org.sqlite.JDBC
   - URL : jdbc:sqlite:/chemin/vers/source_articles.db

## Utilisation avec le projet

### Méthode 1 : Utiliser WSO2 EI avec le fichier .xml

1. **Démarrer WSO2 EI**
   ```bash
   cd $WSO2_HOME
   ./bin/integrator.sh
   ```

2. **Démarrer l'API REST Flask**
   ```bash
   python app.py
   ```

3. **Appeler l'API Proxy WSO2**
   ```bash
   # Synchronisation des articles
   curl http://localhost:8280/articles-sync
   
   # Avec paramètre de dernière synchronisation
   curl "http://localhost:8280/articles-sync?lastSyncTime=2024-01-01T00:00:00"
   
   # Health check
   curl http://localhost:8280/health
   ```

### Méthode 2 : Utiliser le script Python (Alternative)

Si vous ne voulez pas installer WSO2 EI, utilisez le script Python :

```bash
# Le script wso2_sync.py reproduit le comportement de WSO2 EI
python integration/wso2_sync.py

# L'API Proxy sera accessible sur http://localhost:8280/articles-sync
```

## Configuration avancée

### Variables d'environnement pour le script Python

```bash
# Bases de données
export WSO2_SOURCE_DB=source_articles.db
export WSO2_DESTINATION_DB=destination_articles.db
export SOURCE_DB_TYPE=sqlite  # sqlite, mysql, postgresql
export DEST_DB_TYPE=sqlite

# API REST
export REST_API_URL=http://localhost:5000

# Port du proxy WSO2
export WSO2_PROXY_PORT=8280

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

### Configuration du port

Par défaut, WSO2 EI écoute sur :
- Port 8280 : HTTP (API Proxy)
- Port 9443 : HTTPS (Console d'administration)

Pour modifier les ports, éditer `$WSO2_HOME/repository/conf/tomcat/catalina-server.xml`

## Dépannage

### Erreur : Java non trouvé

```bash
# WSO2 EI nécessite Java 8 ou 11
# Installer Java
# macOS
brew install openjdk@11

# Linux
sudo apt-get install openjdk-11-jdk

# Vérifier
java -version
```

### Erreur : Port déjà utilisé

```bash
# Vérifier les ports utilisés
# Linux/macOS
lsof -i :8280
lsof -i :9443

# Windows
netstat -ano | findstr :8280

# Modifier les ports dans la configuration si nécessaire
```

### Erreur : Data Source non trouvée

- Vérifier que les Data Sources sont créées dans la console
- Vérifier les noms dans le fichier XML (SourceDB, DestinationDB)
- Vérifier que les drivers JDBC sont installés

### Erreur : API REST non accessible

- Vérifier que l'API REST Flask est démarrée : `python app.py`
- Vérifier l'URL dans la configuration : `http://localhost:5000`
- Tester avec curl : `curl http://localhost:5000/health`

### Erreur : Connexion à la base de données échoue

- Vérifier que les bases de données sont accessibles
- Vérifier les credentials dans les Data Sources
- Tester la connexion depuis la console WSO2

## Intégration avec le script start.sh

Pour démarrer WSO2 automatiquement avec les autres services :

```bash
# Ajouter dans start.sh (optionnel)
# Démarrer WSO2 EI si nécessaire
```

## Sécurité

### Changer le mot de passe par défaut

1. Accéder à https://localhost:9443/carbon
2. Menu : Configure → Users and Roles
3. Modifier le mot de passe de l'utilisateur admin

### Configuration HTTPS

- WSO2 EI utilise HTTPS par défaut pour la console
- Les certificats sont dans `$WSO2_HOME/repository/resources/security`

## Ressources

- Documentation officielle : https://ei.docs.wso2.com/
- Forum communautaire : https://stackoverflow.com/questions/tagged/wso2
- GitHub : https://github.com/wso2/product-ei

## Notes

- WSO2 EI nécessite Java 8 ou 11
- La console d'administration nécessite un navigateur web
- Le script Python `wso2_sync.py` est une alternative fonctionnelle qui ne nécessite pas WSO2 EI
- Pour la production, configurer les certificats SSL et la sécurité appropriée

