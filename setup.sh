#!/bin/bash

# Script de configuration de l'environnement virtuel
# Crée et configure l'environnement virtuel Python pour le projet

set -e  # Arrêter en cas d'erreur

echo "Configuration de l'environnement virtuel Python"
echo "================================================"
echo ""

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 n'est pas installe. Veuillez l'installer d'abord."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "[OK] Python detecte: $PYTHON_VERSION"
echo ""

# Nom de l'environnement virtuel
VENV_NAME="venv"

# Vérifier si l'environnement virtuel existe déjà
if [ -d "$VENV_NAME" ]; then
    echo "[WARN] L'environnement virtuel '$VENV_NAME' existe deja."
    read -p "Voulez-vous le recréer ? (o/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        echo "Suppression de l'ancien environnement virtuel..."
        rm -rf "$VENV_NAME"
    else
        echo "[INFO] Utilisation de l'environnement virtuel existant."
        echo ""
        echo "[OK] Pour activer l'environnement virtuel, executez :"
        echo "   source $VENV_NAME/bin/activate"
        exit 0
    fi
fi

# Créer l'environnement virtuel
echo "Creation de l'environnement virtuel '$VENV_NAME'..."
python3 -m venv "$VENV_NAME"

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source "$VENV_NAME/bin/activate"

# Mettre à jour pip
echo "Mise a jour de pip..."
pip install --upgrade pip

# Installer les dépendances
echo "Installation des dependances depuis requirements.txt..."
pip install -r requirements.txt

echo ""
echo "[OK] Configuration terminee avec succes !"
echo ""
echo "Pour activer l'environnement virtuel, executez :"
echo "   source $VENV_NAME/bin/activate"
echo ""
echo "Pour desactiver l'environnement virtuel, executez :"
echo "   deactivate"
echo ""
echo "Pour demarrer les services, executez :"
echo "   python app.py          # API REST"
echo "   python graphql_server.py  # Serveur GraphQL"
echo ""

