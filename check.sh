#!/bin/bash

# Script de vérification de l'installation
# Vérifie que tous les prérequis sont installés

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Vérification de l'installation${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

ERRORS=0

# Vérifier Python
echo -n "Python 3.8+    : "
if command -v python3 &> /dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ $VERSION${NC}"
else
    echo -e "${RED}✗ Non installé${NC}"
    ((ERRORS++))
fi

# Vérifier pip
echo -n "pip            : "
if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ Installé${NC}"
else
    echo -e "${RED}✗ Non installé${NC}"
    ((ERRORS++))
fi

# Vérifier Java
echo -n "Java 17        : "
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    if [[ $JAVA_VERSION == 17* ]]; then
        echo -e "${GREEN}✓ $JAVA_VERSION${NC}"
    else
        echo -e "${YELLOW}⚠ Version $JAVA_VERSION (recommandé: 17.x)${NC}"
    fi
else
    echo -e "${RED}✗ Non installé${NC}"
    ((ERRORS++))
fi

# Vérifier Docker
echo -n "Docker         : "
if command -v docker &> /dev/null; then
    VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo -e "${GREEN}✓ $VERSION${NC}"
else
    echo -e "${RED}✗ Non installé${NC}"
    ((ERRORS++))
fi

# Vérifier Docker Compose
echo -n "Docker Compose : "
if command -v docker-compose &> /dev/null; then
    VERSION=$(docker-compose --version | cut -d' ' -f4 | tr -d ',')
    echo -e "${GREEN}✓ $VERSION${NC}"
else
    echo -e "${RED}✗ Non installé${NC}"
    ((ERRORS++))
fi

# Vérifier environnement virtuel
echo -n "venv/          : "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Créé${NC}"
else
    echo -e "${YELLOW}⚠ Pas encore créé${NC}"
fi

# Vérifier dépendances Python
echo -n "Dependencies   : "
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate 2>/dev/null
    if python -c "import kafka, pyspark, streamlit" 2>/dev/null; then
        echo -e "${GREEN}✓ Installées${NC}"
    else
        echo -e "${YELLOW}⚠ À installer (pip install -r requirements.txt)${NC}"
    fi
    deactivate 2>/dev/null
else
    echo -e "${YELLOW}⚠ Venv non créé${NC}"
fi

# Vérifier Kafka
echo -n "Kafka          : "
if docker ps | grep -q kafka; then
    echo -e "${GREEN}✓ En cours d'exécution${NC}"
elif nc -z localhost 9092 2>/dev/null; then
    echo -e "${GREEN}✓ Accessible${NC}"
else
    echo -e "${YELLOW}⚠ Non démarré (docker-compose up -d)${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Tous les prérequis sont installés !${NC}"
    echo ""
    echo -e "${BLUE}Prochaines étapes :${NC}"
    echo "  1. source venv/bin/activate"
    echo "  2. pip install -r requirements.txt  (si pas encore fait)"
    echo "  3. docker-compose up -d"
    echo "  4. ./start.sh"
else
    echo -e "${RED}❌ $ERRORS prérequis manquants${NC}"
    echo ""
    echo -e "${YELLOW}Consultez QUICKSTART.md pour les instructions d'installation${NC}"
fi

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
