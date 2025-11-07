#!/bin/bash

# Script de test du déploiement Docker
# Teste que tous les services fonctionnent correctement

echo "🧪 Test du déploiement OpenSky Flight Tracker"
echo "=============================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Fonction de test
test_service() {
    local service=$1
    local description=$2
    
    if docker-compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✓${NC} $description"
        return 0
    else
        echo -e "${RED}✗${NC} $description"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

test_url() {
    local url=$1
    local description=$2
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|302"; then
        echo -e "${GREEN}✓${NC} $description accessible"
        return 0
    else
        echo -e "${RED}✗${NC} $description inaccessible"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

echo "1. Test des conteneurs Docker"
echo "------------------------------"
test_service "opensky-zookeeper" "Zookeeper"
test_service "opensky-kafka" "Kafka"
test_service "opensky-kafka-ui" "Kafka UI"
test_service "opensky-producer" "Producer"
test_service "opensky-spark" "Spark Consumer"
test_service "opensky-dashboard" "Dashboard"

echo ""
echo "2. Test des URLs"
echo "----------------"
sleep 5  # Attendre que les services démarrent
test_url "http://localhost:8501" "Dashboard Streamlit"
test_url "http://localhost:8080" "Kafka UI"

echo ""
echo "3. Test des données"
echo "-------------------"

# Vérifier les logs du producer
if docker-compose logs producer 2>/dev/null | grep -q "Vol envoyé"; then
    echo -e "${GREEN}✓${NC} Producer envoie des données"
else
    echo -e "${YELLOW}⚠${NC} Aucune donnée envoyée par le producer (peut prendre quelques minutes)"
fi

# Vérifier les logs de Spark
if docker-compose logs spark-consumer 2>/dev/null | grep -q "Streaming démarré"; then
    echo -e "${GREEN}✓${NC} Spark Consumer traite les données"
else
    echo -e "${RED}✗${NC} Spark Consumer ne traite pas les données"
    ERRORS=$((ERRORS + 1))
fi

# Vérifier les fichiers Parquet
PARQUET_COUNT=$(docker-compose exec -T dashboard ls /data/flights_data/*.parquet 2>/dev/null | wc -l)
if [ "$PARQUET_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓${NC} Fichiers Parquet créés ($PARQUET_COUNT fichiers)"
else
    echo -e "${YELLOW}⚠${NC} Aucun fichier Parquet (peut prendre quelques minutes)"
fi

echo ""
echo "4. Résumé"
echo "---------"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ Tous les tests sont passés !${NC}"
    echo ""
    echo "📊 Dashboard : http://localhost:8501"
    echo "🔍 Kafka UI  : http://localhost:8080"
    exit 0
else
    echo -e "${RED}✗ $ERRORS test(s) échoué(s)${NC}"
    echo ""
    echo "Voir les logs avec : docker-compose logs"
    exit 1
fi
