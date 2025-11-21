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
   
   # Déplacer les dossiers consoles et console_libraries s'ils existent
   # (Certaines versions ne les incluent pas)
   if [ -d "consoles" ]; then
       sudo mv consoles /usr/local/prometheus/
   fi
   if [ -d "console_libraries" ]; then
       sudo mv console_libraries /usr/local/prometheus/
   fi
   ```

4. **Créer un lien symbolique**
   ```bash
   sudo ln -s /usr/local/prometheus/prometheus /usr/local/bin/prometheus
   ```

5. **Vérifier l'installation**
   ```bash
   prometheus --version
   ```

**Note :** Si les dossiers `consoles` et `console_libraries` n'existent pas dans votre version, ce n'est pas un problème. Ils sont optionnels et ne sont nécessaires que pour certaines fonctionnalités avancées.

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

### Erreur macOS : "cannot be opened because the developer cannot be verified"

Cette erreur survient car macOS bloque l'exécution de binaires non signés.

**Solution 1 : Retirer le flag de quarantaine (Recommandé)**
```bash
sudo xattr -rd com.apple.quarantine /usr/local/prometheus/prometheus
sudo xattr -rd com.apple.quarantine /usr/local/prometheus/promtool
xattr -l /usr/local/prometheus/prometheus  # Vérifier
```

**Solution 2 : Autoriser via Paramètres Système**
1. Essayer d'exécuter `prometheus --version`
2. Aller dans **Paramètres Système** > **Confidentialité et sécurité**
3. Cliquer sur **Ouvrir quand même** à côté du message concernant Prometheus

**Solution 3 : Vérifier les permissions**
```bash
sudo chmod +x /usr/local/prometheus/prometheus
sudo chmod +x /usr/local/prometheus/promtool
```

## Utilisation de Prometheus

### Métriques exposées par Flask

L'API REST Flask expose automatiquement les métriques suivantes via `prometheus-flask-exporter` :

- **`flask_http_request_total`** : Nombre total de requêtes HTTP
- **`flask_http_request_duration_seconds`** : Temps de réponse par endpoint
- **`flask_http_request_exceptions_total`** : Erreurs (4xx, 5xx)

Accès direct aux métriques : `http://localhost:5000/metrics`

### Requêtes PromQL utiles

Une fois Prometheus démarré, vous pouvez utiliser ces requêtes dans l'interface web (http://localhost:9090) :

**Nombre total de requêtes :**
```promql
sum(flask_http_request_total)
```

**Taux de requêtes par seconde :**
```promql
rate(flask_http_request_total[5m])
```

**Temps de réponse moyen :**
```promql
rate(flask_http_request_duration_seconds_sum[5m]) / rate(flask_http_request_duration_seconds_count[5m])
```

**Taux d'erreurs 4xx :**
```promql
rate(flask_http_request_total{status=~"4.."}[5m])
```

**Taux d'erreurs 5xx :**
```promql
rate(flask_http_request_total{status=~"5.."}[5m])
```

## Notes importantes

- Prometheus est optionnel pour le projet
- Les métriques Flask sont toujours disponibles sur `http://localhost:5000/metrics`
- Vous pouvez visualiser les métriques directement via curl sans Prometheus
- Pour la production, utiliser une installation complète de Prometheus avec stockage persistant
- Consulter la documentation Prometheus pour plus de requêtes PromQL : https://prometheus.io/docs/prometheus/latest/querying/basics/

