# Résoudre l'erreur "cannot be opened because the developer cannot be verified" sur macOS

## Problème

macOS bloque l'exécution de Prometheus car le binaire n'est pas signé par un développeur vérifié par Apple.

## Solution 1 : Retirer le flag de quarantaine (Recommandé)

```bash
# Retirer le flag de quarantaine de macOS
sudo xattr -rd com.apple.quarantine /usr/local/prometheus/prometheus
sudo xattr -rd com.apple.quarantine /usr/local/prometheus/promtool

# Vérifier que les flags ont été retirés
xattr -l /usr/local/prometheus/prometheus
```

## Solution 2 : Autoriser via les Paramètres Système

1. **Ouvrir les Paramètres Système**
   - Aller dans **Sécurité et confidentialité** (ou **Confidentialité et sécurité**)

2. **Autoriser Prometheus**
   - Essayer d'exécuter `prometheus --version`
   - Une alerte apparaîtra
   - Cliquer sur **Ouvrir quand même** ou **Autoriser**

3. **Si l'option n'apparaît pas**
   - Aller dans **Paramètres Système** > **Confidentialité et sécurité**
   - Faire défiler jusqu'à **Sécurité**
   - Cliquer sur **Ouvrir quand même** à côté du message concernant Prometheus

## Solution 3 : Utiliser la ligne de commande avec confirmation

```bash
# Exécuter avec confirmation
sudo spctl --master-disable  # Désactiver temporairement Gatekeeper (non recommandé pour la sécurité)
# Puis exécuter prometheus
prometheus --version
sudo spctl --master-enable   # Réactiver Gatekeeper
```

## Solution 4 : Vérifier et corriger les permissions

```bash
# Vérifier les permissions
ls -la /usr/local/prometheus/prometheus

# S'assurer que le fichier est exécutable
sudo chmod +x /usr/local/prometheus/prometheus
sudo chmod +x /usr/local/prometheus/promtool

# Vérifier que les liens symboliques pointent correctement
ls -la /usr/local/bin/prometheus
```

## Solution 5 : Exécuter directement depuis /usr/local/prometheus

Si les liens symboliques ne fonctionnent pas :

```bash
# Utiliser le chemin complet
/usr/local/prometheus/prometheus --version

# Ou ajouter au PATH temporairement
export PATH=$PATH:/usr/local/prometheus
prometheus --version
```

## Vérification

Après avoir appliqué une des solutions :

```bash
# Tester Prometheus
prometheus --version

# Devrait afficher quelque chose comme :
# prometheus, version 3.8.0-rc.0
```

## Utilisation avec le projet

Une fois que Prometheus fonctionne :

```bash
# Depuis le répertoire du projet
cd /Users/azizabdoul/Documents/API_RESTful_Flask_GraphQL

# Démarrer Prometheus
prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus_data

# Ou utiliser le script
./start.sh prometheus
```

## Note de sécurité

- Retirer le flag de quarantaine est généralement sûr pour des binaires téléchargés depuis des sources officielles (comme GitHub releases de Prometheus)
- Ne désactivez pas Gatekeeper de manière permanente pour des raisons de sécurité
- Vérifiez toujours que vous téléchargez depuis les sources officielles

