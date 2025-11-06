#!/bin/bash

# Script de nettoyage de l'ancienne structure
# ⚠️  ATTENTION : Ce script supprime les anciens dossiers !

BLUE='\033[0;34m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Migration vers nouvelle structure simplifiée     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Aller dans le dossier parent
cd "$(dirname "$0")/.."

echo -e "${YELLOW}📁 Dossiers à supprimer :${NC}"
echo "  - kafka/"
echo "  - spark/"
echo "  - streamlit_app/"
echo "  - data/"
echo "  - logs/"
echo "  - docs/"
echo "  - run_spark.sh"
echo "  - start.sh (ancien)"
echo ""

read -p "❓ Confirmer la suppression ? (oui/non) : " confirm

if [ "$confirm" != "oui" ]; then
    echo -e "${RED}✗ Annulé${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}🗑️  Suppression en cours...${NC}"

# Sauvegarder d'abord (par sécurité)
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}💾 Création d'une sauvegarde : $BACKUP_DIR/${NC}"
mkdir -p "$BACKUP_DIR"

# Copier avant de supprimer
[ -d kafka ] && cp -r kafka "$BACKUP_DIR/"
[ -d spark ] && cp -r spark "$BACKUP_DIR/"
[ -d streamlit_app ] && cp -r streamlit_app "$BACKUP_DIR/"
[ -d data ] && cp -r data "$BACKUP_DIR/"
[ -d logs ] && cp -r logs "$BACKUP_DIR/"
[ -d docs ] && cp -r docs "$BACKUP_DIR/"

echo -e "${GREEN}✓ Sauvegarde créée${NC}"

# Supprimer les anciens dossiers
echo -e "${YELLOW}🗑️  Suppression des anciens dossiers...${NC}"

rm -rf kafka/
rm -rf spark/
rm -rf streamlit_app/
rm -rf data/
rm -rf logs/
rm -rf docs/
rm -f run_spark.sh
rm -f start.sh

echo -e "${GREEN}✓ Suppression terminée${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Migration terminée !${NC}"
echo ""
echo -e "📁 Nouvelle structure dans : ${BLUE}opensky-flight-tracker/${NC}"
echo -e "💾 Sauvegarde dans : ${YELLOW}$BACKUP_DIR/${NC}"
echo ""
echo -e "${BLUE}🚀 Pour démarrer :${NC}"
echo -e "   cd opensky-flight-tracker"
echo -e "   source venv/bin/activate"
echo -e "   ./start.sh"
echo ""
