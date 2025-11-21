# Guide d'Installation Prometheus

## Problème avec Homebrew

Si vous rencontrez des erreurs lors de l'installation via Homebrew (notamment sur macOS 13 ou versions plus anciennes), voici plusieurs alternatives.

## Option 1 : Installation manuelle (Recommandé)

### macOS / Linux

1. **Télécharger Prometheus**
   ```bash
   # Trouver la dernière version sur https://prometheus.io/download/
   # Exemple pour macOS (Intel)
   cd ~/Downloads
   wget https://github.com/prometheus/prometheus/releases/download/v2.51.0/prometheus-2.51.0.darwin-amd64.tar.gz
   
   # Ou pour Apple Silicon
   wget https://github.com/prometheus/prometheus/releases/download/v2.51.0/prometheus-2.51.0.darwin-arm64.tar.gz
   ```

2. **Extraire l'archive**
   ```bash
   tar -xzf prometheus-2.51.0.darwin-*.tar.gz
   cd prometheus-2.51.0.darwin-*
   ```

3. **Déplacer vers un emplacement permanent**
   ```bash
   # Créer un dossier pour Prometheus
   sudo mkdir -p /usr/local/prometheus
   sudo mv prometheus promtool /usr/local/prometheus/
   sudo mv consoles console_libraries /usr/local/prometheus/
   ```

4. **Créer un lien symbolique**
   ```bash
   sudo ln -s /usr/local/prometheus/prometheus /usr/local/bin/prometheus
   ```

5. **Vérifier l'installation**
   ```bash
   prometheus --version
   ```

## Option 2 : Installation via Docker

Si Docker est installé :

```bash
# Lancer Prometheus via Docker
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Vérifier
docker ps | grep prometheus
```

## Option 3 : Utiliser le script du projet (sans Prometheus)

Le projet fonctionne sans Prometheus. Les métriques sont toujours exposées sur `/metrics`, mais ne seront pas collectées automatiquement.

```bash
# Démarrer les services sans Prometheus
./start.sh rest
./start.sh graphql
```

## Option 4 : Installation via Homebrew (si disponible)

Si Homebrew fonctionne correctement :

```bash
# Essayer l'installation
brew install prometheus

# Si cela échoue, essayer de mettre à jour Homebrew d'abord
brew update
brew upgrade
brew install prometheus
```

## Configuration après installation manuelle

1. **Créer un fichier de configuration** (déjà présent dans le projet : `prometheus.yml`)

2. **Démarrer Prometheus**
   ```bash
   # Depuis le répertoire du projet
   prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus_data
   ```

3. **Ou utiliser le script start.sh**
   ```bash
   # Le script détectera Prometheus s'il est dans le PATH
   ./start.sh prometheus
   ```

## Vérification

Une fois Prometheus installé et démarré :

1. **Vérifier que Prometheus fonctionne**
   ```bash
   curl http://localhost:9090
   ```

2. **Accéder à l'interface web**
   - Ouvrir http://localhost:9090 dans un navigateur

3. **Vérifier les métriques**
   - Aller dans Status → Targets
   - Vérifier que `flask-rest-api` est "UP"

## Variables d'environnement (optionnel)

Pour faciliter l'utilisation, ajouter à `~/.zshrc` ou `~/.bash_profile` :

```bash
# Prometheus
export PROMETHEUS_HOME=/usr/local/prometheus
export PATH=$PATH:$PROMETHEUS_HOME
```

## Dépannage

### Erreur : "command not found: prometheus"

- Vérifier que Prometheus est dans le PATH
- Vérifier les permissions : `chmod +x /usr/local/prometheus/prometheus`

### Erreur : "port 9090 already in use"

- Arrêter le processus existant : `lsof -ti:9090 | xargs kill`
- Ou utiliser un autre port : `prometheus --web.listen-address=:9091`

### Erreur : "permission denied"

- Utiliser `sudo` pour les opérations de déplacement
- Ou installer dans un dossier utilisateur : `~/prometheus`

## Notes importantes

- Prometheus est optionnel pour le projet
- Les métriques Flask sont toujours disponibles sur `http://localhost:5000/metrics`
- Vous pouvez visualiser les métriques directement via curl sans Prometheus
- Pour la production, utiliser une installation complète de Prometheus avec stockage persistant

