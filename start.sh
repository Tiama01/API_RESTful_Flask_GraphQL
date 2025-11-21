#!/bin/bash

# Script de démarrage amélioré pour tous les services
# Usage: ./start.sh [rest|graphql|prometheus|kafka|consumer|all]

# Note: On n'utilise pas set -e car certains services sont optionnels
# et leur échec ne doit pas arrêter le script

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables pour stocker les PIDs
REST_PID=""
GRAPHQL_PID=""
PROMETHEUS_PID=""
ZOOKEEPER_PID=""
KAFKA_PID=""
CONSUMER_PID=""

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    log_info "Arrêt de tous les services..."
    
    [ -n "$REST_PID" ] && kill $REST_PID 2>/dev/null && log_info "API REST arrêtée (PID: $REST_PID)"
    [ -n "$GRAPHQL_PID" ] && kill $GRAPHQL_PID 2>/dev/null && log_info "GraphQL arrêté (PID: $GRAPHQL_PID)"
    [ -n "$PROMETHEUS_PID" ] && kill $PROMETHEUS_PID 2>/dev/null && log_info "Prometheus arrêté (PID: $PROMETHEUS_PID)"
    [ -n "$CONSUMER_PID" ] && kill $CONSUMER_PID 2>/dev/null && log_info "Kafka Consumer arrêté (PID: $CONSUMER_PID)"
    [ -n "$KAFKA_PID" ] && kill $KAFKA_PID 2>/dev/null && log_info "Kafka arrêté (PID: $KAFKA_PID)"
    [ -n "$ZOOKEEPER_PID" ] && kill $ZOOKEEPER_PID 2>/dev/null && log_info "Zookeeper arrêté (PID: $ZOOKEEPER_PID)"
    
    # Attendre un peu pour que les processus se terminent proprement
    sleep 2
    
    # Forcer l'arrêt si nécessaire
    [ -n "$REST_PID" ] && kill -9 $REST_PID 2>/dev/null || true
    [ -n "$GRAPHQL_PID" ] && kill -9 $GRAPHQL_PID 2>/dev/null || true
    [ -n "$PROMETHEUS_PID" ] && kill -9 $PROMETHEUS_PID 2>/dev/null || true
    [ -n "$CONSUMER_PID" ] && kill -9 $CONSUMER_PID 2>/dev/null || true
    [ -n "$KAFKA_PID" ] && kill -9 $KAFKA_PID 2>/dev/null || true
    [ -n "$ZOOKEEPER_PID" ] && kill -9 $ZOOKEEPER_PID 2>/dev/null || true
    
    log_success "Tous les services ont été arrêtés"
    exit 0
}

# Enregistrer la fonction de nettoyage
trap cleanup INT TERM EXIT

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    log_info "Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Fonction pour vérifier si un port est disponible
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 1  # Port occupé
    else
        return 0  # Port libre
    fi
}

# Fonction pour attendre qu'un service soit prêt
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0
    
    log_info "Attente que $service_name soit prêt..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            log_success "$service_name est prêt"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    log_warning "$service_name n'est pas encore prêt après $max_attempts tentatives"
    return 1
}

# Fonction pour démarrer l'API REST
start_rest() {
    if check_port 5000; then
        log_info "Démarrage de l'API REST Flask..."
        python app.py > logs/rest.log 2>&1 &
        REST_PID=$!
        sleep 2
        
        # Vérifier si le processus est toujours en cours d'exécution
        if ! kill -0 $REST_PID 2>/dev/null; then
            log_error "L'API REST s'est arrêtée immédiatement après le démarrage"
            log_info "Dernières lignes du log:"
            tail -20 logs/rest.log | sed 's/^/  /'
            return 1
        fi
        
        if wait_for_service "http://localhost:5000/health" "API REST"; then
            log_success "API REST démarrée (PID: $REST_PID) - http://localhost:5000"
        else
            log_error "L'API REST n'a pas démarré correctement"
            log_info "Dernières lignes du log:"
            tail -20 logs/rest.log | sed 's/^/  /'
            return 1
        fi
    else
        log_warning "Le port 5000 est déjà utilisé. L'API REST est peut-être déjà démarrée."
    fi
}

