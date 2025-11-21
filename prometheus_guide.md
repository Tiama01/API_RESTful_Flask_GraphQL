# Guide Prometheus - Monitoring de l'API REST Flask

## Métriques exposées

L'API REST Flask expose automatiquement les métriques suivantes via `prometheus-flask-exporter` :

### Métriques HTTP standard

- **`http_requests_total`**: Nombre total de requêtes HTTP
  - Labels: `method`, `endpoint`, `status`
  
- **`http_request_duration_seconds`**: Temps de réponse par endpoint
  - Labels: `method`, `endpoint`
  - Type: Histogram
  
- **`http_requests_4xx_total`**: Nombre d'erreurs 4xx (client)
  - Labels: `method`, `endpoint`
  
- **`http_requests_5xx_total`**: Nombre d'erreurs 5xx (serveur)
  - Labels: `method`, `endpoint`

### Métriques personnalisées

- **`http_requests_total`** (custom): Nombre total de requêtes avec labels personnalisés
- **`http_request_duration_seconds`** (custom): Temps de réponse par endpoint

## Installation et démarrage de Prometheus

### 1. Télécharger Prometheus

```bash
# macOS
brew install prometheus

# Linux
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64
```

### 2. Démarrer Prometheus

```bash
# Depuis le répertoire du projet
prometheus --config.file=prometheus.yml
```

Prometheus sera accessible sur `http://localhost:9090`

### 3. Vérifier que Prometheus scrape les métriques

1. Ouvrir `http://localhost:9090`
2. Aller dans **Status > Targets**
3. Vérifier que `flask-rest-api` est dans l'état **UP**

## Requêtes PromQL utiles

### Nombre total de requêtes

```promql
sum(http_requests_total)
```

### Taux de requêtes par seconde

```promql
rate(http_requests_total[5m])
```

### Temps de réponse moyen par endpoint

```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

### Taux d'erreurs 4xx

```promql
rate(http_requests_4xx_total[5m])
```

### Taux d'erreurs 5xx

```promql
rate(http_requests_5xx_total[5m])
```

### Requêtes par endpoint

```promql
sum by (endpoint) (rate(http_requests_total[5m]))
```

### Temps de réponse par percentile (p95)

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Dashboard Grafana (optionnel)

Pour visualiser les métriques dans Grafana :

1. Installer Grafana :
```bash
brew install grafana  # macOS
# ou
sudo apt-get install grafana  # Linux
```

2. Démarrer Grafana :
```bash
grafana-server
```

3. Accéder à Grafana : `http://localhost:3000`
   - Login par défaut : `admin` / `admin`

4. Ajouter Prometheus comme source de données :
   - Configuration > Data Sources > Add data source
   - Type : Prometheus
   - URL : `http://localhost:9090`

5. Créer un dashboard avec les requêtes PromQL ci-dessus

## Alertes (exemple)

Créer un fichier `alert_rules.yml` :

```yaml
groups:
  - name: flask_api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_5xx_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreurs 5xx élevé"
          description: "Le taux d'erreurs 5xx est de {{ $value }} erreurs/seconde"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Temps de réponse élevé (p95)"
          description: "Le temps de réponse p95 est de {{ $value }} secondes"
```

Puis décommenter dans `prometheus.yml` :
```yaml
rule_files:
  - "alert_rules.yml"
```

## Notes

- Les métriques sont exposées en temps réel sur `/metrics`
- Prometheus scrape les métriques toutes les 10 secondes (configurable)
- Les métriques sont conservées pendant 15 jours par défaut (configurable)
- Pour la production, configurez un stockage persistant pour Prometheus

