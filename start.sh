#!/bin/bash

# Script de démarrage automatique - OpenSky Flight Tracker
# Lance les 3 composants : Producer, Spark Consumer, Dashboard

# Configurer Java 17 pour Spark
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================"
echo -e "  OpenSky Flight Tracker - Dubai (DXB)"
echo -e "======================================${NC}"
echo ""

# Activer l'environnement virtuel
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activation de l'environnement virtuel...${NC}"
    source venv/bin/activate
    echo -e "${GREEN}✓ Environnement activé${NC}"
else
    echo -e "${RED}✗ Environnement virtuel introuvable${NC}"
    echo -e "${YELLOW}Créez-le avec: python3 -m venv venv && pip install -r requirements.txt${NC}"
    exit 1
fi

# Vérifier Kafka
echo -e "${YELLOW}Vérification de Kafka...${NC}"
if ! nc -z localhost 9092 2>/dev/null; then
    echo -e "${RED}✗ Kafka n'est pas accessible${NC}"
    echo -e "${YELLOW}Lancement de Kafka avec Docker...${NC}"
    docker-compose up -d
    echo -e "${YELLOW}Attente de Kafka (15s)...${NC}"
    sleep 15
fi

if nc -z localhost 9092 2>/dev/null; then
    echo -e "${GREEN}✓ Kafka est accessible${NC}"
else
    echo -e "${RED}✗ Impossible de démarrer Kafka${NC}"
    exit 1
fi

echo ""

# Fonction de nettoyage
cleanup() {
    echo ""
    echo -e "${YELLOW}Arrêt des processus...${NC}"
    kill $PRODUCER_PID 2>/dev/null
    kill $SPARK_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    echo -e "${GREEN}✓ Tous les processus sont arrêtés${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Démarrer le Producer Kafka
echo -e "${YELLOW}[1/3] Démarrage du Kafka Producer...${NC}"
./venv/bin/python kafka_producer.py > /tmp/producer.log 2>&1 &
PRODUCER_PID=$!
sleep 3

if ps -p $PRODUCER_PID > /dev/null; then
    echo -e "${GREEN}✓ Producer démarré (PID: $PRODUCER_PID)${NC}"
else
    echo -e "${RED}✗ Erreur Producer${NC}"
    cat /tmp/producer.log
    exit 1
fi

# 2. Démarrer Spark Consumer (avec Java 17 via wrapper)
echo -e "${YELLOW}[2/3] Démarrage de Spark Consumer...${NC}"
bash run_spark.sh > /tmp/spark.log 2>&1 &
SPARK_PID=$!
sleep 8

if ps -p $SPARK_PID > /dev/null; then
    echo -e "${GREEN}✓ Spark Consumer démarré (PID: $SPARK_PID)${NC}"
else
    echo -e "${RED}✗ Erreur Spark${NC}"
    cat /tmp/spark.log
    kill $PRODUCER_PID
    exit 1
fi

# 3. Démarrer Dashboard Streamlit
echo -e "${YELLOW}[3/3] Démarrage du Dashboard Streamlit...${NC}"
./venv/bin/python -m streamlit run dashboard.py > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!
sleep 3

if ps -p $STREAMLIT_PID > /dev/null; then
    echo -e "${GREEN}✓ Dashboard démarré (PID: $STREAMLIT_PID)${NC}"
else
    echo -e "${RED}✗ Erreur Dashboard${NC}"
    cat /tmp/streamlit.log
    kill $PRODUCER_PID $SPARK_PID
    exit 1
fi

echo ""
echo -e "${GREEN}======================================"
echo -e "  ✓ Tous les composants sont démarrés"
echo -e "======================================${NC}"
echo ""
echo -e "Informations :"
echo -e "  - Producer PID    : $PRODUCER_PID"
echo -e "  - Spark PID       : $SPARK_PID"
echo -e "  - Streamlit PID   : $STREAMLIT_PID"
echo ""
echo -e "Logs disponibles dans /tmp/"
echo ""
echo -e "${BLUE}Dashboard : http://localhost:8501${NC}"
echo -e "${BLUE}Kafka UI  : http://localhost:8080${NC}"
echo ""
echo -e "Appuyez sur ${YELLOW}Ctrl+C${NC} pour arrêter tous les composants"
echo ""

# Attendre
wait