# Fonction pour démarrer GraphQL
start_graphql() {
    if check_port 8000; then
        log_info "Démarrage du serveur GraphQL..."
        python graphql_server.py > logs/graphql.log 2>&1 &
        GRAPHQL_PID=$!
        sleep 2
        
        # Vérifier si le processus est toujours en cours d'exécution
        if ! kill -0 $GRAPHQL_PID 2>/dev/null; then
            log_error "Le serveur GraphQL s'est arrêté immédiatement après le démarrage"
            log_info "Dernières lignes du log:"
            tail -20 logs/graphql.log | sed 's/^/  /'
            return 1
        fi
        
        if wait_for_service "http://localhost:8000/health" "GraphQL"; then
            log_success "GraphQL démarré (PID: $GRAPHQL_PID) - http://localhost:8000/graphql"
        else
            log_error "Le serveur GraphQL n'a pas démarré correctement"
            log_info "Dernières lignes du log:"
            tail -20 logs/graphql.log | sed 's/^/  /'
            return 1
        fi
    else
        log_warning "Le port 8000 est déjà utilisé. GraphQL est peut-être déjà démarré."
    fi
}

# Fonction pour démarrer Prometheus
start_prometheus() {
    if ! command -v prometheus &> /dev/null; then
        log_warning "Prometheus n'est pas installe."
        log_info "Options d'installation:"
        log_info "   - Installation manuelle: Consultez PROMETHEUS_INSTALL.md"
        log_info "   - Via Docker: docker run -d -p 9090:9090 prom/prometheus"
        log_info "   - Note: Prometheus est optionnel, les metriques sont disponibles sur /metrics"
        return 1
    fi
    
    if check_port 9090; then
        if [ ! -f "prometheus.yml" ]; then
            log_error "Le fichier prometheus.yml n'existe pas"
            return 1
        fi
        
        log_info "Démarrage de Prometheus..."
        prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus_data > logs/prometheus.log 2>&1 &
        PROMETHEUS_PID=$!
        sleep 3
        if wait_for_service "http://localhost:9090" "Prometheus"; then
            log_success "Prometheus démarré (PID: $PROMETHEUS_PID) - http://localhost:9090"
        else
            log_warning "Prometheus a démarré mais n'est pas encore accessible"
        fi
    else
        log_warning "Le port 9090 est déjà utilisé. Prometheus est peut-être déjà démarré."
    fi
}

