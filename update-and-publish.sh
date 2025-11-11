#!/bin/bash
# Script pour mettre à jour les images Docker Hub avec les dernières modifications

set -e  # Arrêter en cas d'erreur

echo "🔄 Mise à jour et publication des images Docker Hub"
echo "===================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOCKER_USERNAME="zbelem001"

echo -e "${YELLOW}[1/5] Vérification de l'état Git...${NC}"
git status --short
echo ""

echo -e "${YELLOW}[2/5] Commit des modifications...${NC}"
read -p "Message de commit (ou Enter pour 'Update Docker images with cleanup fix'): " commit_msg
commit_msg=${commit_msg:-"Update Docker images with cleanup fix"}

git add .
git commit -m "$commit_msg" || echo "Rien à commiter"
echo -e "${GREEN}✓ Modifications committées${NC}"
echo ""

echo -e "${YELLOW}[3/5] Push vers GitHub...${NC}"
git push origin main
echo -e "${GREEN}✓ Poussé vers GitHub${NC}"
echo ""

echo -e "${YELLOW}[4/5] Reconstruction des images Docker...${NC}"
echo "⏳ Cela peut prendre 5-10 minutes..."
echo ""

echo "  → Building producer..."
sudo docker-compose build producer

echo "  → Building spark-consumer..."
sudo docker-compose build spark-consumer

echo "  → Building dashboard..."
sudo docker-compose build dashboard

echo -e "${GREEN}✓ Images reconstruites${NC}"
echo ""

echo -e "${YELLOW}[5/5] Publication sur Docker Hub...${NC}"
echo "⏳ Cela peut prendre quelques minutes..."
echo ""

# Vérifier la connexion Docker Hub
if ! sudo docker info | grep -q "Username"; then
    echo -e "${RED}❌ Vous n'êtes pas connecté à Docker Hub${NC}"
    echo "Connectez-vous avec : sudo docker login"
    exit 1
fi

# Tagger et pusher les images
echo "  → Tagging et pushing producer..."
sudo docker tag opensky-flight-tracker_producer ${DOCKER_USERNAME}/opensky-producer:latest
sudo docker push ${DOCKER_USERNAME}/opensky-producer:latest

echo "  → Tagging et pushing spark-consumer..."
sudo docker tag opensky-flight-tracker_spark-consumer ${DOCKER_USERNAME}/opensky-spark:latest
sudo docker push ${DOCKER_USERNAME}/opensky-spark:latest

echo "  → Tagging et pushing dashboard..."
sudo docker tag opensky-flight-tracker_dashboard ${DOCKER_USERNAME}/opensky-dashboard:latest
sudo docker push ${DOCKER_USERNAME}/opensky-dashboard:latest

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ SUCCÈS ! Images mises à jour${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "📋 Images publiées :"
echo "  • ${DOCKER_USERNAME}/opensky-producer:latest"
echo "  • ${DOCKER_USERNAME}/opensky-spark:latest"
echo "  • ${DOCKER_USERNAME}/opensky-dashboard:latest"
echo ""
echo "🔗 Docker Hub : https://hub.docker.com/u/${DOCKER_USERNAME}"
echo ""
echo -e "${BLUE}💡 Maintenant votre prof pourra lancer :${NC}"
echo -e "   ${BLUE}docker-compose -f docker-compose.hub.yml pull${NC}  # Pour télécharger les nouvelles images"
echo -e "   ${BLUE}docker-compose -f docker-compose.hub.yml up -d${NC}  # Pour démarrer"
echo ""
