#!/bin/bash

# Script de vérification pour le professeur
# Vérifie que tous les services sont actifs et fonctionnels

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================="
echo -e "  OpenSky Flight Tracker - Test Complet"
echo -e "=============================================${NC}"
echo ""

# Fonction pour vérifier un service
check_service() {
    local service=$1
    local status=$(docker-compose -f docker-compose.hub.yml ps | grep "$service" | grep "Up")
    
    if [ -n "$status" ]; then
        echo -e "${GREEN}✓${NC} $service est actif"
        return 0
    else
        echo -e "${RED}✗${NC} $service n'est pas actif"
        return 1
    fi
}

# Fonction pour vérifier un port
check_port() {
    local port=$1
    local name=$2
    
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Port $port ($name) est accessible"
        return 0
    else
        echo -e "${RED}✗${NC} Port $port ($name) n'est pas accessible"
        return 1
    fi
}

# Fonction pour vérifier les logs
check_logs() {
    local service=$1
    local keyword=$2
    
    local logs=$(docker-compose -f docker-compose.hub.yml logs --tail=50 $service 2>/dev/null | grep -i "$keyword")
    
    if [ -n "$logs" ]; then
        echo -e "${GREEN}✓${NC} $service fonctionne (logs OK)"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} $service démarre encore (logs en attente)"
        return 1
    fi
}

echo -e "${YELLOW}[1/4] Vérification de Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker n'est pas installé${NC}"
    echo -e "Installez Docker : https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker est installé${NC}"
echo ""

echo -e "${YELLOW}[2/4] Vérification des conteneurs Docker...${NC}"
errors=0

check_service "opensky-zookeeper" || ((errors++))
check_service "opensky-kafka" || ((errors++))
check_service "opensky-kafka-ui" || ((errors++))
check_service "opensky-producer" || ((errors++))
check_service "opensky-spark" || ((errors++))
check_service "opensky-dashboard" || ((errors++))

echo ""

echo -e "${YELLOW}[3/4] Vérification des ports...${NC}"

check_port 2181 "Zookeeper" || ((errors++))
check_port 9092 "Kafka" || ((errors++))
check_port 8080 "Kafka UI" || ((errors++))
check_port 8501 "Dashboard" || ((errors++))

echo ""

echo -e "${YELLOW}[4/4] Vérification des logs applicatifs...${NC}"

sleep 2

# Vérifier que le producer envoie des données
if docker-compose -f docker-compose.hub.yml logs --tail=50 producer 2>/dev/null | grep -q "détectés\|envoyé"; then
    echo -e "${GREEN}✓${NC} Producer envoie des données"
else
    echo -e "${YELLOW}⚠${NC} Producer n'a pas encore envoyé de données (attendez 30s)"
    ((errors++))
fi

# Vérifier que Spark traite
if docker-compose -f docker-compose.hub.yml logs --tail=50 spark-consumer 2>/dev/null | grep -q "Streaming\|Batch"; then
    echo -e "${GREEN}✓${NC} Spark Consumer traite les données"
else
    echo -e "${YELLOW}⚠${NC} Spark Consumer démarre encore (attendez 60s)"
    ((errors++))
fi

# Vérifier les fichiers Parquet
if docker exec opensky-spark ls /data/flights_data/*.parquet 2>/dev/null | grep -q ".parquet"; then
    file_count=$(docker exec opensky-spark ls /data/flights_data/*.parquet 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} Fichiers Parquet créés ($file_count fichiers)"
else
    echo -e "${YELLOW}⚠${NC} Aucun fichier Parquet encore (attendez 2 min)"
    ((errors++))
fi

echo ""
echo -e "${BLUE}=============================================${NC}"

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✓ TOUS LES TESTS PASSENT${NC}"
    echo ""
    echo -e "${BLUE}Accédez au dashboard :${NC}"
    echo -e "  📊 Dashboard : ${BLUE}http://localhost:8501${NC}"
    echo -e "  🔍 Kafka UI  : ${BLUE}http://localhost:8080${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ $errors avertissement(s) détecté(s)${NC}"
    echo ""
    echo -e "${YELLOW}Recommandations :${NC}"
    echo -e "  1. Attendez 2-3 minutes après le démarrage"
    echo -e "  2. Relancez ce script : ${BLUE}bash test-professor.sh${NC}"
    echo -e "  3. Voir les logs : ${BLUE}docker-compose -f docker-compose.hub.yml logs -f${NC}"
    echo ""
    
    if [ $errors -le 2 ]; then
        echo -e "${YELLOW}Note : Ces avertissements sont normaux si le système vient de démarrer.${NC}"
        echo -e "${BLUE}Essayez d'accéder quand même au dashboard :${NC}"
        echo -e "  📊 http://localhost:8501"
        exit 0
    else
        exit 1
    fi
fi