# Fonction pour trouver Kafka
find_kafka() {
    # Chercher dans les emplacements communs
    local kafka_paths=(
        "$HOME/kafka/bin"
        "/usr/local/kafka/bin"
        "/opt/kafka/bin"
        "$KAFKA_HOME/bin"
        "./kafka/bin"
        "/opt/homebrew/opt/kafka/libexec/bin"  # Homebrew sur Apple Silicon (libexec)
        "/usr/local/opt/kafka/libexec/bin"      # Homebrew sur Intel (libexec)
        "/opt/homebrew/opt/kafka/bin"            # Homebrew sur Apple Silicon (bin)
        "/usr/local/opt/kafka/bin"                # Homebrew sur Intel (bin)
    )
    
    for path in "${kafka_paths[@]}"; do
        if [ -f "$path/kafka-server-start.sh" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # Si Homebrew est installé, chercher via brew --prefix
    if command -v brew &> /dev/null; then
        local brew_kafka=$(brew --prefix kafka 2>/dev/null)
        if [ -n "$brew_kafka" ]; then
            local brew_bin="$brew_kafka/libexec/bin"
            if [ -f "$brew_bin/kafka-server-start.sh" ]; then
                echo "$brew_bin"
                return 0
            fi
        fi
    fi
    
    # Chercher dans le PATH
    if command -v kafka-server-start.sh &> /dev/null; then
        dirname $(which kafka-server-start.sh)
        return 0
    fi
    
    # Chercher kafka-topics.sh (alternative)
    if command -v kafka-topics.sh &> /dev/null; then
        local kafka_bin=$(dirname $(which kafka-topics.sh))
        if [ -f "$kafka_bin/kafka-server-start.sh" ]; then
            echo "$kafka_bin"
            return 0
        fi
    fi
    
    return 1
}

# Fonction pour vérifier si Kafka utilise KRaft (pas besoin de Zookeeper)
is_kafka_kraft() {
    local kafka_configs=(
        "/usr/local/etc/kafka/server.properties"
        "/opt/homebrew/etc/kafka/server.properties"
        "$HOME/kafka/config/server.properties"
        "/usr/local/kafka/config/server.properties"
        "/opt/kafka/config/server.properties"
    )
    
    for config in "${kafka_configs[@]}"; do
        if [ -f "$config" ]; then
            # Vérifier si process.roles est défini (mode KRaft)
            if grep -q "process.roles" "$config" 2>/dev/null; then
                return 0  # Mode KRaft
            fi
        fi
    done
    
    return 1  # Mode Zookeeper
}

# Fonction pour démarrer Zookeeper
start_zookeeper() {
    # Vérifier si Kafka utilise KRaft (pas besoin de Zookeeper)
    if is_kafka_kraft; then
        log_info "Kafka est en mode KRaft, Zookeeper n'est pas necessaire"
        return 0
    fi
    
    local kafka_bin=$(find_kafka)
    
    if [ -z "$kafka_bin" ]; then
        log_warning "Kafka n'est pas trouvé."
        log_info "Pour installer Kafka:"
        log_info "   macOS: brew install kafka"
        log_info "   Linux: wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz"
        log_info "   Ou definissez KAFKA_HOME=/chemin/vers/kafka"
        log_info "   Consultez KAFKA_SETUP.md pour plus de details"
        return 1
    fi
    
    # Chercher le fichier de configuration Zookeeper
    local zookeeper_configs=(
        "$kafka_bin/../config/zookeeper.properties"
        "$kafka_bin/../etc/kafka/zookeeper.properties"  # Homebrew libexec
        "/usr/local/etc/kafka/zookeeper.properties"  # Homebrew
        "/opt/homebrew/etc/kafka/zookeeper.properties"  # Homebrew Apple Silicon
        "$HOME/kafka/config/zookeeper.properties"
        "/usr/local/kafka/config/zookeeper.properties"
        "/opt/kafka/config/zookeeper.properties"
    )
    
    local zookeeper_config=""
    for config in "${zookeeper_configs[@]}"; do
        if [ -f "$config" ]; then
            zookeeper_config="$config"
            break
        fi
    done
    
    if [ -z "$zookeeper_config" ]; then
        log_warning "Fichier de configuration Zookeeper non trouvé"
        log_info "Si Kafka est en mode KRaft (version 4.x+), Zookeeper n'est pas necessaire"
        return 1
    fi
    
    if check_port 2181; then
        log_info "Démarrage de Zookeeper..."
        "$kafka_bin/zookeeper-server-start.sh" "$zookeeper_config" > logs/zookeeper.log 2>&1 &
        ZOOKEEPER_PID=$!
        sleep 3
        log_success "Zookeeper démarré (PID: $ZOOKEEPER_PID)"
    else
        log_warning "Le port 2181 est déjà utilisé. Zookeeper est peut-être déjà démarré."
    fi
}

# Fonction pour démarrer Kafka
start_kafka() {
    local kafka_bin=$(find_kafka)
    
    if [ -z "$kafka_bin" ]; then
        log_warning "Kafka n'est pas trouvé"
        return 1
    fi
    
    # Chercher le fichier de configuration Kafka
    local kafka_configs=(
        "$kafka_bin/../config/server.properties"
        "/usr/local/etc/kafka/server.properties"  # Homebrew
        "/opt/homebrew/etc/kafka/server.properties"  # Homebrew Apple Silicon
        "$HOME/kafka/config/server.properties"
        "/usr/local/kafka/config/server.properties"
        "/opt/kafka/config/server.properties"
    )
    
    local kafka_config=""
    for config in "${kafka_configs[@]}"; do
        if [ -f "$config" ]; then
            kafka_config="$config"
            break
        fi
    done
    
    if [ -z "$kafka_config" ]; then
        log_warning "Fichier de configuration Kafka non trouvé"
        return 1
    fi
    
    if check_port 9092; then
        log_info "Démarrage de Kafka..."
        "$kafka_bin/kafka-server-start.sh" "$kafka_config" > logs/kafka.log 2>&1 &
        KAFKA_PID=$!
        sleep 5
        log_success "Kafka démarré (PID: $KAFKA_PID)"
    else
        log_warning "Le port 9092 est déjà utilisé. Kafka est peut-être déjà démarré."
    fi
}

# Fonction pour démarrer le consumer Kafka
start_kafka_consumer() {
    if [ -z "$KAFKA_PID" ] && ! check_port 9092; then
        log_warning "Kafka ne semble pas être démarré. Démarrage du consumer annulé."
        return 1
    fi
    
    log_info "Démarrage du Kafka Consumer..."
    python integration/kafka_consumer.py > logs/kafka_consumer.log 2>&1 &
    CONSUMER_PID=$!
    sleep 2
    log_success "Kafka Consumer démarré (PID: $CONSUMER_PID)"
}

# Créer le dossier logs s'il n'existe pas
mkdir -p logs

# Service à démarrer
SERVICE=${1:-all}

echo ""
log_info "Demarrage des services..."
echo ""

case $SERVICE in
  rest)
    start_rest
    log_info "Appuyez sur Ctrl+C pour arrêter"
    wait $REST_PID
    ;;
    
  graphql)
    start_graphql
    log_info "Appuyez sur Ctrl+C pour arrêter"
    wait $GRAPHQL_PID
    ;;
    
  prometheus)
    start_prometheus
    log_info "Appuyez sur Ctrl+C pour arrêter"
    wait $PROMETHEUS_PID
    ;;
    
  kafka)
    # Démarrer Zookeeper seulement si nécessaire (pas en mode KRaft)
    if ! is_kafka_kraft; then
        start_zookeeper
        sleep 2
    else
        log_info "Kafka en mode KRaft, Zookeeper non necessaire"
    fi
    start_kafka
    log_info "Appuyez sur Ctrl+C pour arrêter"
    if [ -n "$ZOOKEEPER_PID" ]; then
        wait $ZOOKEEPER_PID $KAFKA_PID
    else
        wait $KAFKA_PID
    fi
    ;;
    
  consumer)
    start_kafka_consumer
    log_info "Appuyez sur Ctrl+C pour arrêter"
    wait $CONSUMER_PID
    ;;
    
  all)
    log_info "Démarrage de tous les services..."
    echo ""
    
    # Démarrer Zookeeper et Kafka en premier (si disponibles)
    # Note: Kafka 4.x+ utilise KRaft et n'a pas besoin de Zookeeper
    if start_zookeeper; then
        # Si Zookeeper est nécessaire (Kafka < 4.0), attendre avant de démarrer Kafka
        if ! is_kafka_kraft; then
            sleep 2
        fi
        start_kafka
        sleep 2
    else
        # Si Zookeeper n'est pas nécessaire (KRaft), démarrer Kafka directement
        if is_kafka_kraft; then
            log_info "Kafka en mode KRaft, demarrage direct sans Zookeeper"
            start_kafka
            sleep 2
        fi
    fi
    
    # Démarrer l'API REST
    start_rest
    sleep 2
    
    # Démarrer GraphQL (dépend de REST)
    start_graphql
    sleep 2
    
    # Démarrer Prometheus (optionnel)
    start_prometheus || true
    sleep 2
    
    # Démarrer le consumer Kafka (optionnel, nécessite Kafka)
    if [ -n "$KAFKA_PID" ] || ! check_port 9092; then
        start_kafka_consumer || true
    fi
    
    echo ""
    log_success "Tous les services sont démarrés !"
    echo ""
    echo "============================================================"
    echo "Services disponibles :"
    echo "============================================================"
    [ -n "$REST_PID" ] && echo "  [OK] API REST:        http://localhost:5000"
    [ -n "$REST_PID" ] && echo "  [OK] Metriques:       http://localhost:5000/metrics"
    [ -n "$GRAPHQL_PID" ] && echo "  [OK] GraphQL:         http://localhost:8000/graphql"
    [ -n "$PROMETHEUS_PID" ] && echo "  [OK] Prometheus:      http://localhost:9090"
    [ -n "$ZOOKEEPER_PID" ] && echo "  [OK] Zookeeper:       http://localhost:2181"
    [ -n "$KAFKA_PID" ] && echo "  [OK] Kafka:           http://localhost:9092"
    [ -n "$CONSUMER_PID" ] && echo "  [OK] Kafka Consumer:  En cours d'execution"
    echo "============================================================"
    echo ""
    log_info "Appuyez sur Ctrl+C pour arrêter tous les services"
    echo ""
    
    # Attendre indéfiniment jusqu'à interruption
    wait
    ;;
    
  *)
    echo "Usage: $0 [rest|graphql|prometheus|kafka|consumer|all]"
    echo ""
    echo "Options:"
    echo "  rest        - Démarrer uniquement l'API REST Flask"
    echo "  graphql     - Démarrer uniquement le serveur GraphQL"
    echo "  prometheus  - Démarrer uniquement Prometheus"
    echo "  kafka       - Démarrer Zookeeper et Kafka"
    echo "  consumer    - Démarrer le Kafka Consumer"
    echo "  all         - Démarrer tous les services (défaut)"
    exit 1
    ;;
esac
